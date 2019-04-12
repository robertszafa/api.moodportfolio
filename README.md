# Prerequisites
1. python 3.6+
2. pip
3. Initialise the database from the DB.sql file. Your MySQL password and users should match config.py

# Install
1. git clone https://github.com/robertszafa/api.moodportfolio.git
2. cd api.moodportfolio
3. pip install -r requirements.txt

# Run
1. python server.py

## Comments
- API endpoints are under /resources
- if you create a new API endpoint, you have to also include it in server.py
- if you install any new dependencies, update the requirements file with pip freeze > requirements.txt  
- confirm email & reset password endpoints won't work locally unless you change the redirect from 'moodportfolio.ml' to 'localhost:3000'
- if you do the above, don't forget to change it back