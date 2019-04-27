from flask import request, jsonify
from flask_restful import Resource
from config import mysql
from .helpers import _authenticate_user, _get_photo_uri
from base64 import b64decode
import os


class PhotoUri(Resource):
    def get(self):
        try:
            user_id = _authenticate_user(request)
            photo_id = request.headers.get('PhotoId')
        except Exception as err:
            return jsonify({'success': False, 'error': 'incorrectOrExpiredAuthToken', 'photoUri': ''})

        try:
            photo_uri = _get_photo_uri(photo_id, user_id)
        except Exception as err:
            return jsonify({'success': False, 'error': 'databaseError', 'photoUri': ''})

        return jsonify({'success': True, 'error': '', 'photoUri': photo_uri})

    def delete(self):
        try:
            user_id = _authenticate_user(request)
            photo_id = request.headers.get('PhotoId')
        except Exception as err:
            return jsonify({'success': False, 'error': 'incorrectOrExpiredAuthToken'})
        
        print('deleting ', photo_id)
        try:
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM Photo WHERE photoID=%s AND userID=%s", (photo_id, user_id))
            mysql.connection.commit()
            cur.close()
        except Exception as err:
            print(err)
            return jsonify({'success': False, 'error': 'databaseError'})
        
        photo_path = f'photos/{user_id}/{photo_id}.txt'
        try:
            if os.path.exists(photo_path):
                os.remove(photo_path)
        except Exception as err:
            print(err)
            return jsonify({'success': False, 'error': 'osError'})
 
        return jsonify({'success': True, 'error': ''})