from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

#Base = declarative_base()
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class City(Base):
    __tablename__ = "city"
    idCity = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(25), nullable=False, unique=True)
    houses = relationship("House", back_populates="city")

class Type(Base):
    __tablename__ = "type"
    idType = Column(Integer, primary_key=True, unique=True)
    name = Column(String(25), nullable=False, unique=True)
    houses = relationship("House", back_populates="type")

class House(Base):
    __tablename__ = "house"
    idHouse = Column(Integer, primary_key=True, unique=True)
    idCity = Column(Integer, ForeignKey(City.idCity), nullable=False)
    idType = Column(Integer, ForeignKey(Type.idType), nullable=False)
    surface = Column(Float, nullable=False)
    rooms = Column(Integer, nullable=False)
    bedrooms = Column(Integer, nullable=False)
    bathrooms = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    yearBuilt = Column(Integer, nullable=False)
    
    city = relationship("City", back_populates="houses")
    #rel_idCity_house = relationship("City")
    type = relationship("Type", back_populates="houses")
