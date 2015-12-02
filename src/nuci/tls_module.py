# Foris - web administration interface for OpenWrt based on NETCONF
# Copyright (C) 2015 CZ.NIC, z. s. p. o. <https://www.nic.cz>
#
# Foris is distributed under the terms of GNU General Public License v3.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import re
from xml.etree import cElementTree as ET

from foris.core import gettext_dummy as _
from foris.nuci.modules.base import YinElement

client_name_regexp = r'[a-zA-Z0-9_.-]+'
re_client_name = re.compile(client_name_regexp)


class NuciTLS(YinElement):
    tag = "nuci-tls"
    NS_URI = "http://www.nic.cz/ns/router/nuci-tls"

    CLIENT_STATUS_ACTIVE = _("active")
    CLIENT_STATUS_REVOKED = _("revoked")
    CLIENT_STATUS_EXPIRED = _("expired")

    def __init__(self, clients, generating):
        super(NuciTLS, self).__init__()
        self.clients = clients
        self.generating = generating

    @staticmethod
    def from_element(element):
        generating = element.find(NuciTLS.qual_tag("generating")) is not None
        client_elements = element.findall(NuciTLS.qual_tag("client"))
        clients = {}
        for client_el in client_elements:
            name = client_el.find(NuciTLS.qual_tag("name")).text
            status = client_el.find(NuciTLS.qual_tag("status")).text
            clients[name] = {'name': name, 'status': status}
        return NuciTLS(clients, generating)

    @property
    def key(self):
        return "nuci-tls"

    @staticmethod
    def rpc_reset_ca(background=True):
        rpc_el = ET.Element(NuciTLS.qual_tag("reset-CA"))
        if background:
            ET.SubElement(rpc_el, NuciTLS.qual_tag("background"))
        return rpc_el

    @staticmethod
    def rpc_new_client(name, background=True):
        rpc_el = ET.Element(NuciTLS.qual_tag("new-client"))
        name_el = ET.SubElement(rpc_el, NuciTLS.qual_tag("name"))
        name_el.text = name
        if background:
            ET.SubElement(rpc_el, NuciTLS.qual_tag("background"))
        return rpc_el

    @staticmethod
    def rpc_revoke_client(name):
        rpc_el = ET.Element(NuciTLS.qual_tag("revoke-client"))
        name_el = ET.SubElement(rpc_el, NuciTLS.qual_tag("name"))
        name_el.text = name
        return rpc_el

    @staticmethod
    def rpc_get_token(name):
        rpc_el = ET.Element(NuciTLS.qual_tag("get-token"))
        name_el = ET.SubElement(rpc_el, NuciTLS.qual_tag("name"))
        name_el.text = name
        return rpc_el

####################################################################################################
ET.register_namespace("nuci-tls", NuciTLS.NS_URI)
