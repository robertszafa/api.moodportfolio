from flask import request, jsonify
from flask_restful import Resource
from config import mysql
from .helpers import _authenticate_user
import os


class PhotoDescription(Resource):
    def post(self):
        try:
            user_id = _authenticate_user(request)
            photo_path =  request.json.get('photoPath')
            description = request.json.get('description')
        except Exception as err:
            return jsonify({'success': False, 'error': 'incorrectOrExpiredAuthToken'})

        try:
            cur = mysql.connection.cursor()
            cur.execute("UPDATE Photo SET description=%s WHERE userID=%s AND path=%s", 
                        (description, user_id, photo_path))
            mysql.connection.commit()
            cur.close()
        except Exception as err:
            print(err)
            return jsonify({'success': False, 'error': 'databaseError'})


        return jsonify({'success': True, 'error': ''})
