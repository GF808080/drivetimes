#basic setup for the sqlalchemy database

from sqlalchemy import create_engine, MetaData
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json
with open('/home/sentinel/HouseSearchDriveTimes/config.json', 'r') as infile:
    config = json.loads(infile.read())
dbloc = config['dbloc']

engine = create_engine(dbloc,  echo=True)
connection = engine.connect()
Base = declarative_base()
meta = MetaData()
session = sessionmaker(bind=engine)
session.configure(bind=engine)
s = session()

class houses(Base):

    __tablename__ = "houses"

    id = Column(Integer, primary_key=True)
    address = Column(String)  


    def __init__(self, name):

        self.name = name    

class drivetimes(Base):
    __tablename__ = "drivetimes"
    id = Column(Integer, primary_key=True)
    start = Column(String)
    dest = Column(String)
    starttime = Column(DateTime)
    drivetime = Column(Integer)
    
    def __init__(self, name):

        self.name = name  

class offices(Base):
    __tablename__ = "offices"

    id = Column(Integer, primary_key=True)
    address = Column(String)
    person = Column(String)


    def __init__(self, name):

        self.name = name    
##### CREATE STEP---only need to do this once
#Base.metadata.create_all(engine)
### 
Houses = Table('houses', meta, autoload=True, autoload_with = engine)
Offices = Table('offices', meta, autoload=True, autoload_with = engine)
DriveTimes = Table('drivetimes', meta, autoload=True, autoload_with=engine)
##refreshes houses table
#import pandas as pd
#aframe = pd.read_csv('houseAddresses.csv',dtype=str)
#for h in aframe.houses.values:
#    print(str(h))
#    ins = Houses.insert().values(address=str(h))
#    connection.execute(ins)
###


if __name__ == "__main__":
    session = sessionmaker(bind=engine)
    s = session()
    connection.execute(Offices.insert().values(address = 'Washington, DC 20007', person='Stacy'))

    myhouses =connection.execute(Houses.select())
    for i in myhouses:
        print(i)