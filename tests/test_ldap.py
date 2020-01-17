"""
Copyright © 2019-2020 Ralph Seichter

Graciously sponsored by sys4 AG <https://sys4.de/>

This file is part of automx2.

automx2 is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

automx2 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with automx2. If not, see <https://www.gnu.org/licenses/>.
"""
import unittest

from automx2.generators.apple import AppleGenerator
from automx2.generators.mozilla import MozillaGenerator
from automx2.generators.outlook import OutlookGenerator
from automx2.ldap import LdapAccess
from automx2.ldap import LookupResult
from automx2.ldap import STATUS_ERROR
from automx2.ldap import STATUS_NO_MATCH
from automx2.ldap import STATUS_SUCCESS
from automx2.model import Ldapserver
from automx2.util import unique
from tests.base import LDAP_BIND_PASSWORD
from tests.base import LDAP_BIND_USER
from tests.base import LDAP_HOSTNAME
from tests.base import LDAP_PORT
from tests.base import LDAP_SEARCH_BASE
from tests.base import TestCase
from tests.base import app


class LdapTests(TestCase):
    """Tests for LDAP access methods."""
    EXISTS_LOCAL = 'a'
    EXISTS_DOMAIN = 'example.com'
    EXISTS_EMAIL = f'{EXISTS_LOCAL}@{EXISTS_DOMAIN}'
    EXISTS_CN = 'John Doe'
    EXISTS_UID = 'jd'
    UNIQUE = unique()
    ATTRIBUTES = {'attributes': {'x': [UNIQUE]}}

    @staticmethod
    def search_filter(email_address):
        return f'(mail={email_address})'

    def setUp(self) -> None:
        super().setUp()
        self.ldap = LdapAccess(hostname=LDAP_HOSTNAME, user=LDAP_BIND_USER, password=LDAP_BIND_PASSWORD, use_ssl=True)

    def test_attribute_exists(self):
        self.assertEqual(self.UNIQUE, self.ldap.get_attribute(self.ATTRIBUTES, 'x'))

    def test_attribute_missing(self):
        self.assertIsNone(self.ldap.get_attribute(self.ATTRIBUTES, 'y'))

    @unittest.skip  # Avoid triggering fail2ban
    def test_bind_failed(self):
        self.ldap = LdapAccess(hostname=LDAP_HOSTNAME, user=LDAP_BIND_USER, password=self.UNIQUE)
        x: LookupResult = self.ldap.lookup(LDAP_SEARCH_BASE, self.search_filter(self.EXISTS_EMAIL))
        self.assertEqual(STATUS_ERROR, x.status)

    def test_does_not_exist(self):
        x: LookupResult = self.ldap.lookup(LDAP_SEARCH_BASE, self.search_filter(self.UNIQUE))
        self.assertEqual(STATUS_NO_MATCH, x.status)

    def test_exists(self):
        x: LookupResult = self.ldap.lookup(LDAP_SEARCH_BASE, self.search_filter(self.EXISTS_EMAIL), attr_cn='cn')
        self.assertEqual(STATUS_SUCCESS, x.status)
        self.assertEqual(self.EXISTS_CN, x.cn)
        self.assertEqual(self.EXISTS_UID, x.uid)

    def test_apple_generator_ldap(self):
        with app.app_context():
            gen = AppleGenerator()
            gen.client_config(self.EXISTS_LOCAL, self.EXISTS_DOMAIN, '', '')

    def test_outlook_generator_ldap(self):
        with app.app_context():
            gen = OutlookGenerator()
            gen.client_config(self.EXISTS_LOCAL, self.EXISTS_DOMAIN, '', '')

    def test_mozilla_generator_ldap(self):
        with app.app_context():
            server = Ldapserver.query.filter_by(id=LDAP_PORT).one()
            gen = MozillaGenerator()
            x = gen._ldap_lookup(self.EXISTS_EMAIL, server)
            self.assertEqual(STATUS_SUCCESS, x.status)
            y = gen._ldap_lookup(self.UNIQUE, server)
            self.assertEqual(STATUS_NO_MATCH, y.status)


if __name__ == '__main__':
    unittest.main()
