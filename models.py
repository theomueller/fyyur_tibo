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
    genres = db.Column("genres",db.ARRAY(db.String()),nullable=False) 
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    # implement a relationshipn one to many (one show /one artist/ one venue)
    shows = db.relationship('Show', backref=db.backref('venue'), lazy="joined")

    def __repr__(self):
        return f"<Venue {self.id} name:{self.name}>"

class Artist(db.Model):
    __tablename__ = 'artists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column("genres",db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=True)
    seeking_description=db.Column(db.String(250))
    # implement a relationshipn one to many (one show /one artist/ one venue)
    shows = db.relationship('Show', backref=db.backref('artist'), lazy="joined")

    def __repr__(self):
        return f"<Artist {self.id} name:{self.name}>"

class Show(db.Model):
    __tablename__='shows'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
   
    def __repr__(self):
       return f"<Show {self.id} Artist:{self.artist_id} Venue:{self.venue_id} s>"
