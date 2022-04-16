'''
run lokal: http://127.0.0.1:5000/tes/getall/
https://botutang.herokuapp.com/tes/getall/
link git jojo: https://github.com/JonathanGun/UtangBot
heroku login
heroku create
heroku addons:create heroku-postgresql:hobby-dev --app botutang
heroku config --app botutang
heroku pg:psql --app botutang
heroku logs --tail
heroku logs --tail --app botutang
'''


import os
from app.db import setup_db, db_drop_and_create_all
from app.db import register, addUtang, getUser, getUtang, detail, total, pay
from flask import Flask, request, abort
from flask_cors import CORS
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import ConfirmTemplate, MessageAction, MessageEvent, PostbackAction, PostbackEvent, SourceGroup, SourceRoom, TemplateSendMessage, TextMessage, TextSendMessage  # NOQA


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # inisialisasi
    line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))
    handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))

    # handler untuk line
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

    @handler.add(MessageEvent, message=TextMessage) # handler text message
    def handle_text_message(event):
        msg = ""
        # profile = line_bot_api.get_profile(event.source.user_id)
        
        msg = event.message.text

        if (msg == "halo"):
            msg = "halo juga"
        elif (msg.lower().startswith('register ')):
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Command register")
            )
        elif (msg.lower().startswith('add ')):
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
        elif (msg == "help"):
            try:
                line_bot_api.reply_message(
                    event.reply_token,
                    # TextSendMessage (text = "halo"),
                    messages=[
                    TemplateSendMessage(
                        alt_text='Confirm template',
                        template=ConfirmTemplate(
                            text='Are you sure?',
                            actions=[
                                PostbackAction(
                                    label='postback',
                                    display_text='postback text',
                                    data='action=buy&itemid=1'
                                ),
                                MessageAction(
                                    label='message',
                                    text='message text'
                                )
                            ]
                        )
                    )],
                )
            except LineBotApiError as e:
                print (e)

        elif (msg == "help2"):
            try:
                sender_id = line_bot_api.get_profile(event.source.user_id)
                line_bot_api.push_message(
                    sender_id,
                    TextSendMessage (text = "halo"),
                    # messages=[
                    # TemplateSendMessage(
                    #     alt_text='Confirm template',
                    #     template=ConfirmTemplate(
                    #         text='Are you sure?',
                    #         actions=[
                    #             PostbackAction(
                    #                 label='postback',
                    #                 display_text='postback text',
                    #                 data='action=buy&itemid=1'
                    #             ),
                    #             MessageAction(
                    #                 label='message',
                    #                 text='message text'
                    #             )
                    #         ]
                    #     )
                    # )],
                )
            except LineBotApiError as e:
                print (e)

        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=msg)
            )
    
    @handler.add(PostbackEvent) # handler postback message
    def handle_postback(event):
        if event.postback.data == "promotion=true":
            pass
            # line_id = event.source.user_id
            # user_profile = User.objects.get(username=line_id)
            # user_profile.promotable= True # set promotable to be True
            # user_profile.save()




    # handler manual
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
    
    @app.route("/tes/reg/")
    def reg():
        x = register("12354", "register kevin")
        x = register("12345", "register andy")
        x = register("123456", "register sebas")
        x = register("123", "register ari")

        return "OK %s" % (x)

    @app.route("/tes/tab1/") # print tabel user
    def getall1():
        listUser = getUser()
        out_string = ""
        for row in listUser:
            # date_str = row.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            out_string += "{%d | %s | %s | %s} \n" % (row.id_user, row.id_line, row.username, row.timestamp)
        print (out_string)
        return 'OK' + ' ' + out_string
    
    @app.route("/tes/tab2/") # print tabel utang
    def getall2():
        listUser = getUtang()
        out_string = ""
        for row in listUser:
            out_string += "{%d | %d | %d | %s | %.3f | %d | %s} \n" % (row.nomor, row.id_lender, row.id_debtor, row.komen, row.harga, row.status, row.time_insert)
        print (out_string)
        # print (listUser[0].timestamp.strftime("%Y-%m-%d"))
        return 'OK' + ' ' + out_string
    
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

    @app.route("/tes/pay/")
    def pay1():
        x = pay("12354", "pay andy")
        return 'OK'
    
    return app
