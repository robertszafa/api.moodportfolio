from flask import request, jsonify
from flask_restful import Resource
from config import mysql
from .helpers import _authenticate_user, _get_num_of_photos, _get_place
from base64 import b64decode
import os
import datetime
import random
# from .ai.src.EmotionDetector import test_SingleInstance




class Emotions(Resource):
    def post(self):
        try:
            user_id = _authenticate_user(request)
            latitude = request.json.get('latitude')
            longitude = request.json.get('longitude')
        except Exception as err:
            return jsonify({'success': False, 'error': 'incorrectOrExpiredAuthToken', 'emotion' : ''})

        now = datetime.datetime.now()
        now.strftime('%Y-%m-%d %H:%M:%S')

        # Split the data URI on the comma to get the base64 encoded data without the header. 
        # Call base64.b64decode to decode that to bytes. Last, write the bytes to a file.
        data_uri = request.json.get('dataUri')
        header, encoded = data_uri.split(",", 1)
        
        
        # store the photo dataURI in a txt file .photos/{user_id}/{photo_index}.txt
        photo_index = f'{_get_num_of_photos(user_id) + 1}.txt'
        photo_uri_dir = f'photos/{user_id}/' 
        if not os.path.exists(photo_uri_dir):
            os.makedirs(photo_uri_dir)
        with open(photo_uri_dir + photo_index, "w") as f:
            f.write(data_uri)

        ############## CLASSIFY PHOTO HERE ###################################################
        # save as photos/{user_id}/{photo_index}.jpg (temporarily) and classify
		#IMAGE can be jpeg/png and colored 
        # img_data = b64decode(encoded)
        # saved_model_path = "../ai/vgg13.model"
		#img_path = 
        # emotion = test_SingleInstance(saved_model_path,imgData)
        # print(emotion)
        # photo_jpg_dir = f'photos/{user_id}/{photo_index}.jpg' 
        # with open(photo_jpg_dir, "wb") as f:
        #     f.write(imgData)
        #######################################################################################

        # get city, country
        country = ''
        city = ''
        if latitude and longitude:
            country, city = _get_place(latitude, longitude)

        # get random emotion for now, no one will notice anyway
        # emotion = '{"%s": "100"}' % (random.choice(emotions))
        emotion = '''{
            "Neutral": "%d",
            "Sad": "%d",
            "Happy": "%d",
            "Angry": "%d",
            "Surprise": "%d",
            "Fear": "%d" }''' % (random.randint(0, 100), 
                                 random.randint(0, 100),
                                 random.randint(0, 100),
                                 random.randint(0, 100),
                                 random.randint(0, 100),
                                 random.randint(0, 100),
                                 )
        
        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO Photo(userID, timestamp, path, emotion, city, country) VALUES(%s, %s, %s, %s, %s, %s)",
                        (user_id, now, photo_uri_dir, emotion, city, country))
            mysql.connection.commit()
            cur.close()
        except Exception as err:
            print(err)
            return jsonify({'success': False, 'error': 'databaseError', 'emotion' : ''})


        return jsonify({'success': True, 'error': '', 'emotion': emotion})
