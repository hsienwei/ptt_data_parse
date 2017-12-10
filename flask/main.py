from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

CHANNEL_ACCESS_TOKEN=oBlvlvsfd+tWd8VUxBsNNglNSYK1I05NOvVlzxXuqQbMHL8iSotDdLmU3jRRDNDKiwRbSlbrLCN23Rg45MRgv1HUznh6UdGJ4qoKWnonmOgnJcqXc9qIRjTD5dl5S9Ob8+3Hb1rP+g59dn560AcsWwdB04t89/1O/w1cDnyilFU=
CHANNEL_SECRET=299d53f4c5300cf107fe39d239104eb0

@app.route("/callback", methods=['POST'])
def callback():
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
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


if __name__ == "__main__":
    app.run()