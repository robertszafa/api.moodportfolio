"""
Special GET Queries from ADMIN like:
Most popular tag
Number of users registered
"""

from flask import request, jsonify
from flask_restful import Resource
from config import mysql
from .helpers import _authenticate_user, _get_num_of_user_photos, _convert_to_datetime,_get_num_of_all_photos
import os
import datetime
import json

class AdminQuery2(Resource):
	def post(self):
		try:
			admin_id = _authenticate_user(request)
			#CHECK IF HE/SHE IS AN ADMIN?
			spl_SQL_query = request.json.get('splSQLQuery')

		except Exception as err:
			return jsonify({'success': False, 'error': 'incorrectOrExpiredAuthToken', 'emotions': ''})
        
		res=None
		try:
			cur = mysql.connection.cursor()
			cur.execute(spl_SQL_query)

			res = cur.fetchall()
			cur.close()
		except Exception as err:
			print(err)
			return jsonify({'success': False, 'error': 'databaseError', 'res': ''})

		return jsonify({'success': True, 'error': '', 'result': res})