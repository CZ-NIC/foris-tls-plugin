%# Foris - web administration interface for OpenWrt based on NETCONF
%# Copyright (C) 2015 CZ.NIC, z. s. p. o. <https://www.nic.cz>
%#
%# Foris is distributed under the terms of GNU General Public License v3.
%# You should have received a copy of the GNU General Public License
%# along with this program.  If not, see <https://www.gnu.org/licenses/>.

%rebase("config/base.tpl", **locals())

<div id="page-plugin-tls" class="config-page">
  %include("_messages.tpl")

  <p>
    {{ trans("This page serves for management of remote access to the router's configuration backend using TLS API. You can use generated client tokens for authentication in third-party applications that implement this API.") }}
  </p>
  <p>
    {{ trans("Please be aware that these tokens allow access to the whole configuration of the router, which may be exploited by a malicious user who has access to them.") }}
  </p>

  %if ca.generating:
    <div class="message warning">
      {{ trans("New certification authority is being generated. Please try coming back later.") }}
    </div>
  %else:
    <form action="{{ url("config_action", page_name="tls", action="get-token") }}" method="post">
      <input type="hidden" name="csrf_token" value="{{ get_csrf_token() }}">

      %if ca.clients:
        <h2>{{ trans("List of clients") }}</h2>

        <table class="tls-ca">
          <thead>
            <tr>
              <th>{{ trans("Client") }}</th>
              <th>{{ trans("Status") }}</th>
              <th>{{ trans("Get token") }}</th>
            </tr>
          </thead>
          <tbody>
          %for client in ca.clients.itervalues():
            <tr>
              <td>{{ client['name'] }}</td>
              <td>{{ trans(client['status']) }}</td>
              <td><button name="name" value="{{ client['name'] }}" type="submit">{{ trans("Get token") }}</button></td>
            </tr>
          %end
          </tbody>
        </table>
      %end
    </form>

    <h2>{{ trans("New client") }}</h2>

    <form action="{{ url("config_page", page_name="tls") }}" method="post" class="config-form">
      <input type="hidden" name="csrf_token" value="{{ get_csrf_token() }}">
      %for field in form.active_fields:
          %include("_field.tpl", field=field)
      %end
      <button type="submit" name="send">{{ trans("Create") }}</button>
    </form>

    <h2>{{ trans("Revoke access") }}</h2>

    <p>
      {{ trans("It is not possible to revoke access to individual clients, but you can reset the whole certification authority (CA) and disable access for all the clients. Creating a new authority takes some time. This action is irreversible.") }}
    </p>

    <form action="{{ url("config_action", page_name="tls", action="reset-ca") }}" method="post" id="reset-ca-form">
      <input type="hidden" name="csrf_token" value="{{ get_csrf_token() }}">
      <button type="submit" name="send" id="reset-ca-submit">{{ trans("Reset CA") }}</button>
    </form>
  %end

  <script>
    $(document).on("click", "#reset-ca-submit", function () {
      return confirm("{{ trans("Do you really want to reset the CA and revoke access for all the clients? This can not be undone!") }}");
    });
  </script>
</div>
