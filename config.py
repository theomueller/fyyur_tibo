import os
SECRET_KEY = os.urandom(32)

# during the deveopmemnt
WTF_CSRF_ENABLED = False

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://meunieth@localhost:5432/fyyurtmapp'
# done with createdb fyyurtmapp in my terminal
# check it with psql fyyurtmapp
SQLALCHEMY_TRACK_MODIFICATIONS = False