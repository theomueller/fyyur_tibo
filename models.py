from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column("genres",db.ARRAY(db.String()),nullable=False) 
    # if genres doesn't work here _I will need to do it in alambic after migration
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    # implement a relationshipn one to many (one show /one artist/ one venue)
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
        return f"<Venue {self.id} name:{self.name}>"

class Artist(db.Model):
    __tablename__ = 'artists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column("genres",db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=True)
    seeking_description=db.Column(db.String(250))
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
        return f"<Artist {self.id} name:{self.name}>"

#  Implement Show models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__='shows'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
   
    def __repr__(self):
       return f"<Show {self.id} Artist:{self.artist_id} Venue:{self.venue_id} s>"
