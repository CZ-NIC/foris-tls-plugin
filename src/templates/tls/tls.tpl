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
              <td>
                <button name="name" value="{{ client['name'] }}" type="submit">{{ trans("Download token") }}</button>
                <button class="get-qr" name="qrcode" value="{{ client['name'] }}" type="submit">{{ trans("Get QR code") }}</button>
              </td>
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

  %# jquery.qrcode is part of the JS libraries included in Foris itself
  <script src="{{ static("js/contrib/jquery.qrcode-0.7.0.min.js") }}"></script>
  <script>
    $(document).on("click", "#reset-ca-submit", function () {
      return confirm("{{ trans("Do you really want to reset the CA and revoke access for all the clients? This can not be undone!") }}");
    });

    $(document).on('click', '.get-qr', function(e) {
      e.preventDefault();
      var $this = $(this),
          $form = $this.parents('form:first'),
          formData = $form.serializeArray(),
          clientName = $this.attr('value');

      $this.attr('disabled', 'disabled');
      formData.push({name: $this.attr('name'), value: clientName});

      $.post($form.attr('action'), formData)
          .done(function (qrData) {
            $("#page-plugin-tls")
                .append('<div class="token-modal"><div class="token-modal-content">' +
                    '<span class="close">&times;</span>' +
                    '<div id="token-qrcode" />' +
                    '<p>' + '{{ trans("Access token for client") }} ' +
                    '<strong>' + clientName + '</strong>.<br>' +
                    '{{ trans ("Token will be automatically invalidated in") }} ' +
                    '<span id="token-timeout">?</span> s.' +
                    '</p></div></div>');

            var $tokenTimeoutValue = $('#token-timeout');

            function updateTokenTimeout() {
              var remainingTime = qrData.expires_at - (Date.now() / 1000);
              $tokenTimeoutValue.text(Math.floor(remainingTime));
            }

            updateTokenTimeout();

            function removeModal() {
              $('.token-modal').remove();
            }

            $(window).on('click', function (e) {
              if(e.target.className == 'token-modal' || e.target.className == 'close') {
                removeModal();
              }
            });

            var removeModalInterval = window.setInterval(function () {
              if ((Date.now() / 1000) > qrData.expires_at) {
                removeModal();
                window.clearTimeout(removeModalInterval);
              } else {
                updateTokenTimeout();
              }
            }, 1000);

            var turrisURI = "turris://" + qrData.host + qrData.path + '?scheme=' + qrData.scheme
                + '&hostname=' + qrData.hostname + '&board_name=' + qrData.board_name;


            $("#token-qrcode").qrcode({
              size: 200,
              text: turrisURI
            });

          })
          .fail(function () {
            window.alert('{{ trans("Unable to get token. Please try refreshing the page and try again.") }}')
          })
          .always(function () {
            $this.removeAttr('disabled');
          });
    });
  </script>
</div>
