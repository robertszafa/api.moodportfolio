from flask import request, jsonify
from flask_restful import Resource
from config import mysql
from .helpers import _authenticate_user, _get_place, _convert_to_datetime
from base64 import b64decode
import os
import datetime
import json


BASED_ON_ALL = 'all'
BASED_ON_EMOTION = 'emotion'
BASED_ON_TAG = 'tag'
BASED_ON_TAG_USAGE = 'tagUsage'


class EmotionsQuery(Resource):
	def get(self):
		try:
			user_id = _authenticate_user(request)
			based_on = request.headers.get('BasedOn')
			start_date = request.headers.get('StartDate')
			end_date = request.headers.get('EndDate')
			tag_name = request.headers.get('TagName')
			limit = request.headers.get('Limit')
		except Exception as err:
			return jsonify({'success': False, 'error': 'incorrectOrExpiredAuthToken', 'emotions': ''})

		if start_date and end_date:
			start_date = _convert_to_datetime(start_date)
			end_date = _convert_to_datetime(end_date)
		
		print(based_on, start_date, end_date)

		result = None
		if based_on == BASED_ON_ALL:
			try:
				cur = mysql.connection.cursor()
				if limit:
					cur.execute("""SELECT emotion, timestamp, photoID, city, description FROM Photo 
								   WHERE UserID=%s ORDER BY photoID DESC LIMIT %s""",
								   (user_id, int(limit)))
				else:
					cur.execute("""SELECT emotion, timestamp, photoID, city, description FROM Photo 
					 			   WHERE (timestamp BETWEEN %s AND %s) AND UserID=%s""",
								   (start_date, end_date, user_id))

				result = cur.fetchall()
				cur.close()
			except Exception as err:
				print(err)
				return jsonify({'success': False, 'error': 'databaseError', 'emotions': ''})
		elif based_on == BASED_ON_TAG_USAGE:
			try:
				cur = mysql.connection.cursor()
				cur.execute("""SELECT name, tagID, count FROM Tag WHERE tagID in 
				              (SELECT tagID FROM Photo_Tag WHERE photoID in (SELECT photoID FROM Photo 
							  WHERE (timestamp BETWEEN %s AND %s) AND userID=%s)) ORDER BY count DESC""", 
							  (start_date, end_date, user_id))

				result = cur.fetchall()
				cur.close()
			except Exception as err:
				print(err)
				return jsonify({'success': False, 'error': 'databaseError', 'result': result})
		elif based_on == BASED_ON_TAG:
			try:
				cur = mysql.connection.cursor()
				cur.execute("""SELECT emotion, timestamp, photoID, city, description 
							   FROM Photo WHERE (timestamp BETWEEN %s AND %s) AND userID=%s 
							   AND photoID in (SELECT photoID FROM Photo_Tag WHERE 
							   tagID=(SELECT tagID FROM Tag WHERE name=%s))""", 
							   (start_date, end_date, user_id, tag_name))

				result = cur.fetchall()
				cur.close()
			except Exception as err:
				print(err)
				return jsonify({'success': False, 'error': 'databaseError', 'result': result})
		

		return jsonify({'success': True, 'error': '', 'result': result})
