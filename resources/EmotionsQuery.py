from flask import request, jsonify
from flask_restful import Resource
from config import mysql
from .helpers import _authenticate_user, _get_num_of_user_photos, _get_place, _convert_to_datetime
from base64 import b64decode
import os
import datetime
import json


BASED_ON_ALL = 'all'
BASED_ON_EMOTION = 'emotion'
BASED_ON_TAG = 'tag'


class EmotionsQuery(Resource):
    def post(self):
        try:
            user_id = _authenticate_user(request)
            based_on = request.json.get('basedOn')
            start_date = request.json.get('startDate')
            end_date = request.json.get('endDate')
        except Exception as err:
            return jsonify({'success': False, 'error': 'incorrectOrExpiredAuthToken', 'emotions': ''})

        start_date = _convert_to_datetime(start_date)
        end_date = _convert_to_datetime(end_date)

        if based_on == BASED_ON_ALL:
            try:
                cur = mysql.connection.cursor()
                cur.execute("SELECT emotion, timestamp, photoID FROM Photo WHERE (timestamp BETWEEN %s AND %s) AND UserID=%s",
                            (start_date, end_date, user_id))
                emotions = cur.fetchall()
                cur.close()
            except Exception as err:
                print(err)
                return jsonify({'success': False, 'error': 'databaseError', 'emotions': ''})

        return jsonify({'success': True, 'error': '', 'result': emotions})
