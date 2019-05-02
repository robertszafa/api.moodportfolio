from flask import request, jsonify, url_for, redirect
from flask_restful import Resource
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from config import mysql, app
from .helpers import _hash_password, _encode_auth_token, _get_user_id, _authenticate_user, _send_email
from datetime import datetime, timedelta
import jwt


s = URLSafeTimedSerializer(app.config.get('SECRET_KEY'))


class Register(Resource):
    def post(self):
        try:
            name = request.json.get('name')
            email = request.json.get('email')
            password = _hash_password(request.json.get('password'))

            registration_token = _encode_registration_token(name, password)
        except:
            return jsonify({'emailSent' : False, 'error' : 'incorrectInput'})

        token = s.dumps(email, salt='email-confirm')
        subject = f'Almost there {name}! Confirm Your Email'
        link = url_for('confirm_email',
                        token=token,
                        registration_token=registration_token,
                        _external=True)
        msg_text = f'Dear {name}, click the link below to verify your account.\n\n{link}'
        msg_html = f"<h3>Dear {name}, click <a href='{link}'>here</a> to verify your account.</h3>"

        # _send_email(subject, msg_text, email, name=name, html=msg_html)

        headers = {
            'Authorization': 'ba365b103bb3218b3ba1b11660a456c29670ce7d',
            'Content-Type': 'application/json',
        }

        data = '{\n    "options": {\n      "sandbox": true\n    },\n    "content": {\n      "from": "testing@sparkpostbox.com",\n      "subject": "Thundercats are GO!!!",\n      "text": "Welcome"\n    },\n    "recipients": [{ "address": "moodportfol.io@gmail.com" }]\n}'

        response = requests.post('https://api.eu.sparkpost.com/api/v1/transmissions', headers=headers, data=data)

        return jsonify({'emailSent' : True, 'error' : ''})


        return jsonify({'emailSent' : True, 'error' : ''})

    def delete(self):
        try:
            user_id = _authenticate_user(request)
        except Exception as err:
            return jsonify({'success': False, 'error': 'incorrectOrExpiredAuthToken'})
        
        try:
            cur = mysql.connection.cursor()
            # get all user tags 
            cur.execute("""SELECT tagID FROM Photo_Tag 
                           WHERE photoID in (SELECT photoID FROM Photo WHERE userID=%s)""", 
                           (user_id,))

            tags = cur.fetchall()

            for tag in tags:
                tag_id = tag['tagID']
                # count this tag
                tag_count = cur.execute("""SELECT * FROM Photo_Tag WHERE photoID in 
                                        (SELECT photoID FROM Photo WHERE userID=%s) AND tagID=%s""", 
                                        (user_id, tag_id))
                # update count in Tags
                cur.execute("UPDATE Tag SET count=count-%s", (tag_count, ))

            # delete user's Photo_Tags
            cur.execute("""DELETE FROM Photo_Tag 
                           WHERE photoID in (SELECT photoID FROM Photo WHERE userID=%s)""", 
                           (user_id, ))
            # delete Tag if count==0
            cur.execute("DELETE FROM Tag WHERE count<1")
            # delete all photos
            cur.execute("DELETE FROM Photo WHERE userID=%s", (user_id, ))
            # delete user
            cur.execute("DELETE FROM User WHERE userID=%s", (user_id, ))

            mysql.connection.commit()
            cur.close()
        except Exception as err:
            print(err)
            return jsonify({'success': False, 'error': 'databaseError'})
        

        return jsonify({'success': True, 'error': ''})


@app.route('/confirm_email/<token>')
def confirm_email(token):
    # confirmation token expires after 24h
    email = s.loads(token, salt='email-confirm', max_age=36000) 

    registration_token = request.args.get('registration_token')
    name, password = _decode_registration_token(registration_token)
    now = datetime.now()
    now.strftime('%Y-%m-%d %H:%M:%S')
   
    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO User(name, hashedPassword, email, signupDate) VALUES(%s, %s, %s, %s)",
                        (name, password, email, now))
        mysql.connection.commit()
        cur.close()
    except Exception as err:
        return '<h1>Ups, an error has occured... Please try again later</h1>'

    return redirect("https://moodportfolio.ml/login", code=302)



def _encode_registration_token(name, password_hash):
    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=1, seconds=0),
            'iat': datetime.utcnow(),
            'name': name,
            'password_hash': password_hash
        }
        return jwt.encode(
            payload,
            app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        print(e)
        return e

def _decode_registration_token(auth_token):
    try:
        payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
        return payload['name'], payload['password_hash']
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False

