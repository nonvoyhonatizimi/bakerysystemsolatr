from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'foydalanuvchilar'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True, nullable=False)
    parol = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), default='operator')
    ism = db.Column(db.String(100))
    employee_id = db.Column(db.Integer, db.ForeignKey('xodimlar.id'), nullable=True)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    employee = db.relationship('Employee', backref=db.backref('user', uselist=False))

class Employee(db.Model):
    __tablename__ = 'xodimlar'
    id = db.Column(db.Integer, primary_key=True)
    ism = db.Column(db.String(100), nullable=False)
    lavozim = db.Column(db.String(50))
    telefon = db.Column(db.String(20))
    oylik = db.Column(db.Numeric(10, 2), default=0)
    status = db.Column(db.String(20), default='faol')
    ish_boshlanish = db.Column(db.Date, default=datetime.utcnow)
    # Kunlik ish haqqi stavkasi (bir dona/qop uchun)
    ish_haqqi_stavka = db.Column(db.Numeric(10, 2), default=0)

class Customer(db.Model):
    __tablename__ = 'mijozlar'
    id = db.Column(db.Integer, primary_key=True)
    nomi = db.Column(db.String(100), nullable=False)
    turi = db.Column(db.String(50))
    telefon = db.Column(db.String(20))
    manzil = db.Column(db.String(200))
    kredit_limit = db.Column(db.Numeric(10, 2), default=0)
    jami_qarz = db.Column(db.Numeric(10, 2), default=0)
    status = db.Column(db.String(20), default='faol')

class BreadType(db.Model):
    __tablename__ = 'non_turlari'
    id = db.Column(db.Integer, primary_key=True)
    nomi = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Dough(db.Model):
    __tablename__ = 'xamir'
    id = db.Column(db.Integer, primary_key=True)
    sana = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Vaqt bilan
    un_turi = db.Column(db.String(100), default='Oddiy un')  # Ishlatilgan un turi
    un_kg = db.Column(db.Integer, default=0)  # Hamir kg (ish haqqi va qoldiq uchun)
    xamir_soni = db.Column(db.Integer, default=0)
    xodim_id = db.Column(db.Integer, db.ForeignKey('xodimlar.id'))
    
    employee = db.relationship('Employee', backref='dough_records')

class BreadMaking(db.Model):
    __tablename__ = 'non_yasash'
    id = db.Column(db.Integer, primary_key=True)
    sana = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Vaqt bilan
    xamir_id = db.Column(db.Integer, db.ForeignKey('xamir.id'))
    hamir_kg = db.Column(db.Integer, default=0)  # Ishlatilgan hamir kg (ish haqqi uchun)
    non_turi = db.Column(db.String(100), default='Domboq')  # Non turi (Domboq, Achchiq, etc.)
    chiqqan_non = db.Column(db.Integer, default=0)
    sof_non = db.Column(db.Integer, default=0)
    brak = db.Column(db.Integer, default=0)
    xodim_id = db.Column(db.Integer, db.ForeignKey('xodimlar.id'))
    
    dough = db.relationship('Dough', backref='bread_making')
    employee = db.relationship('Employee', backref='bread_records')

class Oven(db.Model):
    __tablename__ = 'tandir'
    id = db.Column(db.Integer, primary_key=True)
    sana = db.Column(db.Date, nullable=False)
    un_kg = db.Column(db.Integer, default=0)  # Ishlatilgan un (kg)
    kirdi = db.Column(db.Integer, default=0)  # Kirgan non (dona)
    chiqdi = db.Column(db.Integer, default=0)  # Chiqqan non (dona)
    brak = db.Column(db.Integer, default=0)  # Brak non (dona)
    xodim_id = db.Column(db.Integer, db.ForeignKey('xodimlar.id'))
    
    employee = db.relationship('Employee', backref='oven_records')

class Sale(db.Model):
    __tablename__ = 'sotuvlar'
    id = db.Column(db.Integer, primary_key=True)
    sana = db.Column(db.Date, nullable=False)
    mijoz_id = db.Column(db.Integer, db.ForeignKey('mijozlar.id'))
    non_turi = db.Column(db.String(50))
    miqdor = db.Column(db.Integer)
    narx_dona = db.Column(db.Numeric(10, 2))
    jami_summa = db.Column(db.Numeric(10, 2))
    tolandi = db.Column(db.Numeric(10, 2), default=0)
    qoldiq_qarz = db.Column(db.Numeric(10, 2), default=0)
    xodim_id = db.Column(db.Integer, db.ForeignKey('xodimlar.id'))
    
    customer = db.relationship('Customer', backref='sales')
    employee = db.relationship('Employee', backref='sales')

class Expense(db.Model):
    __tablename__ = 'xarajatlar'
    id = db.Column(db.Integer, primary_key=True)
    sana = db.Column(db.Date, nullable=False)
    turi = db.Column(db.String(50))
    summa = db.Column(db.Numeric(10, 2))
    izoh = db.Column(db.String(200))
    xodim_id = db.Column(db.Integer, db.ForeignKey('xodimlar.id'))
    
    employee = db.relationship('Employee', backref='expenses')

class Cash(db.Model):
    __tablename__ = 'kassa'
    id = db.Column(db.Integer, primary_key=True)
    sana = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Vaqt bilan
    kirim = db.Column(db.Numeric(10, 2), default=0)
    chiqim = db.Column(db.Numeric(10, 2), default=0)
    balans = db.Column(db.Numeric(10, 2), default=0)
    izoh = db.Column(db.String(200))
    turi = db.Column(db.String(50))  # Sotuv, Xarajat, Ish haqqi

class Log(db.Model):
    __tablename__ = 'jurnal'
    id = db.Column(db.Integer, primary_key=True)
    sana = db.Column(db.DateTime, default=datetime.utcnow)
    foydalanuvchi = db.Column(db.String(50))
    harakat = db.Column(db.String(100))
    maumot = db.Column(db.String(200))

class UnQoldiq(db.Model):
    __tablename__ = 'un_qoldiq'
    id = db.Column(db.Integer, primary_key=True)
    sana = db.Column(db.DateTime, default=datetime.utcnow)
    un_turi = db.Column(db.String(100), default='Oddiy un')  # Un turi
    qop_soni = db.Column(db.Integer, default=0)
    izoh = db.Column(db.String(200))
    xodim_id = db.Column(db.Integer, db.ForeignKey('xodimlar.id'))
    
    employee = db.relationship('Employee', backref='un_qoldiq_records')

class UnTuri(db.Model):
    __tablename__ = 'un_turlari'
    id = db.Column(db.Integer, primary_key=True)
    nomi = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
