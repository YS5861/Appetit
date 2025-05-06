import os
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Table, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

# Veritabanı oluşturulacak dosya
veritabani_adi = "Appetit.db"

# Always create engine and session
engine = create_engine(f"sqlite:///{veritabani_adi}")
Base = declarative_base()
Session = sessionmaker(bind=engine)

# Çoktan çoğa ilişki için yardımcı tablo
yemek_malzeme = Table(
    'yemek_malzeme', Base.metadata,
    Column('yemek_id', ForeignKey('yemek.id'), primary_key=True),
    Column('malzeme_id', ForeignKey('malzeme.id'), primary_key=True)
)

class Kullanici(Base):
    __tablename__ = 'kullanici'
    id = Column(Integer, primary_key=True)
    isim = Column(String, nullable=False)
    yemekler = relationship("GecmisYemek", back_populates="kullanici")

class Malzeme(Base):
    __tablename__ = 'malzeme'
    id = Column(Integer, primary_key=True)
    ad = Column(String, unique=True, nullable=False)

class Yemek(Base):
    __tablename__ = 'yemek'
    id = Column(Integer, primary_key=True)
    ad = Column(String, nullable=False)
    tarif = Column(Text, nullable=False)
    malzemeler = relationship("Malzeme", secondary=yemek_malzeme, backref="yemekler")
    kalori = Column(Text, nullable=False)
    karbonhidrat = Column(Text, nullable=False)
    protein = Column(Text, nullable=False)
    yag = Column(Text, nullable=False)
    GHG = Column(Text, nullable=False)

class GecmisYemek(Base):
    __tablename__ = 'gecmis_yemek'
    id = Column(Integer, primary_key=True)
    kullanici_id = Column(Integer, ForeignKey('kullanici.id'))
    yemek_id = Column(Integer, ForeignKey('yemek.id'))
    tarih = Column(DateTime, default=datetime.utcnow)
    kullanici = relationship("Kullanici", back_populates="yemekler")
    yemek = relationship("Yemek")

# Only create tables if database doesn't exist
if not os.path.exists(veritabani_adi):
    # Tabloları veritabanına oluştur
    Base.metadata.create_all(engine)
    print("Veritabanı oluşturuldu.")
else:
    print("Veritabanı zaten mevcut.")