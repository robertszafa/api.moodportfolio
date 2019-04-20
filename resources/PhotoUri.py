from flask import request, jsonify
from flask_restful import Resource
from config import mysql
from .helpers import _authenticate_user, _get_photo_uri
from base64 import b64decode
import os


class PhotoUri(Resource):
    def get(self):
        try:
            user_id = _authenticate_user(request)
            photo_id = request.headers.get('PhotoId')
        except Exception as err:
            return jsonify({'success': False, 'error': 'incorrectOrExpiredAuthToken', 'photoUri': ''})

        photo_uri = _get_photo_uri(photo_id)

        return jsonify({'success': True, 'error': '', 'photoUri': photo_uri})
