import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__='user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250),nullable=False)
    email = Column(String(250),nullable=False)
    picture = Column(String(250))

class Catalog(Base):
    __tablename__='catalog'
    category = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    @property
    def serialize(self):
        return{
            'category': self.category,
            'id': self.id
        }

class CatalogItem(Base):
    __tablename__='catalog_item'
    title = Column(String(250), nullable=False)
    description = Column(String(500))
    item_id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('catalog.id'))
    catalog = relationship(Catalog)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)


# We added this serialize function to be able to send JSON objects in a
# serializable format
    @property
    def serialize(self):

        return {

            'title': self.title,
            'description': self.description,
            'item_id': self.item_id,
            'category_id': self.category_id,
            #'catalog': self.catalog,
        }

############insert at end of file ##################
#engine =create_engine('sqlite:///catalogdatabase.db)
engine =create_engine('sqlite:///catalogdatabasewithusers.db')
Base.metadata.create_all(engine)
