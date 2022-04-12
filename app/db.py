
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

    def __str__(self): # print database
        d = {}
        for column in self.__table__.columns:
            d[column.name] = str(getattr(self, column.name))
        return str(d)
    
    @classmethod
    def searchUser(cls, stringToSearch):
        return cls.query.filter( # search id_line atau username sesuai stringToSearch
            (cls.id_line == stringToSearch) |
            (cls.username == stringToSearch)
        ).all()
    
    


class DaftarUtang(db.Model): # tabel daftar utang
    __tablename__ = 'daftar_utang'
    nomor = db.Column(db.Integer, primary_key = True) # nomor baris
    id_lender = db.Column(db.Integer) # id pemberi utang
    id_debtor = db.Column(db.Integer) # id peminjam
    komen = db.Column(db.String(30)) # username
    price = db.Column(db.Float) # besar utang
    lunas = db.Column(db.Boolean) 

    def __init__(self, id_lender, id_debtor, komen, price, lunas): # constructor
        self.id_lender = id_lender
        self.id_debtor = id_debtor
        self.komen = komen
        self.price = price
        self.lunas = lunas

    def insert(self): # insert ke database
        db.session.add(self)
        db.session.commit()

    def delete(self): # delete dari database
        db.session.delete(self)
        db.session.commit()

    def update(self): # update isi database
        db.session.commit()

    def __str__(self): # print database
        d = {}
        for column in self.__table__.columns:
            d[column.name] = str(getattr(self, column.name))
        return str(d)
    
    @classmethod
    def detail(cls, id_user, id_target):
        return cls.query.filter( # search detail utang 2 orang tertentu
            ((cls.id_lender == id_user) & (cls.id_debtor == id_target)) |
            ((cls.id_lender == id_target) & (cls.id_debtor == id_user)) &
            (cls.lunas == False)
        ).order_by(
            cls.nomor,
        ).all()
    
    @classmethod
    def detailForSum(cls, id_user): # detail untuk hitung total utang
        return cls.query.with_entities(
            cls.id_lender,
            cls.id_debtor,
            db.func.sum(cls.price).label("price"),
        ).filter( # search id_line atau username sesuai stringToSearch
            ((cls.id_lender == id_user) | (cls.id_debtor == id_user)) &
            (cls.lunas == False)
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
        ).all()

    @classmethod
    def get_all_aggr(cls, group_id, item_name):
        # select taker, sum(amount) where item_name and group_id group by taker
        return cls.query.with_entities(
            cls.taker,
            db.func.sum(cls.amount).label("amount"),
        ).filter(
            (cls.group_id == group_id) &
            (cls.item_name == item_name)
        ).group_by(
            cls.taker,
        ).all()

    @classmethod
    def get_all(cls, group_id, item_name):
        # select taker, sum(amount) where item_name and group_id group by taker
        return cls.query.with_entities(
            cls.taker,
            cls.amount,
            cls.created_at,
        ).filter(
            (cls.group_id == group_id) &
            (cls.item_name == item_name)
        ).all()
    '''

    



# fungsi untuk akses database
def register(id_line, in_string):
    listUser = DaftarUser.searchUser (id_line) # cek apakah user sudah register
    if (len(listUser)): # jika sudah register
        return "sudah register"
    else: # jika belum register, simpan data registrasi
        username = in_string.split(" ")[1]
        # insert ke database
        DaftarUser(id_line, username).insert()
        return "register berhasil"
    # return (listUser[0])

def addUtang(id_line, in_string):
    # nomor = Integer
    # id_lender = Integer
    # id_debtor = Integer
    # komen = String(30)
    # price = Float
    # lunas = Boolean 
    # add <username target> <komentar> <harga>

    datas = in_string.split(" ", 2)
    debtor = datas[1]
    datas = datas[2].rsplit(" ", 1)
    id_lender = 0
    id_debtor = 0
    komen = datas[0]
    price = float(datas[1])

    cekLender = DaftarUser.searchUser (id_line) # cek apakah lender sudah register
    cekDebtor = DaftarUser.searchUser (debtor) # cek apakah debtor sudah register
    if (len(cekLender) & len(cekDebtor)): # jika lender dan debtor sudah register
        id_lender = cekLender[0].id_user
        id_debtor = cekDebtor[0].id_user
        # insert utang ke database
        DaftarUtang(id_lender, id_debtor, komen, price, False).insert()

def detail(id_line, in_string):
    user_target = in_string.split(" ")[1]
    cekLender = DaftarUser.searchUser (id_line) # cek apakah lender sudah register
    cekDebtor = DaftarUser.searchUser (user_target) # cek apakah debtor sudah register
    lender = [cekLender[0].id_user, cekLender[0].username] # id, username
    debtor = [cekDebtor[0].id_user, cekDebtor[0].username] # id, username
    if (len(cekLender) & len(cekDebtor)): # jika lender dan debtor sudah register
        detailUtang = DaftarUtang.detail(lender[0], debtor[0])
    out_string = "Detail utang %s kepada %s:\n" % (debtor[1], lender[1])
    for row in detailUtang:
        if (row.id_lender == lender[0]): # lender benar
            out_string += "%.3f | %s\n" % (row.price, row.komen)
        else: # lender terbalik
            out_string += "%.3f | %s\n" % (-row.price, row.komen)
    print (out_string)

def total(id_line):
    cekLender = DaftarUser.searchUser (id_line) # cek apakah lender sudah register
    lender = [cekLender[0].id_user, cekLender[0].username] # id, username
    listUtang = DaftarUtang.detailForSum(cekLender[0].id_user)
    for ele in listUtang:
        print ("%d %d %.3f" % (ele.id_lender, ele.id_debtor, ele.price))
    

def getUser():
    return DaftarUser.query.all()

def getUtang():
    return DaftarUtang.query.all()
