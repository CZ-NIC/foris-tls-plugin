# Foris - web administration interface for OpenWrt based on NETCONF
# Copyright (C) 2015 CZ.NIC, z. s. p. o. <https://www.nic.cz>
#
# Foris is distributed under the terms of GNU General Public License v3.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os

import bottle

from foris.core import gettext_dummy as gettext, ugettext as _
from foris.fapi import ForisForm
from foris.form import Textbox
from foris.plugins import ForisPlugin
from foris.config import ConfigPageMixin, add_config_page
from foris.config_handlers import BaseConfigHandler
from foris.utils import messages, reverse
from foris.validators import RegExp, LenRange

from .nuci import get_ca, get_token, ca_filter, new_client, reset_ca
from .nuci.tls_module import client_name_regexp


class TLSConfigHandler(BaseConfigHandler):
    userfriendly_title = gettext("TLS API")  # TODO: something less stupid

    def get_form(self):
        tls_form = ForisForm("tls", self.data, filter=ca_filter)
        maintenance_main = tls_form.add_section(
            name="tls_client", title=_(self.userfriendly_title)
        )
        maintenance_main.add_field(
            Textbox, name="client_name", label=_("Client name"), required=True,
            hint=_("Display name for the client. It must be shorter than 64 characters "
                   "and must contain only alphanumeric characters, dots, dashes and "
                   "underscores."),
            validators=[RegExp(_("Client name is invalid."),
                               client_name_regexp),
                        LenRange(1, 63)]
        )

        def maintenance_form_cb(data):
            client_name = data['client_name']
            if new_client(client_name):
                messages.success(
                    _("Request for creating a new client \"%s\" was succesfully submitted. "
                      "Client token should be available for download in a minute.") % client_name
                )
            else:
                messages.error(_("Error occurred when creating client \"'%s\".") % client_name)
            return "none", None

        tls_form.add_callback(maintenance_form_cb)
        return tls_form


class TLSConfigPage(ConfigPageMixin, TLSConfigHandler):
    template = "tls/tls.tpl"

    def _action_get_token(self):
        """Handle POST requesting download of nuci-tls token

        :return: response with token with appropriate HTTP headers
        """
        client_name = bottle.request.POST.get("name")
        token = get_token(client_name)
        if not token:
            messages.error(_("Unable to get token for user \"%s\".") % client_name)
            bottle.redirect(reverse("config_page", page_name="tls"))

        bottle.response.set_header("Content-Type", "application/x-pem-file")
        bottle.response.set_header("Content-Disposition", 'attachment; filename="%s.pem' % client_name)
        bottle.response.set_header("Content-Length", len(token))
        return token

    def _action_reset_ca(self):
        """Call RPC for resetting the CA and redirect back.

        :return: redirect to plugin's main page
        """
        if reset_ca():
            messages.success(_("Reset of certification authority was successfully submitted."))
        else:
            messages.error(_("Error occurred when trying to reset CA."))

        bottle.redirect(reverse("config_page", page_name="tls"))

    def call_action(self, action):
        if bottle.request.method != 'POST':
            # all actions here require POST
            messages.error("Wrong HTTP method.")
            bottle.redirect(reverse("config_page", page_name="tls"))
        if action == "get-token":
            return self._action_get_token()
        elif action == "reset-ca":
            return self._action_reset_ca()
        raise bottle.HTTPError(404, "Unknown action.")

    def render(self, **kwargs):
        kwargs['ca'] = get_ca()
        kwargs['PLUGIN_NAME'] = TLSPlugin.PLUGIN_NAME
        kwargs['PLUGIN_STATICS'] = TLSPlugin.PLUGIN_STATICS
        return super(TLSConfigPage, self).render(**kwargs)

    def save(self, *args, **kwargs):
        kwargs['no_messages'] = True  # handle messages in methods of TLSConfigPage
        return super(TLSConfigPage, self).save(*args, **kwargs)


class TLSPlugin(ForisPlugin):
    PLUGIN_NAME = "tls"
    DIRNAME = os.path.dirname(os.path.abspath(__file__))
    PLUGIN_STATICS = [
        "css/screen.css",
    ]

    def __init__(self, app):
        super(TLSPlugin, self).__init__(app)
        add_config_page("tls", TLSConfigPage, top_level=True)
