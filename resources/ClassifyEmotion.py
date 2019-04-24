from flask import request, jsonify
from flask_restful import Resource
from config import mysql
from .helpers import _authenticate_user, _get_num_of_user_photos, _get_place, _dict_to_json
from base64 import b64decode
import os
import datetime
import random
import json
from .ai.EmotionDetector import test_SingleInstance


class ClassifyEmotion(Resource):
    def post(self):
        try:
            user_id = _authenticate_user(request)
            latitude = request.json.get('latitude')
            longitude = request.json.get('longitude')
        except Exception as err:
            return jsonify({'success': False, 'error': 'incorrectOrExpiredAuthToken', 'photoId': '',
                            'emotion' : '', 'dominantEmotion': ''})

        now = datetime.datetime.now()
        now.strftime('%Y-%m-%d %H:%M:%S')

        # Split the data URI on the comma to get the base64 encoded data without the header. 
        # Call base64.b64decode to decode that to bytes. Last, write the bytes to a file.
        data_uri = request.json.get('dataUri')
        header, encoded = data_uri.split(",", 1)

        # store the photo dataURI in a txt file .photos/{user_id}/{photo_index}.txt
        photo_id = _get_num_of_user_photos(user_id) + 1
        photo_index = f'{photo_id}.txt'
        photo_path = f'photos/{user_id}/{photo_index}'
        if not os.path.exists(f'photos/{user_id}'):
                os.makedirs(f'photos/{user_id}')
        with open(photo_path, "w") as f:
                f.write(data_uri)


        ############## CLASSIFY PHOTO HERE ###################################################
        img_data = b64decode(encoded)
        full_path = os.path.dirname(os.path.realpath(__file__))
        model_file_path = os.path.join(full_path,"vgg13.model")
        emotions = test_SingleInstance(model_file_path,img_data)
        #######################################################################################

        # covert to int
        for key in emotions.keys():
            emotions[key] = int(emotions[key] * 100)

        dominant_emotion = max(emotions, key=emotions.get)

        print(emotions)

        # get city, country
        country = ''
        city = ''
        if latitude and longitude:
            country, city = _get_place(latitude, longitude)

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO Photo(userID, timestamp, path, emotion, city, country) VALUES(%s, %s, %s, %s, %s, %s)",
                                (user_id, now, photo_path, json.dumps(emotions), city, country))
            photo_id = cur.lastrowid
            mysql.connection.commit()
            cur.close()
        except Exception as err:
            print(err)
            return jsonify({'success': False, 'error': 'databaseError', 'photoId': '', 'emotion': '', 'dominantEmotion': ''})



        return jsonify({'success': True, 'error': '', 'photoId': photo_id, 'emotion': emotions, 'dominantEmotion': {dominant_emotion: emotions[dominant_emotion]}})




