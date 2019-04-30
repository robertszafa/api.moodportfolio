from flask import request, jsonify
from flask_restful import Resource
from flask_mail import Message
from config import mysql, app
from .helpers import _hash_password, _encode_auth_token, _get_user_id, _authenticate_user, _verify_user, _get_user_email, _send_email
import random
import string


class ResetPassword(Resource):
    def post(self):
        try:
            email = request.json.get('email')
            new_password = _get_random_password()
            password_hash = _hash_password(new_password)
        except Exception as e:
            return jsonify({'emailSent' : False, 'error' : 'incorrectInput'})
        
        try:
            cur = mysql.connection.cursor()
            cur.execute(f"UPDATE User SET hashedPassword='{password_hash}' WHERE email='{email}'")
            mysql.connection.commit()
            cur.close()
        except Exception as e:
            return jsonify({'emailSent' : False, 'error' : 'databaseError'})
        
        subject = f'Moodportfolio - Reset password!'
        msg_text = f'Your new password is: {new_password}\n\nYou should change your password after you log in again'
        msg_html = f"<h3>Your new password is: {new_password}\n\nYou should change your password after you log in again</h3>"

        _send_email(subject, msg_text, email, html=msg_html)

        return jsonify({'emailSent' : True, 'error' : ''})

    def put(self):
        try:
            user_id = _authenticate_user(request)
            new_password = request.json.get('newPassword')
            current_password = request.json.get('currentPassword')
        except Exception as e:
            return jsonify({'success' : False, 'error' : 'incorrectInput'})
        
        if not _verify_user(_get_user_email(user_id), current_password).json.get('loggedIn'):
            return jsonify({'success' : False, 'error' : 'wrongCurrentPassword'})
        
        password_hash = _hash_password(new_password)
        try:
            cur = mysql.connection.cursor()
            cur.execute(f"UPDATE User SET hashedPassword='{password_hash}' WHERE userID='{user_id}'")
            mysql.connection.commit()
            cur.close()
        except Exception as e:
            return jsonify({'success' : False, 'error' : 'databaseError'}) 

        return jsonify({'success' : True, 'error' : ''}) 


def _get_random_password():
    password_characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(password_characters) for i in range(10))
