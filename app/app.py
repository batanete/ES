#!/usr/bin/env python3
import datetime
import logging
import random
import string
import os
import boto3
import connexion
from connexion import NoContent
from flask import Flask,render_template,request,make_response,session,escape,redirect,url_for
from hashlib import sha1
from base64 import b64encode
import crud
from datetime import timedelta


UPLOAD_FOLDER='./'


#returns a password's hash according to sha1
def encrypt_password(key):

    m=sha1()
    m.update(key.encode('utf-8'))
    return b64encode(m.digest())

#generates a random token for a user session.
def gen_token(size=20):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(size))

#verifies if token is correct for the given user
def verify_token(username,token):
    return True

#returns username of logged in user, or None
def verify_session():
    if 'username' in session.keys():
        return session['username']
    else:
        return None

#returns html page for creating account
def create_account_menu():
    return render_template('register_page.html')

#returns the login screen
def login_menu():
    username=verify_session()
    if username is not None:
        return render_template('menu.html',username=session['username'],name=session['name'],id=str(session['id']))

    else:
        return render_template("login_page.html",loginerror="false")

#TODOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOoo
def main_menu():
    username=verify_session()

    if username is None:
        return render_template("login_page.html",loginerror="true")

    return render_template('menu.html',username=session['username'],name=session['name'],id=str(session['id']))

#method for creating a new account.returns code 200 in case of success and 403 in case account exists
def create_account(user):

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
    username=verify_session()
    if username is None:
        return NoContent,403

    print(edituserinfo)
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
    acc=crud.verify_account(username,encrypt_password(password))

    if acc is None:
        logging.warning('login failed on account '+username)
        return render_template("login_page.html",loginerror="true"),403
    else:
        token=gen_token()
        session['username']=acc['email']
        session['name']=acc['name']
        session['id']=acc['id']
        session['token']=token
        logging.info('login successful on account '+username)
        return render_template('menu.html',username=session['username'],name=session['name'],id=str(session['id'])),200

def logout():
    print("logout")
    print("ses: "+session['username'])
    session.pop('username')
    session.pop('token')

    return render_template('login_page.html'), 200


#method for uploading a new song to database
def upload_song(songfile,title,album,artist,year,path):
    username=verify_session()

    if username is None:
        return NoContent,403


    if not crud.add_song(title,album,artist,year,path,username):
        return NoContent,403

    #PARA A AMAZON FICA DIFERENTE ESTA PARTE
    """
    try:
        os.stat(UPLOAD_FOLDER+path)
    except:
        os.mkdir(UPLOAD_FOLDER+path)
    songfile.save(UPLOAD_FOLDER+path+'/'+str(songfile.filename))
    """
    #################
    s3 = boto3.resource('s3', aws_access_key_id = AWS_KEY_ID, aws_secret_access_key = AWS_KEY)
    s3.Bucket('es2bata').put_object(Key = path+'/'+songfile.filename, Body = songfile)

    return NoContent,204



#method for deleting a song uploaded by the user
def delete_song(user_token,song_id):
    username=verify_session()

    if username is None:
        return NoContent,403

    res=crud.delete_song(username,song_id)
    if res is None:
        return NoContent,404
    elif res:
        return NoContent,204
    else:
        return NoContent,403

#method for disowning a song uploaded by the user
def disown_song(song_id):

    id=song_id['id']
    username=verify_session()

    if username is None:
        return NoContent,403


    res=crud.disown_song(username,id)
    if res is None:
        return NoContent,404
    elif res:
        return NoContent,204
    else:
        return NoContent,403


#adds a song to playlist the user owns.
def add_music_to_playlist(playlist_song):
    username=verify_session()

    if username is None:
        return NoContent,403
    song_id=playlist_song['song_id']
    playlist_id=playlist_song['playlist_id']

    res=crud.add_music_to_playlist(username,song_id,playlist_id)
    if res is None:
        return NoContent,404
    elif not res:
        return NoContent, 403
    else:
        return NoContent,204

def remove_music_from_playlist(removed_song):
    username=verify_session()

    if username is None:
        return NoContent,403

    song_id=removed_song['song_id']
    playlist_id=removed_song['playlist_id']

    print("song_id: "+str(song_id))
    print("playlist_id: "+str(playlist_id))

    if crud.remove_music_from_playlist(username, song_id, playlist_id):
        logging.info("successfully deleted song")
        return NoContent, 204
    else:
        logging.warning("failed to delete song "+str(song_id)+".song not found")
        return NoContent, 404



#returns list of songs that follow a certain
def search_song(username,token,criteria):

    username=verify_session()

    if username is None:
        return NoContent,403

    res=crud.search_song(criteria)

    return res,200

###
###
#creates a new playlist
def create_playlist(playlist_name):
    print("name: ", playlist_name)
    username=verify_session()

    if username is None:
        return NoContent,403

    logging.info("attempting to create playlist " ,playlist_name)
    #username = "teste"
    if crud.create_playlist(playlist_name['name'], username):
        logging.info("successfully created playlist ",playlist_name)
        return render_template('menu.html',username=session['username'],name=session['name'],id=str(session['id']))
    else:
        logging.warning("failed to create playlist")
        return NoContent, 400

#edit the name of one playlist
def edit_playlist_name(newplaylistname):
    username=verify_session()

    if username is None:
        return NoContent,403

    playlist_id=newplaylistname['id']
    new_name=newplaylistname['newname']
    logging.info("attempting to edit playlist name" +str(playlist_id) +" to " +new_name)



    if crud.edit_playlist_name(playlist_id, new_name, username):
        logging.info("successfully edited playlist "+str(playlist_id)+" to "+new_name)
        return NoContent, 200
    else:
        logging.warning("failed to edit playlist "+str(playlist_id)+".playlist doens't exists")
        return NoContent, 404

#list playlists created by user
def list_playlists(order):
    username=verify_session()

    if username is None:
        return NoContent,403

    #print("username:" +username+" order: "+order+" token: "+token)


    return crud.list_playlists(username,order),200

#list the songs of a specific playlist !!!!
def list_playlist_songs(playlist_id):
    username=verify_session()

    if username is None:
        return NoContent,403


    logging.info("attempting to list songs from playlist" +str(playlist_id))
    aux=crud.list_playlist_songs(playlist_id, username)
    if aux is not None:
        logging.info("successfully listed playlist songs "+str(playlist_id))
        return aux, 200
    else:
        logging.warning("failed to list playlist songs "+str(playlist_id))
        return NoContent, 404

#delete a playlist
def delete_playlist(playlist_id):
    username=verify_session()
    print(playlist_id['id'])
    if username is None:
        return NoContent,403

    pl_id = playlist_id['id']
    logging.info("attempting to delete a playlist" +str(pl_id))

    if crud.delete_playlist(pl_id, username):
        logging.info("successfully deleted playlist "+str(pl_id))
        return NoContent, 204
    else:
        logging.warning("failed to delete playlist "+str(pl_id))
        return NoContent, 404

#edit a song
def edit_song(newsongdata):
    print('entra no edit')
    username=verify_session()

    if username is None:
        return NoContent,403

    id=newsongdata['id']
    title=newsongdata['newtitle']
    artist=newsongdata['newartist']
    year=newsongdata['newyear']
    album=newsongdata['newalbum']


    logging.info("attempting to edit song" +str(id))
    if crud.edit_song(id, title, artist, year,album, username):
        logging.info("successfully edited song "+str(id))
        return NoContent, 200
    else:
        logging.warning("failed to edit song "+str(id))
        return NoContent, 404

#list songs
def list_songs():
    username=verify_session()

    if username is None:
        return NoContent,403

    logging.info("attempting to list songs")
    songs=crud.list_songs()
    if songs is not None:
        logging.info("successfully listed songs ")
        return songs, 200
    else:
        logging.warning("no songs found ")
        return NoContent, 404


#read aws keys from file
def get_aws_keys():
    global AWS_KEY,AWS_KEY_ID
    with open('keys','r') as f:
        lines=f.readlines()
        AWS_KEY_ID=lines[0].replace('\n','')
        AWS_KEY=lines[1].replace('\n','')
