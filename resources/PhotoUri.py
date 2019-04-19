from flask import request, jsonify
from flask_restful import Resource
from config import mysql
from .helpers import _authenticate_user
from base64 import b64decode
import os


class PhotoUri(Resource):
    def get(self):
        try:
            user_id = _authenticate_user(request)
            photo_path = request.headers.get('Path')
        except Exception as err:
            return jsonify({'success': False, 'error': 'incorrectOrExpiredAuthToken', 'photoUri': ''})

        photo_uri = ""
        with open(photo_path, "r") as f:
            photo_uri = f.read()

        return jsonify({'success': True, 'error': '', 'photoUri': photo_uri})
