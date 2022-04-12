'''
akses db: http://127.0.0.1:5000/tes/getall/
link git jojo: https://github.com/JonathanGun/UtangBot
heroku login
heroku addons:create heroku-postgresql:hobby-dev --app botutang
heroku config --app botutang
heroku pg:psql --app botutang
heroku logs --tail
'''


import os
from tkinter import Y
from app.db import setup_db, db_drop_and_create_all
from app.db import register, addUtang, getUser, getUtang, detail, total
from flask import Flask, request, abort
from flask_cors import CORS
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # reset db
    @app.route("/tes/reset_db/")
    def reset_db():
        db_drop_and_create_all()
        
        x = register("12354", "register kevin")
        x = register("12345", "register andy")
        x = register("123456", "register sebas")
        x = register("123", "register ari")


        x = addUtang("12354", "add andy nasi 100")
        x = addUtang("12354", "add andy nasi2 10")
        x = addUtang("12354", "add andy nasi3 35")
        
        x = addUtang("12345", "add kevin lauk 20")
        x = addUtang("12345", "add kevin mie goreng 30")
        
        x = addUtang("12354", "add sebas ayam rebus 8")
        x = addUtang("12354", "add sebas ikan 9")

        x = addUtang("123456", "add kevin sayur 25")
        x = addUtang("123456", "add kevin nasi goreng 31")

        return 'OK'



    # handler untuk line
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




    # handler manual
    @app.route("/tes/reg/")
    def reg():
        x = register("12354", "register kevin")
        x = register("12345", "register andy")
        x = register("123456", "register sebas")
        x = register("123", "register ari")

        return "OK %s" % (x)

    @app.route("/tes/tab1/") # print tabel user
    def getall1():
        x = getUser()
        for i in x:
            print(i)
        return 'OK' + ' ' + "".join(map(str, x))
    
    @app.route("/tes/tab2/") # print tabel utang
    def getall2():
        x = getUtang()
        for i in x:
            print(i)
        return 'OK' + ' ' + "".join(map(str, x))
    
    @app.route("/tes/add/")
    def addutang():
        x = addUtang("12354", "add andy nasi 100")
        x = addUtang("12354", "add andy nasi2 10")
        x = addUtang("12354", "add andy nasi3 35")
        
        x = addUtang("12345", "add kevin lauk 20")
        x = addUtang("12345", "add kevin mie goreng 30")
        
        x = addUtang("12354", "add sebas ayam rebus 8")
        x = addUtang("12354", "add sebas ikan 9")

        x = addUtang("123456", "add kevin sayur 25")
        x = addUtang("123456", "add kevin nasi goreng 31")
        return 'OK'
    
    @app.route("/tes/detail/")
    def detail1():
        x = detail("12354", "detail andy")
        return 'OK'

    @app.route("/tes/total/")
    def total1():
        x = total("12354")
        return 'OK'

    return app