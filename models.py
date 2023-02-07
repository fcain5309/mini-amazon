from sqlalchemy import Column, Integer, String
from databases import database
from database import Base

class Car(Base):
    __tablename__ = 'cars'
    id = Column(Integer, primary_key=True)
    make = Column(String(20), unique=True)
    model = Column(String(20), unique=False)
    color = Column(String(20), unique=False)
    year = Column(String(4), unique=False)

    def __init__(self, make=None, model=None, color=None, year=None):
        self.make = make
        self.model = model
        self.color = color
        self.year = year

    def __repr__(self):
        return '<Car %r>' % (self.model)