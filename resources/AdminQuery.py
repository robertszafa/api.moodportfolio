from flask import request, jsonify
from flask_restful import Resource
from config import mysql
from .helpers import _authenticate_user, _get_num_of_user_photos, _convert_to_datetime,_get_num_of_all_photos
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
			admin_id = _authenticate_user(request)
			#CHECK IF HE/SHE IS AN ADMIN?
			based_on = request.json.get('basedOn')
			#based_on = "city" "country" "user_id" "timestamp" "tag"
			#leave other json fields empty if NOT NEEDED.
			start_date = request.json.get('startDate')
			end_date = request.json.get('endDate')
			city = request.json.get('city')
			country = request.json.get('country')
			user_id = request.json.get('userID')
			tag = request.json.get('tag')
			
			#combinations:
			"""
			single tag, multiple tags
			city | country | city/country+user_id | city/country+user_id + time | city/country+time
			"""
		except Exception as err:
			return jsonify({'success': False, 'error': 'incorrectOrExpiredAuthToken', 'emotions': ''})

		start_date = _convert_to_datetime(start_date)
		end_date = _convert_to_datetime(end_date)

		if based_on == "??????":
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
