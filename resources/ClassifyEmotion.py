from flask import request, jsonify
from flask_restful import Resource
from config import mysql
from .helpers import _authenticate_user, _get_num_of_user_photos, _get_place, _dict_to_json
from base64 import b64decode
import os
import datetime
import random
import json
# from .ai.src.EmotionDetector import test_SingleInstance




class ClassifyEmotion(Resource):
    def post(self):
        try:
            user_id = _authenticate_user(request)
            latitude = request.json.get('latitude')
            longitude = request.json.get('longitude')
        except Exception as err:
            return jsonify({'success': False, 'error': 'incorrectOrExpiredAuthToken', 'photoId': '', 
                            'photoPath': '', 'emotion' : '', 'dominantEmotion': ''})

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
	# save as photos/{user_id}/{photo_index}.jpg (temporarily) and classify
	img_data = b64decode(encoded)
	full_path = os.path.dirname(os.path.realpath(__file__))	
	model_file_path = os.path.join(full_path,"vgg13.model")
	emotions = test_SingleInstance(model_file_path,img_data)
	print(emotions)
	dominant_emotion = max(emotions, key=emotions.get)
	photo_jpg_dir = f'photos/{user_id}/{photo_index}.jpg' 
	with open(photo_jpg_dir, "wb") as f:
		f.write(imgData)
	#######################################################################################

        # get city, country
        country = ''
        city = ''
        if latitude and longitude:
            country, city = _get_place(latitude, longitude)

        # get random emotion for now, no one will notice anyway
        # emotion = '{"%s": "100"}' % (random.choice(emotions))
        emotions = {}
        emotions['neutral'] = random.randint(0, 100)
        emotions['happiness'] = random.randint(0, 100) 
        emotions['surprise'] = random.randint(0, 100) 
        emotions['sadness'] = random.randint(0, 100) 
        emotions['anger'] = random.randint(0, 100) 
        emotions['disgust'] = random.randint(0, 100) 
        emotions['fear'] = random.randint(0, 100) 
        emotions['contempt'] = random.randint(0, 100) 

        dominant_emotion = max(emotions, key=emotions.get)
        
        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO Photo(userID, timestamp, path, emotion, city, country) VALUES(%s, %s, %s, %s, %s, %s)",
                        (user_id, now, photo_path, json.dumps(emotions), city, country))
            photo_id = cur.lastrowid
            mysql.connection.commit()
            cur.close()
        except Exception as err:
            print(err)
            return jsonify({'success': False, 'error': 'databaseError', 'photoPath': photo_path, 
                            'photoId': '', 'emotion': '', 'dominantEmotion': ''})


        return jsonify({'success': True, 'error': '', 'photoPath': photo_path, 'photoId': photo_id,
                        'emotion': _dict_to_json(emotions), 'dominantEmotion': {dominant_emotion: emotions[dominant_emotion]}})
