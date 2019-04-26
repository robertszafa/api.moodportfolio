from flask import request, jsonify
from flask_restful import Resource
from config import mysql
from .helpers import _authenticate_user, _get_num_of_user_photos, _convert_to_datetime,_get_num_of_all_photos
import os
import datetime
import json


class AdminQuery(Resource):
	def post(self):
		try:
			admin_id = _authenticate_user(request)
			#CHECK IF HE/SHE IS AN ADMIN?
			#based_on = "city" "country" "user_id" "timestamp" "tag"
			#leave other json fields empty if NOT NEEDED.
			start_date = request.json.get('startDate')
			end_date = request.json.get('endDate')
			city = request.json.get('city')
			country = request.json.get('country')
			user_id = request.json.get('userID')
			tag_name = request.json.get('tagName')			
			tag_id = request.json.get('tagID')	

		except Exception as err:
			return jsonify({'success': False, 'error': 'incorrectOrExpiredAuthToken', 'emotions': ''})

		where_clause = []
		queryingTags = False
		
		if start_date!='' and end_date!='':
			start_date = _convert_to_datetime(start_date)
			end_date = _convert_to_datetime(end_date)
			where_clause.append("P.timestamp BETWEEN %s AND %s",(start_date, end_date))

		if city!='':
			where_clause.append("P.city=%s",city)
		
		if country!='':
			where_clause.append("P.country=%s",country)

		if user_id!='':
			where_clause.append("P.UserID=%s",user_id)

		if tag_name!='':
			queryingTags = True
			where_clause.append("T.name=%s",city)

		if tag_id!='':
			queryingTags = True
			where_clause.append("PT.tagID=%s",city)

		where_clause_STR = " AND ".join(where_clause)
		emotions=None
		try:
			cur = mysql.connection.cursor()
			if not queryingTags:
				cur.execute("SELECT * FROM Photo P WHERE %s", where_clause_STR)
			else:
				cur.execute("SELECT P.emotion, P.timestamp, P.photoID, P.city, P.country, T.name, PT.tagID FROM Photo P NATURAL JOIN Photo_Tag PT NATURAL JOIN Tag T WHERE %s", where_clause_STR)

			emotions = cur.fetchall()
			cur.close()
		except Exception as err:
			print(err)
			return jsonify({'success': False, 'error': 'databaseError', 'emotions': ''})

		return jsonify({'success': True, 'error': '', 'result': emotions})
