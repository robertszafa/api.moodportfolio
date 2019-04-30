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
			where_clause.append("P.timestamp BETWEEN \""+start_date +"\" AND \""+ end_date + "\"")

		if city!='':
			where_clause.append("P.city=\""+city+"\"")
		
		if country!='':
			where_clause.append("P.country=\""+country+"\"")

		if user_id!='':
			where_clause.append("P.UserID="+user_id)

		if tag_name!='':
			queryingTags = True
			where_clause.append("T.name=\""+tag_name+"\"")

		if tag_id!='':
			queryingTags = True
			where_clause.append("PT.tagID="+tag_id)

		where_clause_STR = " AND ".join(where_clause)
		

		sqlStmt = ""
		if not queryingTags:
			sqlStmt = "SELECT emotion FROM Photo P WHERE "+ where_clause_STR
		else:
			sqlStmt = "SELECT P.emotion, P.timestamp, P.photoID, P.city, P.country, T.name, PT.tagID FROM Photo P NATURAL JOIN Photo_Tag PT NATURAL JOIN Tag T WHERE "+ where_clause_STR
		
		print("[ADMIN_QUERY]sql stmt made: ", sqlStmt)
		emotions=None
		try:
			cur = mysql.connection.cursor()
			cur.execute(sqlStmt)
			emotions = cur.fetchall()
			cur.close()
		except Exception as err:
			print(err)
			return jsonify({'success': False, 'error': 'databaseError', 'emotions': ''})

		return jsonify({'success': True, 'error': '', 'result': emotions})

	def delete(self):
		try:
			admin_id = _authenticate_user(request)
			user_id = request.args.get('userID') 
			#if all then delete everything.

		except Exception as err:
			return jsonify({'success': False, 'error': 'incorrectOrExpiredAuthToken'})

		where_clause = "" #delete everything
		if user_id!="all": 
			where_clause = "userID=%s",user_id
		
		try:
			cur = mysql.connection.cursor()
			if where_clause=="":
				curr.execute("DELETE * FROM User")
			else:
				cur.execute("DELETE * FROM User WHERE %s",where_clause)
				cur.execute("DELETE * FROM Photo WHERE %s",where_clause)
			cur.close()
		except Exception as err:
			print(err)
			return jsonify({'success': False, 'error': 'databaseError'})

		return jsonify({'success': True, 'error': ''})
