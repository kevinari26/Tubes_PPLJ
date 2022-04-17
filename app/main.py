'''
run lokal: http://127.0.0.1:5000/tes/getall/
run cloud: https://botutang.herokuapp.com/tes/tab1/

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
from app.db import register, addUtang, detail, total, pay, confirm
from app.db import getUser, getUtang 
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
        sender_id = line_bot_api.get_profile(event.source.user_id).user_id
        print(sender_id)
        
        msg = event.message.text

        if (msg.lower().strip() == "halo"):
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage (text = "halo juga")
            )
        
        elif (msg.lower().startswith('register ')):
            # register <username>
            try:
                username = msg.split(" ", 1)[1].strip()
                out_string = register (sender_id, username)
                
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage (text = out_string)
                )
            except LineBotApiError as e:
                print (e)
        
        elif (msg.lower().startswith('add ')):
            # add <username debtor> <komentar> <harga>
            try:
                temp = msg.split(" ", 1)[1].strip().split(" ", 1)
                debtor = temp[0].strip() # username debtor
                temp = temp[1].rsplit(" ", 1)
                komen = temp[0].strip() # keterangan benda yang diutangkan
                harga = float(temp[1])
                out_string, lender, id_line_debtor, nomor = addUtang(event.source.user_id, debtor, komen, harga)
                
                if (lender != 0):
                    line_bot_api.push_message( # push message untuk debtor
                        id_line_debtor,
                        messages=[
                        TemplateSendMessage(
                            alt_text = "Tagihan utang. Cek tagihan di smartphone Anda.",
                            template = ConfirmTemplate(
                                text = "Tagihan utang '%s' dari '%s' sebesar '%.3f'" % (komen, lender, harga),
                                actions=[
                                    PostbackAction(
                                        label = 'yes',
                                        display_text = 'terima tagihan',
                                        data = nomor
                                    ),
                                    PostbackAction(
                                        label = 'no',
                                        display_text = 'tolak tagihan',
                                        data = nomor
                                    ),
                                ]
                            )
                        )],
                    )
                line_bot_api.reply_message( # reply message untuk lender
                    event.reply_token,
                    TextSendMessage (text = out_string)
                )
            except LineBotApiError as e:
                print (e)
        
        elif (msg.lower().startswith('detail ')):
            # detail <username debtor>
            try:
                debtor = msg.split(" ", 1)[1].strip()
                out_string = detail (event.source.user_id, debtor)
                
                line_bot_api.reply_message( # reply message untuk user
                    event.reply_token,
                    TextSendMessage (text = out_string)
                )
            except LineBotApiError as e:
                print (e)
        
        
        elif (msg.lower().strip() == 'total'):
            # total
            try:
                out_string = total (event.source.user_id)
                
                line_bot_api.reply_message( # reply message untuk user
                    event.reply_token,
                    TextSendMessage (text = out_string)
                )
            except LineBotApiError as e:
                print (e)
        
        elif (msg.lower().startswith('pay ')):
            # pay <username debtor>
            try:
                user_target = msg.split(" ", 1)[1].strip()
                out_string = pay (event.source.user_id, user_target)
                
                line_bot_api.reply_message( # reply message untuk user
                    event.reply_token,
                    TextSendMessage (text = out_string)
                )
            except LineBotApiError as e:
                print (e)
        
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
                line_bot_api.push_message(
                    sender_id,
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

        # else:
        #     line_bot_api.reply_message(
        #         event.reply_token,
        #         TextSendMessage(text=msg)
        #     )
    
    @handler.add(PostbackEvent) # handler postback message
    def handle_postback(event):
        confirm (event.postback.data, event.postback.label)
        # if event.postback.data == "promotion=true":
        #     pass
            # line_id = event.source.user_id
            # user_profile = User.objects.get(username=line_id)
            # user_profile.promotable= True # set promotable to be True
            # user_profile.save()




    # handler manual
    @app.route("/tes/reset_db/")
    def reset_db():
        db_drop_and_create_all()
        
        x = register("U8cea9944d781b6557cfba7ce0e9c91c7", "ari")
        x = register("12345", "andy")
        x = register("123456", "sebas")
        x = register("123", "sam")


        a, b, c, d = addUtang("U8cea9944d781b6557cfba7ce0e9c91c7", "andy", "nasi", 100)
        a, b, c, d = addUtang("U8cea9944d781b6557cfba7ce0e9c91c7", "andy", "nasi2", 10)
        a, b, c, d = addUtang("U8cea9944d781b6557cfba7ce0e9c91c7", "andy", "nasi3", -35)
        
        a, b, c, d = addUtang("123", "ari", "lauk lauk", 20)
        a, b, c, d = addUtang("123", "ari", "lauk lauk 2", 30)

        a, b, c, d = addUtang("12345", "sam", "lauk", 20)
        a, b, c, d = addUtang("12345", "sam", "mie goreng", 30)
        
        a, b, c, d = addUtang("U8cea9944d781b6557cfba7ce0e9c91c7", "sebas", "ayam rebus", 8)
        a, b, c, d = addUtang("U8cea9944d781b6557cfba7ce0e9c91c7", "sebas", "ikan", 9)

        a, b, c, d = addUtang("123456", "sam", "sayur", 25)
        a, b, c, d = addUtang("123456", "sam", "nasi goreng", 31)

        return 'OK'
    
    @app.route("/tes/reg/")
    def reg():
        x = register("U8cea9944d781b6557cfba7ce0e9c91c7", "ari")
        x = register("12345", "andy")
        x = register("123456", "sebas")
        x = register("123", "jonathan")
        return "OK %s" % (x)

    @app.route("/tes/tab1/") # print tabel user
    def getall1():
        listUser = getUser()
        out_string = ""
        for row in listUser:
            # date_str = row.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            out_string += "{%d | %s | %s | %s} \n" % (row.id_user, row.id_line, row.username, row.timestamp)
        print (out_string)
        return 'OK ' + out_string
    
    @app.route("/tes/tab2/") # print tabel utang
    def getall2():
        listUser = getUtang()
        out_string = ""
        for row in listUser:
            out_string += "{%d | %d | %d | %s | %.3f | %d | %s} \n" % (row.nomor, row.id_lender, row.id_debtor, row.komen, row.harga, row.status, row.time_insert)
        print (out_string)
        # print (listUser[0].timestamp.strftime("%Y-%m-%d"))
        return 'OK ' + out_string
    
    @app.route("/tes/add/")
    def addutang():
        a, b, c, d = addUtang("U8cea9944d781b6557cfba7ce0e9c91c7", "andy", "nasi", 100)
        a, b, c, d = addUtang("U8cea9944d781b6557cfba7ce0e9c91c7", "andy", "nasi2", 10)
        a, b, c, d = addUtang("U8cea9944d781b6557cfba7ce0e9c91c7", "andy", "nasi3", -35)
        
        a, b, c, d = addUtang("123", "ari", "lauk lauk", 20)
        a, b, c, d = addUtang("123", "ari", "lauk lauk 2", 30)

        a, b, c, d = addUtang("12345", "kevin", "lauk", 20)
        a, b, c, d = addUtang("12345", "kevin", "mie goreng", 30)
        
        a, b, c, d = addUtang("U8cea9944d781b6557cfba7ce0e9c91c7", "sebas", "ayam rebus", 8)
        a, b, c, d = addUtang("U8cea9944d781b6557cfba7ce0e9c91c7", "sebas", "ikan", 9)

        a, b, c, d = addUtang("123456", "kevin", "sayur", 25)
        a, b, c, d = addUtang("123456", "kevin", "nasi goreng", 31)
        return 'OK'
    
    @app.route("/tes/detail/")
    def detail1():
        x = detail("U8cea9944d781b6557cfba7ce0e9c91c7", "andy")
        print (x)
        return 'OK ' + x

    @app.route("/tes/total/")
    def total1():
        x = total ("U8cea9944d781b6557cfba7ce0e9c91c7")
        print (x)
        return 'OK ' + x

    @app.route("/tes/pay/")
    def pay1():
        x = pay   ("U8cea9944d781b6557cfba7ce0e9c91c7", "andy")
        return 'OK'
    
    return app
