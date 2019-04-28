from flask import request, jsonify
from flask_restful import Resource
from config import mysql
from .helpers import _authenticate_user, _get_tag_id
from base64 import b64decode
import os
import datetime
import json


class PhotoTag(Resource):
    def post(self):
        try:
            user_id = _authenticate_user(request)
            photo_id = request.json.get('photoId')
            tag_name = request.json.get('tagName').lower()
        except Exception as err:
            return jsonify({'success': False, 'error': 'incorrectOrExpiredAuthToken', 'tagId': ''})

        tag_id = None
        try:
            cur = mysql.connection.cursor()

            # check if tag already exists
            tag_id= _get_tag_id(tag_name)
            if tag_id:
                cur.execute("INSERT INTO Photo_Tag(photoID, tagID) VALUES(%s, %s)", (photo_id, tag_id))
                cur.execute("UPDATE Tag SET count=count+1 WHERE tagID=%s", (tag_id,))
            # if not, create an entry for it
            else:
                cur.execute("INSERT INTO Tag(name, count) VALUES(%s, %s)", (tag_name, 1))
                tag_id = cur.lastrowid
                cur.execute("INSERT INTO Photo_Tag(photoID, tagID) VALUES(%s, %s)", (photo_id, tag_id))

            mysql.connection.commit()
            cur.close()
        except Exception as err:
            print(err)
            return jsonify({'success': False, 'error': 'databaseError', 'tagId': tag_id})


        return jsonify({'success': True, 'error': '', 'tagId': tag_id})


    def get(self):
        try:
            user_id = _authenticate_user(request)
            photo_id = request.headers.get('PhotoId')
        except Exception as err:
            return jsonify({'success': False, 'error': 'incorrectOrExpiredAuthToken', 'photoTags': ''})
        
        tags = None
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT name, tagID FROM Tag WHERE tagID in (SELECT tagID FROM Photo_Tag WHERE photoID=%s)", (int(photo_id),))
            tags = cur.fetchall()
            cur.close()
        except Exception as err:
            print(err)
            return jsonify({'success': False, 'error': 'databaseError', 'photoTags': tags})

        return jsonify({'success': True, 'error': '', 'photoTags': tags})


    def delete(self):
        try:
            user_id = _authenticate_user(request)
            photo_id = request.headers.get('PhotoId')
            tag_id = request.headers.get('TagId')
        except Exception as err:
            return jsonify({'success': False, 'error': 'incorrectOrExpiredAuthToken'})
        
        try:
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM Photo_Tag WHERE photoID=%s AND tagID=%s", (photo_id, tag_id))
            cur.execute("UPDATE Tag SET count=count-1 WHERE tagID=%s", (tag_id,))

            # delete tag from Tag table if count == 0
            cur.execute("SELECT count FROM Tag WHERE tagID=%s", (tag_id,))
            if (cur.fetchone()['count'] < 1):
                cur.execute("DELETE FROM Tag WHERE tagID=%s", (tag_id,))

            mysql.connection.commit()
            cur.close()
        except Exception as err:
            print(err)
            return jsonify({'success': False, 'error': 'databaseError'})
 
        return jsonify({'success': True, 'error': ''})