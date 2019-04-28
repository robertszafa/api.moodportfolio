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

"""
USE GUIDE:
GET REQUEST SHOULD INCLUDE:
{
	'basedOn' : "#users" or "popularTag" or "any"
	'splSQLQuery' : "select * from ..... "
}
#users -> Number of users registered
popularTag -> Most popular tag
any -> write your own query in "splSQLQuery"
"""

class AdminQuery2(Resource):

    def get(self):
		try:
			admin_id = _authenticate_user(request)
			#CHECK IF HE/SHE IS AN ADMIN?
			based_on = request.json.get('basedOn')
            spl_SQL_query = request.json.get('splSQLQuery')

		except Exception as err:
			return jsonify({'success': False, 'error': 'incorrectOrExpiredAuthToken', 'emotions': ''})
        
		res=None
		try:
			cur = mysql.connection.cursor()
            if based_on=='#users':
                cur.execute("SELECT COUNT(*) FROM User")
            elif based_on=='popularTag':
                cur.execute("SELECT name,count FROM Tag WHERE count = (SELECT max(count) FROM Tag)")
            else: #if based_on=="any":
                cur.execute(spl_SQL_query)

			res = cur.fetchall()
			cur.close()
		except Exception as err:
			print(err)
			return jsonify({'success': False, 'error': 'databaseError', 'res': ''})

		return jsonify({'success': True, 'error': '', 'result': res})