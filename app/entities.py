import os
import sys
import json
from sqlalchemy import Column, ForeignKey, Integer, String, Table,desc,Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship,sessionmaker
from sqlalchemy import create_engine


"""
This file contains all the class declarations for the entities.
"""


Base = declarative_base()


#defines the table for the many to many association between playlists and songs
association_songs_playlists = Table('songs_playlists', Base.metadata,
    Column('song_id', Integer, ForeignKey('songs.id')),
    Column('playlist_id', Integer, ForeignKey('playlists.id'))
)


class User(Base):
    __tablename__ = 'users'
    # Here we define columns for the table user
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False,unique=True)
    password = Column(String(250), nullable=False)

    playlists = relationship("Playlist", back_populates="owner")
    songs = relationship("Song", back_populates="uploader")



    def verify_account(self,email,password):
        """returns true if login is successful"""
        return self.email==email and self.password==password

    def __repr__(self):
        return 'name:'+self.name+';email:'+self.email

    def to_json(self):
        return {'id':self.id,'name':self.name,'email':self.email}


class Playlist(Base):
    __tablename__ = 'playlists'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

    owner_id = Column(Integer, ForeignKey('users.id'))

    creation_date=Column(Date,nullable=False)

    owner = relationship("User", back_populates="playlists")


    songs=relationship("Song",
                    secondary=association_songs_playlists,
                    back_populates="playlists")


class Song(Base):
    __tablename__='songs'

    id = Column(Integer, primary_key=True)

    uploader_id = Column(Integer, ForeignKey('users.id'))
    uploader = relationship("User", back_populates="songs")

    title = Column(String(50), nullable=False)
    artist=Column(String(50), nullable=False)
    year=Column(Integer,nullable=False)
    path=Column(String(50), nullable=False)

    playlists = relationship(
        "Playlist",
        secondary=association_songs_playlists,
        back_populates="songs")

    def to_json(self):
        return {'id':self.id, 'title':self.title, 'artist':self.artist, 'year':self.year}
