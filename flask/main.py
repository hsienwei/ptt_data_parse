from flask import Flask, request, abort, send_from_directory

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)


CHANNEL_ACCESS_TOKEN = 'oBlvlvsfd+tWd8VUxBsNNglNSYK1I05NOvVlzxXuqQbMHL8iSotDdLmU3jRRDNDKiwRbSlbrLCN23Rg45MRgv1HUznh6UdGJ4qoKWnonmOgnJcqXc9qIRjTD5dl5S9Ob8+3Hb1rP+g59dn560AcsWwdB04t89/1O/w1cDnyilFU='
CHANNEL_SECRET= '299d53f4c5300cf107fe39d239104eb0'

app = Flask(__name__)

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


@app.route('/.well-known/acme-challenge/<path:path>')
def send_js(path):
    return send_from_directory('static', path)

@app.route("/callback", methods=['POST'])
def callback():
    print("b")
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("a")
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))



if __name__ == "__main__":
    #app.run()
    # set OPENSSL_CONF=E:/openssl-0.9.8h-1-bin/share/openssl.cnf
    # openssl genrsa 1024 > ssl.key
    # openssl req -new -x509 -nodes -sha256 -days 365 -key ssl.key > ssl.cert
    # openssl req -nodes -newkey rsa:2048 -keyout myserver.key -out server.csr   
    context = ('server.csr', 'myserver.key')
    app.run(host='34.238.242.30', port=443, ssl_context='AdHoc', threaded=True, debug=True)
    #app.run(host='220.135.224.98', port=80, threaded=True, debug=True)