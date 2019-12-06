"""
App views: Autoconfigure mail, M$-style.
"""
from flask import Response

from automx2.generators.outlook import OutlookGenerator
from automx2.views import BaseView


class MailConfig(BaseView):
    def config_response(self, local_part, domain_part: str) -> Response:
        data = OutlookGenerator().client_config(local_part, domain_part)
        return data
