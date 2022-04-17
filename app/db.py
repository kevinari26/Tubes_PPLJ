import os
from datetime import datetime
import pytz
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

def setup_db(app):
    '''
        binds a flask application and a SQLAlchemy service
    '''
    database_path = os.environ.get('DATABASE_URL').split("://")
    database_path[0] = database_path[0].replace('postgres', 'postgresql')
    database_path = "://".join(database_path)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)

def db_drop_and_create_all():
    '''
        drops the database tables and starts fresh
        can be used to initialize a clean database
    '''
    db.drop_all()
    db.create_all()




class DaftarUser(db.Model): # tabel daftar user yang sudah register ke bot
    __tablename__ = 'daftar_user'
    id_user = db.Column(db.Integer, primary_key = True) # nomor baris sekaligus nomor id user
    id_line = db.Column(db.String(50)) # id user
    username = db.Column(db.String(20)) # username
    timestamp = db.Column(db.DateTime(timezone=True), default=db.func.now())


    def __init__(self, id_line, username): # constructor
        self.id_line = id_line
        self.username = username

    def insert(self): # insert ke database
        db.session.add(self)
        db.session.commit()

    def delete(self): # delete dari database
        db.session.delete(self)
        db.session.commit()

    def update(self): # update isi database
        db.session.commit()


    @classmethod
    def searchUser(cls, stringToSearch): # search id_line atau username sesuai stringToSearch
        return cls.query.filter( 
            (cls.id_line == stringToSearch) |
            (cls.username == stringToSearch)
        ).all()
    
    @classmethod
    def userById(cls, id_user): # search username sesuai id_user
        return cls.query.filter( # return username
            (cls.id_user == id_user)
        ).all()[0].username



class DaftarUtang(db.Model): # tabel daftar utang
    __tablename__ = 'daftar_utang'
    nomor = db.Column(db.Integer, primary_key = True) # nomor baris
    id_lender = db.Column(db.Integer) # id pemberi utang
    id_debtor = db.Column(db.Integer) # id peminjam
    komen = db.Column(db.String(30)) # username
    harga = db.Column(db.Float) # besar utang
    status = db.Column(db.Integer, default=0)
    # 0: utang baru masuk
    # 1: utang dikonfirmasi 'yes'
    # 2: utang dikonfirmasi 'no'
    # 3: utang sudah dilunasi
    time_insert = db.Column(db.DateTime(timezone=True), default=db.func.now())
    time_konfir = db.Column(db.DateTime(timezone=True))
    time_lunas = db.Column(db.DateTime(timezone=True))


    def __init__(self, id_lender, id_debtor, komen, harga, time_insert): # constructor
        self.id_lender = id_lender
        self.id_debtor = id_debtor
        self.komen = komen
        self.harga = harga
        self.time_insert = time_insert

    def insert(self): # insert ke database
        db.session.add(self)
        db.session.commit()
        return self.nomor

    def delete(self): # delete dari database
        db.session.delete(self)
        db.session.commit()

    def update(self): # update isi database
        db.session.commit()


    @classmethod
    def detail(cls, id_user, id_target):
        return cls.query.filter( # search detail utang 2 orang tertentu
            (((cls.id_lender == id_user) & (cls.id_debtor == id_target)) |
            ((cls.id_lender == id_target) & (cls.id_debtor == id_user))) &
            (cls.status == 1)
        ).order_by(
            cls.nomor,
        ).all()
    
    @classmethod
    def detailForSum(cls, id_user): # detail untuk hitung total utang
        return cls.query.with_entities(
            cls.id_lender,
            cls.id_debtor,
            db.func.sum(cls.harga).label("harga"),
        ).filter( # search id_line atau username sesuai stringToSearch
            ((cls.id_lender == id_user) | (cls.id_debtor == id_user)) &
            (cls.status == 1)
        ).group_by(
            cls.id_lender,
            cls.id_debtor,
        ).all()
    
    @classmethod
    def searchByNomor(cls, nomor): # search username sesuai id_user
        return cls.query.filter( # return username
            (cls.nomor == nomor)
        ).all()[0]





# fungsi lain
def searchArr (arr, eleToSearch): # search dari array, return indexnya (-1 = tidak ditemukan) 
    searchResult = [x for x in arr if x == eleToSearch]
    if (len(searchResult)):
        return arr.index(searchResult[0])
    else:
        return -1


# fungsi untuk akses database
def register(id_line, username):
    listIdLine = DaftarUser.searchUser (id_line) # cek apakah id line sudah pernah register
    if (len(listIdLine)): # jika id line sudah pernah register
        return "Registrasi gagal.\nAkun Line ini sudah pernah melakukan registrasi dengan username: %s" % (listIdLine[0].username)
    else: # jika id line belum pernah register
        tempArr = username.split() # penampung username
        if (len(tempArr)==1) & (tempArr[0]!=""): # username tidak ada spasi
            listUser = DaftarUser.searchUser (tempArr[0].strip()) # cek apakah username sudah digunakan
            if (len(listUser)==0): # username tidak pernah digunakan
                DaftarUser(id_line, tempArr[0]).insert() # insert ke database
                return "Registrasi berhasil."
            else: # username sudah digunakan
                return "Registrasi gagal.\nUsername sudah digunakan oleh akun lain."
        elif (len(tempArr)!=1): # username ada spasi
            return "Registrasi gagal.\nUsername tidak boleh menggunakan spasi!"



def addUtang(id_line, debtor, komen, harga):
    cekLender = DaftarUser.searchUser (id_line) # cek apakah lender sudah register
    cekDebtor = DaftarUser.searchUser (debtor) # cek apakah debtor sudah register
    if (len(cekLender) & len(cekDebtor)): # jika lender dan debtor sudah register
        id_lender = cekLender[0].id_user
        id_debtor = cekDebtor[0].id_user
        time_insert = datetime.now().replace(tzinfo=pytz.timezone("Asia/Jakarta"))
        lender = cekLender[0].username
        id_line_debtor = cekDebtor[0].id_line
        # insert utang ke database
        nomor = DaftarUtang(id_lender, id_debtor, komen, harga, time_insert).insert()
        return ("Penambahan utang '%s' untuk '%s' sebesar '%.3f' berhasil dilakukan.\nMenunggu konfirmasi dari %s." % (komen, debtor, harga, debtor), lender, id_line_debtor, nomor)
    else:
        return ("Akun Anda dan/atau akun target belum melakukan registrasi.", 0, 0, 0)



def detail(id_line, debtor):
    cekLender = DaftarUser.searchUser (id_line) # cek apakah lender sudah register
    cekDebtor = DaftarUser.searchUser (debtor) # cek apakah debtor sudah register
    
    if (len(cekLender) & len(cekDebtor)): # jika lender dan debtor sudah register
        lender = [cekLender[0].id_user, cekLender[0].username] # id, username
        debtor = [cekDebtor[0].id_user, cekDebtor[0].username] # id, username
        detailUtang = DaftarUtang.detail(lender[0], debtor[0])
        
        sum = 0
        out_string = "Detail utang %s kepada %s:\n" % (debtor[1], lender[1])
        for row in detailUtang:
            if (row.id_lender == lender[0]): # debtor berutang kepada lender
                out_string += "%.3f | %s\n" % (row.harga, row.komen)
                sum += row.harga
            else: # lender berutang ke debtor
                out_string += "%.3f | %s\n" % (-row.harga, row.komen)
                sum -= row.harga
        out_string += "\nTotal utang %s kepada %s: %.3f" % (debtor[1], lender[1], sum)
        return out_string
    else:
        return "Akun Anda dan/atau akun target belum melakukan registrasi."



def total (id_line):
    cekLender = DaftarUser.searchUser (id_line) # cek apakah lender sudah register
    # print ("halooooo %d" % (len(cekLender)))
    if (len(cekLender)):
        lender = [cekLender[0].id_user, cekLender[0].username] # id_user, username
        listUtang = DaftarUtang.detailForSum(lender[0])
        arrDibayar_oleh = []
        arrDibayar_harga = []

        for ele in listUtang:
            # print ("%d %d %.3f" % (ele.id_lender, ele.id_debtor, ele.harga))
            if (ele.id_lender == lender[0]): # jika debtor berutang ke lender
                index = searchArr (arrDibayar_oleh, ele.id_debtor) # cek apakah debtor sudah ada di arrDibayar_oleh
                if (index == -1): # jika tidak ditemukan
                    arrDibayar_oleh.append (ele.id_debtor)
                    arrDibayar_harga.append (ele.harga)
                else: # jika ditemukan
                    arrDibayar_harga[index] += ele.harga
            else: # jika lender berutang ke debtor
                index = searchArr (arrDibayar_oleh, ele.id_lender) # cek apakah lender sudah ada di arrDibayar_oleh
                if (index == -1): # jika tidak ditemukan
                    arrDibayar_oleh.append (ele.id_debtor)
                    arrDibayar_harga.append (-ele.harga)
                else: # jika ditemukan
                    arrDibayar_harga[index] -= ele.harga

        out_string = "%s perlu membayar kepada:\n" % (lender[1])
        sum = 0
        for i in range (len(arrDibayar_harga)):
            if (arrDibayar_harga[i] < 0): 
                out_string += "%s: %.3f\n" % (DaftarUser.userById(arrDibayar_oleh[i]), abs(arrDibayar_harga[i]))
                sum += arrDibayar_harga[i]
        out_string += "\n%s akan dibayar oleh:\n" % (lender[1])
        for i in range (len(arrDibayar_harga)):
            if (arrDibayar_harga[i] > 0): 
                out_string += "%s: %.3f\n" % (DaftarUser.userById(arrDibayar_oleh[i]), abs(arrDibayar_harga[i]))
                sum += arrDibayar_harga[i]
        out_string += "\nTotal utang yang harus dibayar %s: %.3f" % (lender[1], -sum)
        return out_string
    else:
        return "Akun Anda belum melakukan registrasi."



def pay (id_line, user_target):
    cekLender = DaftarUser.searchUser (id_line) # cek apakah lender sudah register
    cekDebtor = DaftarUser.searchUser (user_target) # cek apakah debtor sudah register
    if (len(cekLender) & len(cekDebtor)): # jika lender dan debtor sudah register
        lender = [cekLender[0].id_user, cekLender[0].username] # id, username
        debtor = [cekDebtor[0].id_user, cekDebtor[0].username] # id, username
        detailUtang = DaftarUtang.detail(lender[0], debtor[0])
        for ele in detailUtang:
            if (ele.status == 0):
                ele.status = 3
                ele.time_lunas = datetime.now().replace(tzinfo=pytz.timezone("Asia/Jakarta"))
                ele.update()
        return "Pembayaran utang %s kepada %s berhasil dilakukan." % (lender, debtor)
    else:
        return "Username Anda dan/atau username target belum melakukan registrasi."



def confirm (nomor, label):
    data = DaftarUser.searchByNomor (nomor)
    if (label=="yes"):
        data.status = 1
    else:
        data.status = 2
    data.time_konfir = datetime.now().replace(tzinfo=pytz.timezone("Asia/Jakarta"))
    data.update()




def getUser():
    return DaftarUser.query.all()

def getUtang():
    return DaftarUtang.query.all()
