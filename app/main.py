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

procfile old: web: gunicorn wsgi:app

# upload kode ke server
git push heroku main
heroku git:remote -a botutang


# tutorial run 
heroku login
heroku git:clone -a botutang 
cd botutang
git add .
git commit -am "make it better"
git push heroku master

heroku login
cd my-project/
git init
heroku git:remote -a vast-mesa-95190
git add .
git commit -am "make it better"
git push heroku master
heroku git:remote -a vast-mesa-95190
'''

# register <username>
# add <username debtor> <komentar> <harga>
# detail <username debtor>
# total
# pay <username debtor>

import os
from app.db import setup_db, db_drop_and_create_all
from app.db import register, add, add_confirm, detail, total, pay, pay_confirm
from app.db import getUser, getUtang
import flask
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
            print (flask.__version__)
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
                out_string, lender, id_line_debtor, nomor = add(event.source.user_id, debtor, komen, harga)
                
                if (lender != 0): # add utang berhasil
                    line_bot_api.push_message( # push message untuk debtor
                        id_line_debtor,
                        messages=[
                        TemplateSendMessage(
                            alt_text = "Tagihan utang. Cek tagihan di smartphone Anda.",
                            template = ConfirmTemplate(
                                text = "Tagihan utang '%s' dari '%s' sebesar '%.3f'." % (komen, lender, harga),
                                actions=[
                                    PostbackAction(
                                        label = "terima tagihan",
                                        display_text = "Terima tagihan utang '%s' dari '%s' sebesar '%.3f'" % (komen, lender, harga),
                                        # kirim commmand, nomor, status, id_line_lender, debtor, komen, harga
                                        data = "add_confirm %d 1 %s %s %s %.3f" % (nomor, event.source.user_id, debtor, komen, harga)
                                    ),
                                    PostbackAction(
                                        label = "tolak tagihan",
                                        display_text = "Tolak tagihan utang '%s' dari '%s' sebesar '%.3f'" % (komen, lender, harga),
                                        data = "add_confirm %d 2 %s %s %s %.3f" % (nomor, event.source.user_id, debtor, komen, harga)
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
                # butuh out_string, id_line_lender, debtor, dibayarKeLender
                user_lender = msg.split(" ", 1)[1].strip()
                out_string, id_line_lender, lender, debtor, dibayarKeLender, arrNomor = pay (event.source.user_id, user_lender)
                
                if (debtor != 0): # pay berhasil
                    stringNomor = ""
                    for ele in arrNomor:
                        stringNomor += "%d " % ele
                    line_bot_api.push_message( # push message untuk lender
                        id_line_lender,
                        messages=[
                        TemplateSendMessage(
                            alt_text = "Pembayaran utang. Cek tagihan di smartphone Anda.",
                            template = ConfirmTemplate(
                                text = "'%s' melakukan pembayaran utang sebesar '%.3f'." % (debtor, dibayarKeLender),
                                actions=[
                                    PostbackAction(
                                        label = "sudah diterima",
                                        display_text = "Pembayaran utang sudah diterima dari '%s' sebesar '%.3f'" % (debtor, dibayarKeLender),
                                        # kirim command, confirm, id_line_debtor, lender, dibayarKeLender, arrNomor
                                        data = "pay_confirm 1 %s %s %.3f %s" % (event.source.user_id, lender, dibayarKeLender, stringNomor)
                                    ),
                                    PostbackAction(
                                        label = "belum diterima",
                                        display_text = "Pembayaran utang belum diterima dari '%s' sebesar '%.3f'" % (debtor, dibayarKeLender),
                                        data = "pay_confirm 0 %s %s %.3f %s" % (event.source.user_id, lender, dibayarKeLender, stringNomor)
                                    ),
                                ]
                            )
                        )],
                    )
                line_bot_api.reply_message( # reply message untuk user
                    event.reply_token,
                    TextSendMessage (text = out_string)
                )
            except LineBotApiError as e:
                print (e)
        
        elif (msg == "help"):
            try:
                out_string = 'register <username>\n'\
                    'add <username target> <komentar> <harga>\n'\
                    'detail <username target>\n'\
                    'total\n'\
                    'pay <username target>'
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage (text = out_string),
                )
            except LineBotApiError as e:
                print (e)



    
    @handler.add(PostbackEvent) # handler postback message
    def handle_postback(event):
        try:
            command = event.postback.data.split(" ", 1)[0] # cek command
            if (command == "add_confirm"):
                # command, nomor, status, id_line_lender, debtor, komen, harga
                tempArr = event.postback.data.split(" ", 5) # split data
                nomor = int(tempArr[1])
                status = tempArr[2]
                id_line_lender = tempArr[3]
                debtor = tempArr[4]
                tempArr = tempArr[5].rsplit(" ", 1)
                komen = tempArr[0]
                harga = tempArr[1]
                temp = add_confirm (nomor, status) # lakukan konfirmasi
                if (temp == 0): # konfirmasi berhasil
                    if (status == 1): # utang diterima
                        out_string = "Tagihan utang '%s' untuk '%s' sebesar '%s' telah diterima." % (komen, debtor, harga)
                    else: # utang ditolak
                        out_string = "Tagihan utang '%s' untuk '%s' sebesar '%s' telah ditolak." % (komen, debtor, harga)
                    line_bot_api.push_message( # push message ke lender untuk menunjukkan tagihan diterima atau ditolak
                        id_line_lender,
                        TextSendMessage (text = out_string)
                    )
                else: # konfirmasi gagal
                    line_bot_api.reply_message( # reply message untuk debtor
                        event.reply_token,
                        TextSendMessage (text = temp)
                    )
            elif (command == "pay_confirm"):
                # command, confirm, id_line_debtor, lender, dibayarKeLender, arrNomor
                tempArr = event.postback.data.split(" ", 5) # split data
                confirm = tempArr[1]
                id_line_debtor = tempArr[2]
                lender = tempArr[3]
                dibayarKeLender = tempArr[4]
                arrNomor = list(map(int, tempArr[5].split()))
                temp = pay_confirm (arrNomor)
                if (temp == 0): # konfirmasi berhasil
                    if (confirm == "1"): # konfirmasi diterima
                        out_string = "Konfirmasi pembayaran utang kepada '%s' sebesar '%s' telah diterima oleh '%s'." % (lender, dibayarKeLender, lender)
                    else: # konfirmasi ditolak
                        out_string = "Konfirmasi pembayaran utang kepada '%s' sebesar '%s' telah ditolak oleh '%s'." % (lender, dibayarKeLender, lender)
                    line_bot_api.push_message( # push message ke lender untuk menunjukkan tagihan diterima atau ditolak
                        id_line_debtor,
                        TextSendMessage (text = out_string)
                    )
                else: # konfimasi gagal
                    line_bot_api.reply_message( # reply message untuk debtor
                        event.reply_token,
                        TextSendMessage (text = temp)
                    )
        except LineBotApiError as e:
            print (e)





    # handler manual
    @app.route("/tes/reset_db/")
    def reset_db():
        db_drop_and_create_all()
        
        x = register("U8cea9944d781b6557cfba7ce0e9c91c7", "ari")
        x = register("U3d13f5d6ce0d932f34429b7555af1f50", "luck")
        x = register("U96e17e28d1c66ed292688b530b929084", "Sebastian")
        # x = register("123", "sam")


        # a, b, c, d = addUtang("U8cea9944d781b6557cfba7ce0e9c91c7", "luck", "nasi", 100)
        # a, b, c, d = addUtang("U8cea9944d781b6557cfba7ce0e9c91c7", "luck", "nasi2", 10)
        # a, b, c, d = addUtang("U8cea9944d781b6557cfba7ce0e9c91c7", "luck", "nasi3", -35)
        
        # a, b, c, d = addUtang("123", "ari", "lauk lauk", 20)
        # a, b, c, d = addUtang("123", "ari", "lauk lauk 2", 30)

        # a, b, c, d = addUtang("U3d13f5d6ce0d932f34429b7555af1f50", "sam", "lauk", 20)
        # a, b, c, d = addUtang("U3d13f5d6ce0d932f34429b7555af1f50", "sam", "mie goreng", 30)
        
        # a, b, c, d = addUtang("U8cea9944d781b6557cfba7ce0e9c91c7", "sebas", "ayam rebus", 8)
        # a, b, c, d = addUtang("U8cea9944d781b6557cfba7ce0e9c91c7", "sebas", "ikan", 9)

        # a, b, c, d = addUtang("123456", "sam", "sayur", 25)
        # a, b, c, d = addUtang("123456", "sam", "nasi goreng", 31)

        return 'OK'
    
    @app.route("/tes/reg/")
    def reg():
        x = register("U8cea9944d781b6557cfba7ce0e9c91c7", "ari")
        x = register("12345", "luck")
        x = register("123456", "sebas")
        x = register("123", "jonathan")
        return "OK %s" % (x)

    @app.route("/tes/add/")
    def addutang():
        a, b, c, d = add("U8cea9944d781b6557cfba7ce0e9c91c7", "luck", "nasi", 100)
        a, b, c, d = add("U8cea9944d781b6557cfba7ce0e9c91c7", "luck", "nasi2", 10)
        a, b, c, d = add("U8cea9944d781b6557cfba7ce0e9c91c7", "luck", "nasi3", -35)
        
        a, b, c, d = add("123", "ari", "lauk lauk", 20)
        a, b, c, d = add("123", "ari", "lauk lauk 2", 30)

        a, b, c, d = add("12345", "kevin", "lauk", 20)
        a, b, c, d = add("12345", "kevin", "mie goreng", 30)
        
        a, b, c, d = add("U8cea9944d781b6557cfba7ce0e9c91c7", "sebas", "ayam rebus", 8)
        a, b, c, d = add("U8cea9944d781b6557cfba7ce0e9c91c7", "sebas", "ikan", 9)

        a, b, c, d = add("123456", "kevin", "sayur", 25)
        a, b, c, d = add("123456", "kevin", "nasi goreng", 31)
        return 'OK'
    
    @app.route("/tes/detail/")
    def detail1():
        x = detail("U8cea9944d781b6557cfba7ce0e9c91c7", "luck")
        print (x)
        return 'OK ' + x

    @app.route("/tes/total/")
    def total1():
        x = total ("U8cea9944d781b6557cfba7ce0e9c91c7")
        print (x)
        return 'OK ' + x

    @app.route("/tes/pay/")
    def pay1():
        x = pay   ("U8cea9944d781b6557cfba7ce0e9c91c7", "luck")
        return 'OK'
    


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
            out_string += "{%d | %d | %d | %s | %.3f | %d | %s | %s | %s} \n" % (row.nomor, row.id_lender, row.id_debtor, row.komen, row.harga, row.status, row.time_insert, row.time_konfir, row.time_lunas)
        print (out_string)
        # print (listUser[0].timestamp.strftime("%Y-%m-%d"))
        return 'OK ' + out_string
    
    return app
