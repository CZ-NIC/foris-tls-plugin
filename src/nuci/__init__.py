# Foris - web administration interface for OpenWrt based on NETCONF
# Copyright (C) 2015 CZ.NIC, z. s. p. o. <https://www.nic.cz>
#
# Foris is distributed under the terms of GNU General Public License v3.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
from xml.etree import cElementTree as ET

from foris.nuci.client import netconf, dispatch
from ncclient.operations import TimeoutExpiredError
from ncclient.operations import RPCError

from . import tls_module as tls


logger = logging.getLogger(__name__)

# filter for NETCONF subtree with CA data
ca_filter = ET.Element(tls.NuciTLS.qual_tag("ca"))


def get_ca():
    data = netconf.get(
        filter=("subtree", ca_filter)
    ).data_ele

    for elem in data.iter():
        if elem.tag == tls.NuciTLS.qual_tag("ca"):
            return tls.NuciTLS.from_element(elem)

    return None


def get_token(name):
    try:
        data = dispatch(tls.NuciTLS.rpc_get_token(name))
        return data.xml
    except (RPCError, TimeoutExpiredError):
        logger.exception("Error when getting TLS token.")
        return None


def new_client(name):
    try:
        dispatch(tls.NuciTLS.rpc_new_client(name))
        return True
    except RPCError:
        logger.exception("Error when creating new client.")
        return False
    except TimeoutExpiredError:
        logger.exception("Timeout expired when creating new client.")
        return False


def reset_ca():
    try:
        dispatch(tls.NuciTLS.rpc_reset_ca())
        return True
    except (RPCError, TimeoutExpiredError):
        logger.exception("Error when getting TLS token.")
        return False
