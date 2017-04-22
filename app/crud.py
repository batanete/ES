import os
import sys
from entities import *
from sqlalchemy import or_
from datetime import datetime
session=None
engine=None

#create all tables on db
def create_tables():

    # Create all tables in the engine. This is equivalent to "Create Table"
    # statements in raw SQL.
    Base.metadata.create_all(engine)
#returns a session(for use on the business layer)
def get_session():
    global session,engine
    # Create an engine that stores data in the local directory's
    # sqlalchemy_example.db file.
    with open("bd_url", "r") as f:
        bd_url = f.read()


    engine = create_engine(bd_url)
    DBSession = sessionmaker(bind=engine)
    # A DBSession() instance establishes all conversations with the database
    # and represents a "staging zone" for all the objects loaded into the
    # database session object. Any change made against the objects in the
    # session won't be persisted into the database until you call
    # session.commit(). If you're not happy about the changes, you can
    # revert all of them back to the last commit by calling
    # session.rollback()
    session=DBSession()
    return session

#attempts to create a new account.returns false in case account already exists.
def create_account(name,email,password):
    acc=session.query(User).filter_by(email=email).first()

    #account already exists, return False
    if acc is not None:
        return False
    else:
        session.add(User(name=name,email=email,password=password))
        session.commit()
        return True

#edits a user's account
def edit_account(username,newemail,newpassword,newname):
    acc_user=session.query(User).filter_by(email=username).first()

    if acc_user is None:
        return False

    try:
        acc_user.email=newemail
        acc_user.password=newpassword
        acc_user.name=newname
        session.commit()
        return True
    except Exception as e:
        print(e)
        session.rollback()
        return False

#list a given user's playlists
def list_playlists(username,order):
    acc_user=session.query(User).filter_by(email=username).first()

    if acc_user is None:
        return None

    if order=='an':
        playlists=session.query(Playlist).filter_by(owner=acc_user).order_by(Playlist.name).all()
    elif order=='dn':
        playlists=session.query(Playlist).filter_by(owner=acc_user).order_by(Playlist.name.desc()).all()
    elif order=='ad':
        playlists=session.query(Playlist).filter_by(owner=acc_user).order_by(Playlist.creation_date).all()
    else:
        playlists=session.query(Playlist).filter_by(owner=acc_user).order_by(Playlist.creation_date.desc()).all()
    res=[]
    for playlist in playlists:
        res.append(playlist.to_json())
    return res

#returns whether the given user credentials are correct
def verify_account(username,password):
    acc=session.query(User).filter_by(email=username,password=password).first()

    if acc is None:
        return None
    else:
        return acc.to_json()

#add a newly uploaded song to database
def add_song(title,album,artist,year,path,uploader_email):
    acc_user=session.query(User).filter_by(email=uploader_email).first()

    if acc_user is None:
        return False
    print('chega')
    try:
        session.add(Song(title=title,album=album,artist=artist,year=year,path=path,uploader=acc_user))
        session.commit()
        return True
    except Exception as e:
        print(e)
        session.rollback()
        return False


#deletes a song from database, if the given user is the owner
def delete_song(username,songid):
    acc=session.query(User).filter_by(email=username).first()

    if acc is None:
        return False

    s=session.query(Song).get(songid)

    #song doesn't exist
    if s is None:
        return None

    #user is not the owner
    if s.uploader!=acc:
        return False

    session.delete(s)
    session.commit()
    return True

#user disowns, if the given user is the owner
def disown_song(username,songid):
    acc=session.query(User).filter_by(email=username).first()

    if acc is None:
        return False

    s=session.query(Song).get(songid)
    #song doesn't exist
    if s is None:
        return None

    #user is not the owner
    if s.uploader!=acc:
        return False

    s.uploader=None
    session.commit()
    return True

#returns list of songs that follow a certain criteria either on title or artist
def search_song(criteria):
    songs=session.query(Song).filter(or_(Song.title.like('%'+criteria+'%'),Song.artist.like('%'+criteria+'%'))).all()

    res=[]
    for song in songs:
        res.append(song.to_json())

    return res

#adds a song to playlist the user owns.
def add_music_to_playlist(username,songid,playlistid):
    acc=session.query(User).filter_by(email=username).first()
    song=session.query(Song).get(songid)
    pl=session.query(Playlist).get(playlistid)

    #one of the three doesn't exist
    if acc is None or song is None or pl is None:
        return None

    #user is not the owner of the playlist
    if pl.owner!=acc:
        return False

    #music already in playlist
    if song in pl.songs:
        return False


    pl.songs.append(song)
    session.commit()
    return True

def remove_music_from_playlist(username, songid, playlistid):
    acc=session.query(User).filter_by(email=username).first()
    song=session.query(Song).get(songid)
    pl=session.query(Playlist).get(playlistid)
    print(songid)
    print(playlistid)
    print("------")
    print(acc)
    print(song)
    print(pl)
    #one of the three doesn't exist
    if acc is None or song is None or pl is None:
        return None

    #user is not the owner of the playlist
    if pl.owner!=acc:
        return False

    pl.songs.remove(song)
    session.commit()
    return True


###
#attempts to create a new playlist for a specific user
def create_playlist(playlist_name, username):
    acc_user=session.query(User).filter_by(email=username).first()

    if acc_user is None:
        return False
    else:
        #owd_id = acc_user.id
        get_playlist=session.query(Playlist).filter_by(owner=acc_user, name=playlist_name).first()

        if get_playlist is not None:
            return False
        else:
            session.add(Playlist(name=playlist_name, owner=acc_user, owner_id=acc_user.id,creation_date=datetime.now()))
            session.commit()
            return True

def edit_playlist_name(playlist_id, new_name, username):
    acc_user=session.query(User).filter_by(email=username).first()

    if acc_user is None:
        return False
    else:
        #owd_id = acc_user.id
        get_playlist=session.query(Playlist).get(playlist_id)

        if get_playlist is None:
            return False
        else:
            get_playlist.name = new_name
            session.commit()
            return True

def list_playlist_songs(playlist_id, username):
    acc_user=session.query(User).filter_by(email=username).first()

    if acc_user is None:
        return None
    else:
        get_playlist=session.query(Playlist).get(playlist_id)
        if get_playlist is None:
            return None
        else:
            songs_array = []
            for i in get_playlist.songs:
                songs_array.append(i.to_json())

            return songs_array

def delete_playlist(playlist_id,username):
    acc_user=session.query(User).filter_by(email=username).first()

    if acc_user is None:
        return False
    else:
        #owd_id = acc_user.id
        get_playlist=session.query(Playlist).get(playlist_id)

        if get_playlist is None:
            return False
        else:
            session.delete(get_playlist)
            session.commit()
            return True

def edit_song(id_song, song_title, song_artist, song_year,song_album, username):

    acc_user=session.query(User).filter_by(email=username).first()
    if acc_user is None:
        return False
    else:
        #owd_id = acc_user.id
        print('chega aqui')
        get_song=session.query(Song).filter_by(uploader=acc_user, id=id_song).first()

        if get_song is None:
            return False
        else:
            try:
                get_song.title = song_title
                get_song.artist = song_artist
                get_song.year = song_year
                get_song.album=song_album
                session.commit()
                return True
            except Exception as e:
                session.rollback()
                print(e)
                return False

def list_songs():
    songs = session.query(Song).all()

    if len(songs) == 0:
        return None

    else:
        songs_array = []
        for i in songs:
            songs_array.append(i.to_json)

        return songs_array




get_session()
create_tables()
