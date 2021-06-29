#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import re
import dateutil.parser
from datetime import datetime
import babel
from flask import (
  Flask, 
  render_template,
  request, Response, 
  flash, 
  redirect, 
  url_for
)
from flask_moment import Moment

import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm as Form
from forms import *
# TM: add flask migrate in the import
from flask_migrate import Migrate
import config
# TM: import everything from models.py
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
# db = SQLAlchemy(app) -> moved to models.py to avoid circular import
db.init_app(app)

# TODO: connect to a local postgresql database 
# -> Config done
# -> $ flask db init was done in the terminal
# -> $ flask db migrate : didnt work -> new installation of psycopg2 needed !
migrate = Migrate(app,db)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  #date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(value, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

#  Get all Venues 
#  ----------------------------------------------------------------
@app.route('/venues')
def venues():
  # replace with real venues data.
  # num_shows should be aggregated based on number of upcoming shows per venue.

  # create en empty array
  data=[] 
  # get all the venues
  venues = Venue.query.all()
  # store the cities and state in a set
  # set in python are unordered, unchangeable and do not allow duplicate values
  # my second option would have been to use a SELECT DISTINCT
  loc = Venue.query.distinct(Venue.city, Venue.state).all()
  for l in loc:
      data.append({
        "city":l.city,
        "state":l.state,
        "venues":[]
      })
  # first loop to calculate the number of upcoming show 
  for venue in venues:
    num_upcoming_shows = 0
    today = datetime.now()
    num_upcoming_shows =  (db.session.query(Show).filter(Show.venue_id==venue.id)).filter(Show.start_time > today).count()

    # an other way could be to query by filtering on the loc but what about num_upconing shows!
    for d in data:
      if venue.city == d['city'] and venue.state == d['state']:
        d['venues'].append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": num_upcoming_shows
        })


  return render_template('pages/venues.html', areas=data)

#  Search Venue 
#  ----------------------------------------------------------------
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike("%" + search_term + "%")).all()

  response = {
    "count":len(venues),
    "data": []
  }

  for venue in venues:
    response["data"].append({
        'id': venue.id,
        'name': venue.name,
    })
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

#  Get Venue [cRud] per Id
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get_or_404(venue_id)
  today = datetime.now()
  past_shows = []
  upcoming_shows = []
  print(venue.genres)

  for show in venue.shows:
    temp_show = {
        'artist_id': show.artist_id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.start_time#.strftime("%m/%d/%Y, %H:%M")
    }
    if show.start_time <= today:
        past_shows.append(temp_show)
    else:
        upcoming_shows.append(temp_show)

  # object class to dict -> sehr cool function !!!!
  data = vars(venue) 

  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue [CRud]: 1. Form 2. Submission 
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # insert form data as a new Venue record in the db
  form = VenueForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      venue = Venue()
      form.populate_obj(venue)
      db.session.add(venue)
      db.session.commit()
    # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully created!')
    except (ValueError, KeyError, TypeError) as error:
      print(error) 
      db.session.rollback()
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be created.')
    # on unsuccessful db insert, flash an error instead.
    finally:
      db.session.close()
    return render_template('pages/home.html')
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
    return render_template('forms/new_venue.html', form=form)

#  Edit Venue [cRud] per Id
#  ----------------------------------------------------------------
# modify data to be the data object returned from db insertion
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  form.genres.default = venue.genres

  return render_template('forms/edit_venue.html', form=form, venue=venue)

# modify data to be the data object returned from db insertion
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_sbumission(venue_id):
  form = VenueForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      venue = Venue.query.get(venue_id)
      form.populate_obj(venue)
      db.session.commit()
      flash('Venue ' + name + 'has been updated')
    except:
      db.session.rollback()
      flash('An error occured while trying to edit Venue')
    finally:
      db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
    return render_template('forms/new_venue.html', form=form)
    
  

#  Delete Venue [cruD]
#  ----------------------------------------------------------------
#Complete this endpoint for taking a venue_id, and using
# SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
@app.route('/venues/<int:venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    # need to check if i hav to store the name of the venue
    # what happens with show ? Should I delete the show too ?
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue.name + 'was deleted')
  except:
    flash('Venue '+ venue.name + ' was not deleted')
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('index'))

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists(): 
   # replace with real data returned from querying the database

  data = []

  artists = Artist.query.all()
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name
    })

  return render_template('pages/artists.html', artists=data)

#  Search Artist 
#  ----------------------------------------------------------------
@app.route('/artists/search', methods=['POST'])
def search_artists():
  # implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike("%" + search_term + "%")).all()

  response = {
    "count":len(artists),
    "data": []
  }

  for artist in artists:
    response["data"].append({
        'id': artist.id,
        'name': artist.name,
    })
 
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

#  Get Artist [cruD]
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # replace with real artist data from the artist table, using artist_id
 
  artist = Artist.query.get(artist_id)

  past_shows = []
  upcoming_shows = []

  for show in artist.shows:
      temp_show = {
          'venue_id': show.venue_id,
          'venue_name': show.venue.name,
          'venue_image_link': show.venue.image_link,
          'start_time': show.start_time#.strftime("%m/%d/%Y, %H:%M")
      }
      if show.start_time <= datetime.now():
          past_shows.append(temp_show)
      else:
          upcoming_shows.append(temp_show)

  # object class to dict
  data = vars(artist)
  
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)
  return render_template('pages/show_artist.html', artist=data)

#  Update / Edit 1.open the form 2. Callback = edit submission
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  #form.genres.default = artist.genres
  # populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # Take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  artist = Artist.query.get(artist_id)
  if form.validate():
    try:
      form.populate_obj(artist)
      db.session.commit()
      flash('The Artist ' +
                request.form['name'] + ' has been successfully updated!')
    except:
          db.session.rollback()
          flash('An Error has occured and the update unsuccessfull')
    finally:
          db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
    return render_template('forms/edit_artist.html', form=form, artist=artist)


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # insert form data as a new Artist(!) record in the db, instead
  form = ArtistForm(request.form)
  if form.validate():
    try:
      artist = Artist()
      form.populate_obj(artist)
      db.session.add(artist)
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully created!')
    except:
      db.session.rollback()
      flash('An error ocurred, Artist ' +
      request.form['name'] + ' could not be created')
    finally:
      db.session.close()
    return render_template('pages/home.html')
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
    return render_template('forms/new_artist.html', form=form)

# Delete Artist

@app.route('/artists/<artist_id>/delete', methods=['DELETE'])
def delete_artist(artist_id):
  try:
    artist = Artist.query.get(artist_id)
    # need to check if i hav to store the name of the venue
    db.session.delete(artist)
    db.session.commit()
    flash('Artist ' + artist.name + 'was deleted')
  except:
    flash('Artist '+ artist.name + ' was not deleted')
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('index'))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # replace with real venues data.
  # need to create show.artist_name 
  # num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Show.query.join(Venue, Venue.id == Show.venue_id ).join(Artist, Artist.id == Show.artist_id).order_by(db.desc(Show.start_time)).all()
  return render_template('pages/shows.html', shows=shows)
 
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  try:
    show = Show()
    show.artist_id = form.artist_id.data
    show.venue_id = form.venue_id.data
    show.start_time = form.start_time.data
  
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')

  except:
    # on unsuccessful db insert, flash an error instead.
    db.session.rollback()
    flash('An error occured. show could not be listed')
  finally:
    db.session.close()

  return render_template('pages/home.html')
#----------------------------------------------------------------------------#
# error handler.
#----------------------------------------------------------------------------#


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
