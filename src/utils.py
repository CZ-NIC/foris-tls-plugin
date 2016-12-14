# Foris - web administration interface for OpenWrt based on NETCONF
# Copyright (C) 2016 CZ.NIC, z. s. p. o. <https://www.nic.cz>
#
# Foris is distributed under the terms of GNU General Public License v3.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


def get_system_uptime():
    """Get system uptime in seconds from /proc/uptime.

    :return: system uptime as float number
    """

    with open('/proc/uptime', 'r') as f:
        uptime = float(f.read().split(" ")[0])
    return uptime
