
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

    @classmethod
    def searchUser(cls, stringToSearch):
        return cls.query.filter( # search id_line atau username sesuai stringToSearch
            (cls.id_line == stringToSearch) |
            (cls.username == stringToSearch)
        ).all()
    
    def __str__(self): # print database
        d = {}
        for column in self.__table__.columns:
            d[column.name] = str(getattr(self, column.name))
        return str(d)


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

    @classmethod
    def total(cls, stringToSearch):
        return cls.query.filter( # search id_line atau username sesuai stringToSearch
            (cls.id_line == stringToSearch) |
            (cls.username == stringToSearch)
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

    def __str__(self): # print database
        d = {}
        for column in self.__table__.columns:
            d[column.name] = str(getattr(self, column.name))
        return str(d)



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

def addUtang(id_line, msg):
    # nomor = Integer
    # id_lender = Integer
    # id_debtor = Integer
    # komen = String(30)
    # price = Float
    # lunas = Boolean 
    # add <username target> <komentar> <harga>

    datas = msg.split(" ")
    id_lender = 0
    id_debtor = 0
    komen = datas[2]
    price = float(datas[3])

    cekLender = DaftarUser.searchUser (id_line) # cek apakah lender sudah register
    cekDebtor = DaftarUser.searchUser (datas[1]) # cek apakah debtor sudah register
    if (len(cekLender) & len(cekDebtor)):
        id_lender = cekLender[0].id_user
        id_debtor = cekDebtor[0].id_user
        # insert utang ke database
        DaftarUtang(id_lender, id_debtor, komen, price, False).insert()

def total(id_line):
    cekUser = DaftarUser.searchUser (id_line) # cek apakah user sudah register
    if (len(cekUser)): # jika user sudah register



def getUser():
    return DaftarUser.query.all()

def getUtang():
    return DaftarUtang.query.all()
