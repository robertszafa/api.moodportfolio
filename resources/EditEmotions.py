from flask import request, jsonify
from flask_restful import Resource
from config import mysql
from .helpers import _authenticate_user, _get_next_photo_id, _get_place
from base64 import b64decode
import os
import datetime
import random
import json

class EditEmotions(Resource):
    def post(self):
        try:
            user_id = _authenticate_user(request)
            photo_id = request.json.get('photoID')
            dominantEmotionName = request.json.get('emotionName')

        except Exception as err:
            return jsonify({'success': False, 'error':         'incorrectOrExpiredAuthToken', 'photoId': '',
                'emotion' : '', 'dominantEmotion': ''})

        emotions = {'neutral' : 0, 'happiness' : 0, 'surprise' : 0,
                    'sadness' : 0,'anger' : 0, 'disgust' : 0, 
                    'fear' : 0, 'contempt' : 0 }
        emotions[dominantEmotionName] = 100

        try:
            cur = mysql.connection.cursor()
            cur.execute("UPDATE Photo SET emotion = %s WHERE photoID=%s AND userID=%s",(json.dumps(emotions),photo_id,user_id))
            mysql.connection.commit()
            cur.close()
        except Exception as err:
            print(err)
            return jsonify({'success': False, 'error': 'databaseError', 'photoId': '', 'emotion': '', 'dominantEmotion': ''})

        return jsonify({'success': True, 'error': '', 'photoId': photo_id, 'emotion': emotions, 'dominantEmotion': {dominantEmotionName: emotions[dominantEmotionName]}})




