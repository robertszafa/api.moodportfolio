from flask import request, jsonify
from flask_restful import Resource
from config import mysql
from .helpers import _authenticate_user


class IsAdmin(Resource):
    def get(self):
        user_id = _authenticate_user(request)

        if not user_id:
            return jsonify({'success': False, 'error': 'incorrectOrExpiredAuthToken'})
        
        is_admin = False
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT admin FROM User WHERE userID=%s", (user_id, ))
            is_admin = cur.fetchone()['admin']
            cur.close()
        except Exception as err:
            print(err)
            return jsonify({'success': False, 'error': 'databaseError'})

        
        return jsonify({'success': is_admin, 'error': ''})
