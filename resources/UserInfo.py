from flask import request, jsonify
from flask_restful import Resource
from .helpers import _email_exists, _authenticate_user, _get_user_info
from config import mysql


iso5218_gender = {
    0: 'Not known',
    1: 'Male',
    2: 'Female',
    9: 'Other',
}

class UserInfo(Resource):
    def post(self):
        user_id = _authenticate_user(request)

        if not user_id:
            return jsonify({'success': False, 'error': 'incorrectOrExpiredAuthToken'})

        try:
            user_data = request.json
        except:
            return jsonify({'success': False, 'error': 'noDataSupplied'})
        
        dob = request.json.get('dob')
        dob_formatted = dob.split('T')[0]
        old_user_info = _get_user_info(user_id)

        try:
            cur = mysql.connection.cursor()
            cur.execute ("""
                            UPDATE User
                            SET country=%s, townCity=%s, dob=%s, gender=%s, nominatedContact=%s
                            WHERE userID=%s
                        """, (user_data.get('country') or old_user_info['country'], 
                              user_data.get('townCity') or old_user_info['townCity'], 
                              dob_formatted or old_user_info['dob'], 
                              int(user_data.get('gender')) or old_user_info['gender'], 
                              user_data.get('nominatedContact') or old_user_info['nominatedContact'], 
                              user_id)) 

            mysql.connection.commit()
            cur.close()
        except Exception as err:
            return jsonify({'success': False, 'error': f'databaseError: {err}'})


        return jsonify({'success': True, 'error': ''})

    def get(self):
        user_id = _authenticate_user(request)

        if not user_id:
            return jsonify({'success': False, 'error': 'incorrectOrExpiredAuthToken'})

        user_info = _get_user_info(user_id)
        user_info['signupDate'] = user_info['signupDate'].strftime(f"%d/%m/%Y")
        user_info['dob'] = user_info['dob'].strftime(f"%d/%m/%Y")
        user_info['gender'] = iso5218_gender[user_info['gender']]

        return jsonify({'success': True, 'data': user_info})

