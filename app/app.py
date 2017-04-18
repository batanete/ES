#!/usr/bin/env python3
import datetime
import logging
import random
import string

import connexion
from connexion import NoContent
from flask import render_template,session
from hashlib import sha1
from base64 import b64encode
import crud

sessions={}


#returns a password's hash according to sha1
def encrypt_password(key):

    m=sha1()
    m.update(key)
    return b64encode(m.digest())
    #return key

#generates a random token for a user session.
def gen_token(size=20):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(size))

#verifies if token is correct for the given user
def verify_token(username,token):
    return True
    """
    if username not in sessions.keys():
        return False

    return sessions[username]==token
    """

#returns html page for creating account
def create_account_menu():
    return render_template('register_page.html')

#returns the login screen
def login_menu():
    return render_template("login_page.html",loginerror="false")

#TODOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOoo
def main_menu():
    return render_template('main_page.html')

#method for creating a new account.returns code 200 in case of success and 403 in case account exists
def create_account(user):

    print(user)

    username=str(user['email'])
    name=str(user['name'])
    password=str(user['password'])

    logging.info("attempting to create account "+username)
    if crud.create_account(name,username,encrypt_password(password)):
        logging.info("successfully created account "+username)
        return NoContent,200
    else:
        logging.warning("failed to create account "+username+".account already exists.")
        return NoContent,403


#change account info
def edit_account(edituserinfo):
    username=edituserinfo['username']
    newemail=edituserinfo['newemail']
    newname=edituserinfo['newname']
    newpassword=edituserinfo['newpassword']

    if crud.edit_account(username,newemail,encrypt_password(newpassword),newname):
        logging.info("successfully edited account "+username)
        return NoContent,200
    else:
        logging.warning("failed to edit account "+username+".")
        return NoContent,403

#method for logging into an account. creates a new user session when successful.
def login(username,password):
    if not crud.verify_account(username,encrypt_password(password)):
        logging.warning('login failed on account '+username)
        return render_template("login_page.html",loginerror="true"),403
    else:
        token=gen_token()
        sessions[username]=token
        logging.info('login successful on account '+username)
        return render_template('menu.html'),200

#method for deleting a song uploaded by the user
def delete_song(user_token,song_id):
    username=user_token['username']
    token=user_token['token']

    sessions[username]=token

    print(username,token)

    if not verify_token(username,token):
        logging.warning('user attempted forbidden request')
        return NoContent,403


    res=crud.delete_song(username,song_id)
    if res is None:
        return NoContent,404
    elif res:
        return NoContent,204
    else:
        return NoContent,403

#method for disowning a song uploaded by the user
def disown_song(user_token,song_id):
    username=user_token['username']
    token=user_token['token']

    sessions[username]=token

    if not verify_token(username,token):
        logging.warning('user attempted forbidden request')
        return NoContent,403


    res=crud.disown_song(username,song_id)
    if res is None:
        return NoContent,404
    elif res:
        return NoContent,204
    else:
        return NoContent,403


#adds a song to playlist the user owns.
def add_music_to_playlist(user_token,song_id,playlistid):
    username=user_token['username']
    token=user_token['token']

    sessions[username]=token

    if not verify_token(username,token):
        logging.warning('user attempted forbidden request')
        return NoContent,403


    res=crud.add_music_to_playlist(username,songid,playlistid)
    if res is None:
        return NoContent,404
    elif not res:
        return NoContent, 403
    else:
        return NoContent,204

def remove_music_from_playlist(user_token, song_id, playlist_id):
    username=user_token['username']
    token=user_token['token']

    sessions[username]=token

    if not verify_token(username,token):
        logging.warning('user attempted forbidden request')
        return NoContent,403

    if crud.remove_music_from_playlist(playlist_id, song_id, username):
        logging.info("successfully deleted song")
        return NoContent, 200
    else:
        logging.warning("failed to delete song "+str(song_id)+".song not found")
        return NoContent, 404



#returns list of songs that follow a certain
def search_song(username,token,criteria):

    sessions[username]=token

    if not verify_token(username,token):
        logging.warning('user attempted forbidden request')
        return NoContent,403

    res=crud.search_song(criteria)

    return res,200

###
###
#creates a new playlist
def create_playlist(user_token, playlist_name):
    username=user_token['username']
    token=user_token['token']
    sessions[username]=token

    if not verify_token(username,token):
        logging.warning('user attempted forbidden request')
        return NoContent,403


    logging.info("attempting to create playlist " +playlist_name)
    #username = "teste"
    if crud.create_playlist(playlist_name, username):
        logging.info("successfully created playlist "+playlist_name)
        return NoContent, 200
    else:
        logging.warning("failed to create playlist "+playlist_name+".playlist already exists")
        return NoContent, 400

#edit the name of one playlist
def edit_playlist_name(user_token, playlist_id, new_name):
    username=user_token['username']
    token=user_token['token']
    sessions[username]=token

    if not verify_token(username,token):
        logging.warning('user attempted forbidden request')
        return NoContent,403

    logging.info("attempting to edit playlist name" +str(playlist_id) +" to " +new_name)
    username = "teste"
    if crud.edit_playlist_name(playlist_id, new_name, username):
        logging.info("successfully edited playlist "+str(playlist_id)+" to "+new_name)
        return NoContent, 200
    else:
        logging.warning("failed to edit playlist "+str(playlist_id)+".playlist doens't exists")
        return NoContent, 404

#list playlists created by user
def list_playlists(username,order,token):
    print("username:" +username+" order: "+order+" token: "+token)
    if not verify_token(username,token):
        logging.warning('user attempted forbidden request')
        return NoContent,403


    return crud.list_playlists(username,order),200

#list the songs of a specific playlist !!!!
def list_playlist_songs(user_token, playlist_id):
    username=user_token['username']
    token=user_token['token']
    sessions[username]=token

    if not verify_token(username,token):
        logging.warning('user attempted forbidden request')
        return NoContent,403


    logging.info("attempting to list songs from playlist" +playlist_id)
    username = "teste"
    if crud.list_playlist_songs(playlist_id, username) is not None:
        logging.info("successfully listed playlist songs "+playlist_id)
        return NoCOntent, 200
    else:
        logging.warning("failed to list playlist songs "+playlist_id)
        return NoContent, 404

#delete a playlist
def delete_playlist(user_token, playlist_name):
    username=user_token['username']
    token=user_token['token']
    sessions[username]=token

    if not verify_token(username,token):
        logging.warning('user attempted forbidden request')
        return NoContent,403



    logging.info("attempting to delete a playlist" +playlist_id)
    username = "teste"
    if crud.list_playlist_songs(playlist_id, username):
        logging.info("successfully deleted playlist "+playlist_id)
        return NoContent, 200
    else:
        logging.warning("failed to delete playlist "+playlist_id)
        return NoContent, 404

#edit a song
def edit_song(user_token, id_song, song_title, song_artist, song_year):
    username=user_token['username']
    token=user_token['token']
    sessions[username]=token

    if not verify_token(username,token):
        logging.warning('user attempted forbidden request')
        return NoContent,403

    logging.info("attempting to edit song" +str(id_song))
    username = "teste"
    if crud.edit_song(id_song, song_title, song_artist, song_year, username):
        logging.info("successfully edited song "+str(id_song))
        return NoContent, 200
    else:
        logging.warning("failed to edit song "+str(id_song))
        return NoContent, 404

#list songs
def list_songs():
    username=user_token['username']
    token=user_token['token']
    sessions[username]=token

    if not verify_token(username,token):
        logging.warning('user attempted forbidden request')
        return NoContent,403


    logging.info("attempting to list songs")
    songs=crud.list_songs()
    if songs is not None:
        logging.info("successfully listed songs ")
        return songs, 200
    else:
        logging.warning("no songs found ")
        return NoContent, 404



if __name__=='__main__':
    logging.basicConfig(level=logging.INFO)
    session=crud.get_session()

    app = connexion.App(__name__, specification_dir='swagger/')
    app.add_api('swagger.yaml')

    #app.app.secret_key('cenas lixadas')
    app.run(port=8000)
