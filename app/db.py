
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


class DaftarUtang(db.Model):
    __tablename__ = 'daftar_utang'
    id = db.Column(db.Integer, primary_key = True)
    u_id = db.Column(db.String(50))
    debtor = db.Column(db.String(100))
    price = db.Column(db.Float)

    def __init__(self, u_id, debtor, price):
        self.u_id = u_id
        self.debtor = debtor
        self.price = price

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def __str__(self):
        d = {}
        for column in self.__table__.columns:
            d[column.name] = str(getattr(self, column.name))
        return str(d)


def addUtang(user_id, msg):
    datas = msg.split(" ")
    debtor = datas[1]
    price = float(datas[2])
    
    DaftarUtang(user_id, debtor, price).insert()


def getUtang():
    return DaftarUtang.query.all()
