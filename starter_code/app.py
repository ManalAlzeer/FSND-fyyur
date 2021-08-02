#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from os import name
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))

    # implement any missing fields, as a database migration using Flask-Migrate
    show = db.relationship('Show',backref='venue',lazy=True)

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'

#----------------------------------------------------------------------------#

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))

    # implement any missing fields, as a database migration using Flask-Migrate
    show = db.relationship('Show',backref='artist',lazy=True)

    def __repr__(self):
        return f'<Artist: {self.id} {self.name}>'
#----------------------------------------------------------------------------#

# Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, nullable=False)
  venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id'),nullable=False)
  artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id'),nullable=False)

  def __repr__(self):
        return f'<Show {self.id} {self.start_time} {self.venue_id} {self.artist_id}>'


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # replace with real venues data.
  # num_shows should be aggregated based on number of upcoming shows per venue.

  data=[]
  Areas = Venue.query.with_entities(Venue.city, Venue.state).distinct()

  for area in Areas:
    venueList=[]
    venues = Venue.query.filter_by(city=area.city).filter_by(state=area.state).all()

    for venue in venues:
      venueList.append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': len(Show.query.filter_by(venue_id=venue.id).filter(Show.start_time>datetime.now()).all())
      })

    data.append({
      'city':area.city,
      'state':area.state,
      'venues':venueList
    })
  return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term = request.form['search_term']
  search = "%{}%".format(search_term).strip()
# search = search.lower().strip()
  searchTerm = Venue.query.filter(Venue.name.like(search)).all()

  data = []
  for venue in searchTerm:
    data.append({
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': len(Show.query.filter(Show.start_time > datetime.now()).all())
       })

    response={
    "count": len(data),
    "data": data
    }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # replace with real venue data from the venues table, using venue_id

  venue = Venue.query.get(venue_id)
  data=[]
  upcoming_shows = []
  past_shows = []
  upcomingshows = []
  pastshows = []

  shows = Show.query.join(Artist).filter(Show.venue_id==venue_id).all()

  for show in shows:
    if show.start_time > datetime.now():
      upcomingshows.append(show)
    else:
      pastshows.append(show)
  
  for show in upcomingshows:
    print(show.start_time)
    upcoming_shows.append({
      'artist_id': show.artist.id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': format_datetime(str(show.start_time))  
    })
  for show in pastshows:
    past_shows.append({
      'artist_id': show.artist.id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': format_datetime(str(show.start_time)) 
    })

  data = {
    "id": venue_id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "past_shows_count": len(past_shows),        
    "upcoming_shows": upcoming_shows,
    "upcoming_shows_count": len(upcoming_shows)
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # insert form data as a new Venue record in the db, instead
  # modify data to be the data object returned from db insertion
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  address = request.form['address']
  phone = request.form['phone']
  genres = request.form.getlist('genres')
  facebook_link = request.form['facebook_link']
  image_link = request.form['image_link']
  website_link = request.form['website_link']
  if 'seeking_talent' in request.form : seeking_talent = True 
  else : seeking_talent = False
  seeking_description = request.form['seeking_description']

  
  try:
    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link,
    image_link=image_link, website=website_link, seeking_talent=seeking_talent, seeking_description=seeking_description)
    
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + request.form['name']+ ' could not be listed.')
  finally:
    db.session.close()
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback() 
  finally:
    db.session.close()
    return render_template('pages/home.html')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # replace with real data returned from querying the database
  data = Artist.query.all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form['search_term']
  search = "%{}%".format(search_term).strip()
# search = search.lower().strip()
  searchTerm = Artist.query.filter(Artist.name.like(search)).all()

  data = []
  for artist in searchTerm:
    data.append({
      'id': artist.id,
      'name': artist.name,
      'num_upcoming_shows': len(Show.query.filter(Show.start_time > datetime.now()).all())
       })

    response={
    "count": len(data),
    "data": data
    }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # replace with real artist data from the artist table, using artist_id
  
  artist = Artist.query.get(artist_id)
  data=[]
  upcoming_shows = []
  past_shows = []
  upcomingshows = []
  pastshows = []

  shows = Show.query.join(Venue).filter(Show.artist_id==artist_id).all()

  for show in shows:
    if show.start_time > datetime.now():
      upcomingshows.append(show)
    else:
      pastshows.append(show)
  
  for show in upcomingshows:
    print(show.start_time)
    upcoming_shows.append({
      'venue_id': show.venue.id,
      'venue_name': show.venue.name,
      'venue_image_link': show.venue.image_link,
      'start_time': format_datetime(str(show.start_time))  
    })
  for show in pastshows:
    past_shows.append({
      'venue_id': show.venue.id,
      'venue_name': show.venue.name,
      'venue_image_link': show.venue.image_link,
      'start_time': format_datetime(str(show.start_time))  
    })

  data = {
    "id": artist_id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "past_shows_count": len(past_shows),        
    "upcoming_shows": upcoming_shows,
    "upcoming_shows_count": len(upcoming_shows)
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  artist_data = Artist.query.get(artist_id)

  artist={
    "id": artist_id,
    "name": artist_data.name,
    "genres": artist_data.genres,
    "city": artist_data.city,
    "state": artist_data.state,
    "phone": artist_data.phone,
    "website": artist_data.website,
    "facebook_link": artist_data.facebook_link,
    "seeking_venue": artist_data.seeking_venue,
    "seeking_description": artist_data.seeking_description,
    "image_link": artist_data.image_link
  }
  # populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  artist = Artist.query.get(artist_id)
  artist.name = request.form['name']
  artist.city = request.form['city']
  artist.state = request.form['state']
  artist.phone = request.form['phone']
  artist.genres = request.form.getlist('genres')
  artist.facebook_link = request.form['facebook_link']
  artist.image_link = request.form['image_link']
  artist.website = request.form['website_link']
  if 'seeking_venue' in request.form : seeking_venue = True 
  else : seeking_venue = False
  artist.seeking_description = request.form['seeking_description']
  
  try:
    db.session.add(artist)
    db.session.commit()
    # on successful
    flash('Artist ' + request.form['name'] + ' was successfully !')
  except:
    db.session.rollback()
    print(sys.exc_info())
    # on unsuccessful
    flash('An error occurred. Artist ' + request.form['name'])
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_data = Venue.query.get(venue_id)

  venue={
    "id": venue_id,
    "name": venue_data.name,
    "genres": venue_data.genres,
    "address": venue_data.address,
    "city": venue_data.city,
    "state": venue_data.state,
    "phone": venue_data.phone,
    "website": venue_data.website,
    "facebook_link": venue_data.facebook_link,
    "seeking_talent": venue_data.seeking_talent,
    "seeking_description": venue_data.seeking_description,
    "image_link": venue_data.image_link
  }
  # populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  venue.name = request.form['name']
  venue.city = request.form['city']
  venue.state = request.form['state']
  venue.address = request.form['address']
  venue.phone = request.form['phone']
  venue.genres = request.form.getlist('genres')
  venue.facebook_link = request.form['facebook_link']
  venue.image_link = request.form['image_link']
  venue.website = request.form['website_link']
  if 'seeking_talent' in request.form : seeking_talent = True 
  else : seeking_talent = False
  venue.seeking_description = request.form['seeking_description']
  
  try:
    db.session.add(venue)
    db.session.commit()
    # on successful
    flash('Artist ' + request.form['name'] + ' was successfully !')
  except:
    db.session.rollback()
    print(sys.exc_info())
    # on unsuccessful
    flash('An error occurred. Artist ' + request.form['name'])
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # insert form data as a new Venue record in the db, instead
  # modify data to be the data object returned from db insertion
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    image_link = request.form['image_link']
    website_link = request.form['website_link']
    if 'seeking_venue' in request.form : seeking_venue = True 
    else : seeking_venue = False
    seeking_description = request.form['seeking_description']
    try:
      artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link,
      image_link=image_link, website=website_link, seeking_venue=seeking_venue, seeking_description=seeking_description)
    
      db.session.add(artist)
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
      db.session.rollback()
      print(sys.exc_info())
      # on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    finally:
      db.session.close()
      return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # replace with real venues data.
  # num_shows should be aggregated based on number of upcoming shows per venue.

  data = []

  Shows = Show.query.join(Artist).join(Venue).all()
  for show in Shows: 
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name, 
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })


  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # insert form data as a new Show record in the db, instead
  artist_id = request.form['artist_id']
  venue_id = request.form['venue_id']
  start_time = request.form['start_time']

  try:
    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
      db.session.rollback()
      print(sys.exc_info())
      # on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Show could not be listed.')
  finally:
      db.session.close()
      return render_template('pages/home.html')


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
