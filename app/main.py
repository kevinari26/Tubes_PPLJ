import os
from app.db import addUtang, db_drop_and_create_all, getUtang, setup_db
from flask import Flask, request, abort
from flask_cors import CORS
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.route("/tes/reset_db/")
    def reset_db():
        db_drop_and_create_all()
        return 'OK'


    line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))
    handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))


    @app.route("/callback", methods=['POST'])
    def callback():
        signature = request.headers['X-Line-Signature']
        body = request.get_data(as_text=True)
        app.logger.info("Request body: " + body)
        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            abort(400)
        return 'OK'

    @handler.add(MessageEvent, message=TextMessage)
    def handle_text_message(event):
        msg = ""
        # profile = line_bot_api.get_profile(event.source.user_id)
        
        if (event.message.text == "halo"):
            msg = "halo juga"
        else:
            msg = event.message.text

        if (msg.lower().startswith('add ')):
            addUtang(event.source.user_id, msg)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Utang berhasil ditambahkan")
            )
        elif (msg.lower().startswith('total ')):
            utangs = getUtang()
            print(utangs)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=str(utangs))
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=msg)
            )

    @app.route("/tes/getall/")
    def getall():
        x = getUtang()
        for i in x:
            print(i)
        return 'OK' + ' ' + "".join(map(str, x))
    
    @app.route("/tes/add/")
    def addutang():
        x = addUtang(1, "add andy 100")
        return 'OK'

    return app
