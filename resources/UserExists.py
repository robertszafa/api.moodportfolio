from flask import request, jsonify
from flask_restful import Resource
from .helpers import _email_exists, _authenticate_user, _get_user_info
import datetime  

class UserExists(Resource):
    def post(self):
        try:
            email = request.json.get('email')
        except:
            return jsonify({'exists' : False, 'error' : 'noEmailProvided'})

        response = _email_exists(email)

        return jsonify({'exists' : response})
