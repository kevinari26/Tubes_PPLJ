
import os
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

    # def __str__(self): # print database
    #     d = {}
    #     for column in self.__table__.columns:
    #         d[column.name] = str(getattr(self, column.name))
    #     return str(d)
    
    @classmethod
    def searchUser(cls, stringToSearch):
        return cls.query.filter( # search id_line atau username sesuai stringToSearch
            (cls.id_line == stringToSearch) |
            (cls.username == stringToSearch)
        ).all()
    
    @classmethod
    def userById(cls, id_user):
        return cls.query.filter( # search username sesuai id_user
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

    def __init__(self, id_lender, id_debtor, komen, harga): # constructor
        self.id_lender = id_lender
        self.id_debtor = id_debtor
        self.komen = komen
        self.harga = harga

    def insert(self): # insert ke database
        db.session.add(self)
        db.session.commit()

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
            (cls.status == 0)
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
            (cls.status == 0)
        ).group_by(
            cls.id_lender,
            cls.id_debtor,
        ).all()
        
    
    '''
    @classmethod
    def get_all(cls, group_id):
        return cls.query.with_entities(
            cls.item_name,
            cls.owner,
            cls.price,
            cls.created_at,
        ).filter(
            (cls.group_id == group_id) &
            (cls.is_calced.is_(False))
        ).order_by(
            cls.created_at,
        ).group_by(
            cls.taker,
        ).all()
    '''





# fungsi untuk akses database
def register(id_line, in_string):
    listUser = DaftarUser.searchUser (id_line) # cek apakah user sudah register
    if (len(listUser)): # jika sudah register
        return "Akun Line ini sudah pernah registrasi dengan username: %s" % (listUser[0].username)
    else: # jika belum register
        tempArr = in_string.split(" ", 1)[1].strip().split(" ")
        if (len(tempArr)==1): # username tidak ada spasi
            # insert ke database
            DaftarUser(id_line, tempArr[0]).insert()
            return "Registrasi berhasil."
        else:
            return "Username tidak boleh menggunakan spasi!"



def addUtang(id_line, in_string):
    # nomor = Integer
    # id_lender = Integer
    # id_debtor = Integer
    # komen = String(30)
    # harga = Float
    # status = Integer 
    # add <username target> <komentar> <harga>

    datas = in_string.split(" ", 2)
    debtor = datas[1]
    datas = datas[2].rsplit(" ", 1)
    id_lender = 0
    id_debtor = 0
    komen = datas[0]
    harga = float(datas[1])

    cekLender = DaftarUser.searchUser (id_line) # cek apakah lender sudah register
    cekDebtor = DaftarUser.searchUser (debtor) # cek apakah debtor sudah register
    if (len(cekLender) & len(cekDebtor)): # jika lender dan debtor sudah register
        id_lender = cekLender[0].id_user
        id_debtor = cekDebtor[0].id_user
        # insert utang ke database
        DaftarUtang(id_lender, id_debtor, komen, harga).insert()


def detail(id_line, in_string):
    user_target = in_string.split(" ", 1)[1].strip()
    cekLender = DaftarUser.searchUser (id_line) # cek apakah lender sudah register
    cekDebtor = DaftarUser.searchUser (user_target) # cek apakah debtor sudah register
    lender = [cekLender[0].id_user, cekLender[0].username] # id, username
    debtor = [cekDebtor[0].id_user, cekDebtor[0].username] # id, username
    if (len(cekLender) & len(cekDebtor)): # jika lender dan debtor sudah register
        detailUtang = DaftarUtang.detail(lender[0], debtor[0])
        
        sum = 0
        out_string = "Detail utang %s kepada %s:\n" % (debtor[1], lender[1])
        for row in detailUtang:
            if (row.id_lender == lender[0]): # lender dihutangi oleh debtor
                out_string += "%.3f | %s\n" % (row.harga, row.komen)
                sum += row.harga
            else: # lender berhutang ke debtor
                out_string += "%.3f | %s\n" % (-row.harga, row.komen)
                sum -= row.harga
        out_string += "\nTotal utang %s kepada %s: %.3f" % (debtor[1], lender[1], sum)
        print (out_string)


def total(id_line):
    cekLender = DaftarUser.searchUser (id_line) # cek apakah lender sudah register
    lender = [cekLender[0].id_user, cekLender[0].username] # id, username
    listUtang = DaftarUtang.detailForSum(cekLender[0].id_user)
    
    arrLender = list(map(lambda x:x.id_lender, listUtang))
    arrDibayar = []
    for ele in listUtang:
        print ("%d %d %.3f" % (ele.id_lender, ele.id_debtor, ele.harga))
        if (ele.id_lender == lender[0]):
            index = arrLender.index(ele.id_debtor) # cari row kebalikan dari ele
            sum = ele.harga - listUtang[index].harga
            arrDibayar.append([DaftarUser.userById(ele.id_debtor), sum])
            
    out_string = "%s perlu membayar kepada:\n" % (lender[1])
    sum = 0
    for ele in arrDibayar:
        if (ele[1] < 0): 
            out_string += "%s: %.3f\n" % (ele[0], abs(ele[1]))
        sum += ele[1]
    out_string += "\n%s akan dibayar oleh:\n" % (lender[1])
    for ele in arrDibayar:
        if (ele[1] > 0): 
            out_string += "%s: %.3f\n" % (ele[0], ele[1])
    out_string += "\nTotal utang yang harus dibayar %s: %.3f" % (lender[1], -sum)
    print (out_string)


def pay(id_line, in_string):
    user_target = in_string.split(" ", 1)[1].strip()
    cekLender = DaftarUser.searchUser (id_line) # cek apakah lender sudah register
    cekDebtor = DaftarUser.searchUser (user_target) # cek apakah debtor sudah register
    lender = [cekLender[0].id_user, cekLender[0].username] # id, username
    debtor = [cekDebtor[0].id_user, cekDebtor[0].username] # id, username
    if (len(cekLender) & len(cekDebtor)): # jika lender dan debtor sudah register
        detailUtang = DaftarUtang.detail(lender[0], debtor[0])
    for ele in detailUtang:
        ele.status = 3
        ele.update()
    # detailUtang[0].price = 105
    # detailUtang[0].update()

def getUser():
    return DaftarUser.query.all()

def getUtang():
    return DaftarUtang.query.all()
