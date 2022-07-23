# imports
from concurrent.futures.process import _python_exit
import json
import sys
from sre_parse import State
from tokenize import Name
from unicodedata import name
import dateutil.parser
import babel
from flask import (Flask, jsonify, render_template, request,
                   Response, flash, redirect, url_for, abort)
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (Column, ForeignKey, Integer, Table)
from sqlalchemy.orm import (declarative_base, relationship)
import logging
from logging import (Formatter, FileHandler)
from flask_wtf import Form
from forms import *
from models import Venue, Artist, Show, db
from config import *
from datetime import datetime
import sys
from datetime import datetime


app = Flask(__name__)
db = SQLAlchemy(app)
app.config.from_object('config')
moment = Moment(app)
db.init_app(app)
migrate = Migrate(app, db)


# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:tamlin@localhost:5432/fyyur4'

# Filters


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

# ---------------------------------------------------------------------


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue
    locals = []
    venues = Venue.query.all()

    places = Venue.query.distinct(Venue.city, Venue.state).all()

    for place in places:
        locals.append({
            'city': place.city,
            'state': place.state,
            'venues': [{
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': len([show for show in venue.shows if show.start_time > datetime.now()])
            } for venue in venues if
                venue.city == place.city and venue.state == place.state]
        })
    return render_template('pages/venues.html', areas=locals)


@ app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    searchVenue = request.form.get("search_term", "")
    venues = Venue.query.filter(Venue.name.ilike(f'%{searchVenue}%')).all()
    count = Venue.query.filter(Venue.name.ilike(f'%{searchVenue}%')).count()

    def SearchVenue(venues):
        num_upcoming_shows = 0
        for show in venues.shows:
            if show.start_time > datetime.today():
                num_upcoming_shows += 1

        d = {
            "id": venues.id,
            "name": venues.name,

        }
        return d

    response = {
        "count": count,
        "data": [SearchVenue(venue) for venue in venues]
    }
    print(response)
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    # data = Venue.query.get_or_404(venue_id)
    venue = Venue.query.get(venue_id)
    if (venue.genres == None):
        venue.genres = []
    if (venue == None):
        abort(404)

    def VenueDetails(details):
        show = details[0]
        artist = details[1]
        data = {
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(show.start_time)
        }
        return data
    past_shows = db.session.query(Show, Artist).join(Artist).filter(
        Show.start_time <= datetime.today(), Show.venue_id == venue_id).all()
    upcoming_shows = db.session.query(Show, Artist).join(Artist).filter(
        Show.start_time > datetime.today(), Show.venue_id == venue_id).all()
    past_shows_count = db.session.query(Show).join(Venue).filter(
        Show.start_time <= datetime.today()).filter(Show.venue_id == venue_id).count()
    upcoming_shows_count = db.session.query(Show).join(Venue).filter(
        Show.start_time > datetime.today()).filter(Show.venue_id == venue_id).count()

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website_link": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": [VenueDetails(show) for show in past_shows],
        "upcoming_shows": [VenueDetails(show) for show in upcoming_shows],
        "past_shows_count": past_shows_count,
        "upcoming_shows_count": upcoming_shows_count,
    }
    print(venue.genres)

    #venue = Venue.query.get_or_404(venue_id)

    #past_shows = []
    #upcoming_shows = []

    # for show in venue.shows:
    #    temp_show = {
    #        'artist_id': show.artist_id,
    #        'artist_name': show.artist.name,
    #        'artist_image_link': show.artist.image_link,
    #        'start_time': show.start_time.strftime("%M/%D/%Y, %H:%M")
    #    }
    #    if show.start_time <= datetime.now():
    #        past_shows.append(temp_show)
    #    else:
    #        upcoming_shows.append(temp_show)


# object class to dict
    #data = vars(venue)

    #data['past_shows'] = past_shows
    #data['upcoming_shows'] = upcoming_shows
    #data['past_shows_count'] = len(past_shows)
    #data['upcoming_shows_count'] = len(upcoming_shows)

    # return render_template('pages/show_venue.html', venue=data)

# create--------------------


@ app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@ app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = VenueForm(request.form)
    error = False
    try:
        venue = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            genres=form.genres.data,
            image_link=form.image_link.data,
            facebook_link=form.facebook_link.data,
            website_link=form.website_link.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data
        )

        db.session.add(venue)
        db.session.commit()

    # TODO: on unsuccessful db insert, flash an error instead.
    except Exception as e:
        error = True
        db.session.rollback()
        print(e)
    finally:
        db.session.close()
        if error:
            flash('Venue ' + request.form['name'] +
                  ' could not be created !!!')
        if not error:
            flash('Venue ' + request.form['name'] +
                  ' was successfully created !!!')
        # return redirect(url_for('index'))
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        return redirect(url_for('index'))


@ app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    try:
        db.session.query(Show).filter_by(venue_id=venue_id).delete()
        db.session.query(Venue).filter_by(id=venue_id).delete()
        db.session.commit()
    except Exception as e:
        print(f'Error ==> {e}')
        flash('ERROR:Venue could not be deleted.')
        db.session.rollback()
        abort(400)
    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------


@ app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database

    locals = []
    artists = db.session.query(Artist).order_by(Artist.name).all()
    for artist in artists:
        artist = dict(zip(('id', 'name'), artist))
        locals.append(artist)

    return render_template('pages/artists.html', artists=locals)


@ app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    getArtists = request.form.get("search_term", "")
    artists = Artist.query.filter(
        Artist.name.like(f'%{getArtists}%')).all()

    def SearchArtist(artists):
        num_upcoming_shows = 0
        for show in artists.shows:
            if show.start_time > datetime.today():
                num_upcoming_shows += 1

        data = {
            "id": artists.id,
            "name": artists.name,
            "num_upcoming_shows": []}
        return data

    response = {

        "data": [SearchArtist(artist) for artist in artists]

    }
    print(response)

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id

    artist = Artist.query.get(artist_id)
    if (artist.genres == None):
        artist.genres = []
    if (artist == None):
        abort(404)

    def ArtistDetail(details):
        show = details[0]
        venue = details[1]
        data = {
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": str(show.start_time)
        }
        return data

    artist = Artist.query.get(artist_id)
    past_shows = db.session.query(Show, Venue).join(Venue).filter(
        Show.start_time <= datetime.today(), Show.artist_id == artist_id).all()
    upcoming_shows = db.session.query(Show, Venue).join(Venue).filter(
        Show.start_time > datetime.today(), Show.artist_id == artist_id).all()
    past_shows_count = Show.query.filter(
        Show.start_time <= datetime.today(), Show.artist_id == artist_id).count()
    upcoming_shows_count = Show.query.filter(
        Show.start_time > datetime.today(), Show.artist_id == artist_id).count()
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": [ArtistDetail(show) for show in past_shows],
        "upcoming_shows": [ArtistDetail(show) for show in upcoming_shows],
        "past_shows_count": past_shows_count,
        "upcoming_shows_count": upcoming_shows_count
    }

    if artist == None:
        abort(404)

    return render_template('pages/show_artist.html', artist=data)

    #artist = Artist.query.get_or_404(artist_id)

    #past_shows = []
    #upcoming_shows = []

    # for show in artist.shows:
    #    temp_show = {
    #        'artist_id': show.artist_id,
    #        'artist_name': show.artist.name,
    #        'artist_image_link': show.artist.image_link,
    #        'start_time': show.start_time.strftime("%M/%D/%Y, %H:%M")
    #    }
    #    if show.start_time <= datetime.now():
    #        past_shows.append(temp_show)
    #    else:
    #       upcoming_shows.append(temp_show)

# object class to dict
    #data = vars(artist)

    #data['past_shows'] = past_shows
    #data['upcoming_shows'] = upcoming_shows
    #data['past_shows_count'] = len(past_shows)
    #data['upcoming_shows_count'] = len(upcoming_shows)

    # return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------


@ app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    if request.method == 'GET':
        request.form.get('name')
        request.form.get('city')
        request.form.get('state')
        request.form.get('address')
        request.form.get('phone')
        request.form.getlist('genres')
        request.form.get('facebook_link')
        request.form.get('image_link')
        request.form.get('website_link')
        request.form.get('seeking_venue')
        request.form.get('seeking_description')

    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form)


@ app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    try:
        form = ArtistForm()
        artist = Artist.query.get_or_404(artist_id)
        name = request.form.get['Name']
        city = request.form.get['City']
        state = request.form.get['state']
        phone = request.form.get['Phone']
        genres = request.form.getlist['Genres']
        facebook_link = request.form.get['Facebook_link']
        image_link = request.form.get['Image_link']
        website_link = request.form.get['website_link']
        seeking_venues = request.form.get['Looking_for_venues']
        seeking_description = request.form.get['seeking_description']

        artist.name = name
        artist.city = city
        artist.state = state
        artist.phone = phone
        artist.genres = genres
        artist.facebook_link = facebook_link
        artist.image_link = image_link
        artist.website_link = website_link
        artist.seeking_venues = seeking_venues
        artist.seeking_discription = seeking_description

        db.session.add(artist)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        flash('Artist could not be updated')
    finally:
        db.session.close()
        flash('Artist was Successfully Updated')
    return redirect(url_for('show_artist', artist_id=artist_id, form=form))


@ app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

    form = VenueForm()
    if request.method == 'GET':
        request.form.get('name')
        request.form.get('city')
        request.form.get('state')
        request.form.get('address')
        request.form.get('phone')
        request.form.get('image_link')
        request.form.getlist('genres')
        request.form.get('facebook_link')
        request.form.get('website_link')
        request.form.get('seeking_talent')
        request.form.get('seeking_description')

    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form)


@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm
    try:
        venue = Venue.query.get(venue_id)
        venue.name = request.json.get('name', venue.name)
        venue.city = request.json.get('city', venue.city)
        venue.state = request.json.get('state', venue.state)
        venue.address = request.json.get('address', venue.address)
        venue.phone = request.json.get('phone', venue.phone)
        venue.genres = request.json.getlist('genres', venue.genres)
        venue.facebook_link = request.json.get(
            'facebook_link', venue.facabook_link)
        venue.image_link = request.json.get('image_link', venue.image_link)
        venue.website_link = request.json.get(
            'website_link', venue.website_link)
        venue.seeking_talent = request.json.get(
            'seeking_tale', venue.seeking_talent)
        venue.seeking_desscription = request.json.get(
            'seeking_description', venue.seeking_description)

        db.session.add(venue)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        flash('Venue could not be updated!!')
    finally:
        db.session.close()
        flash('Venue was successfully updated!!')

    # return jsonify(venue.to_json())

    return render_template('forms/edit_venue.html', venue_id=venue_id, form=form)

#  Create Artist
#  ----------------------------------------------------------------


@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    error = False
    form = ArtistForm(request.form)

    try:
        new_artist = Artist(
            name=form.name.data['name'],
            city=form.city.data['city'],
            state=form.state.data['state'],
            phone=form.phone.data['phone'],
            image_link=form.image_link.data['image_link'],
            genres=form.genres.data['genres'],
            facebook_link=form.facebook_link.data['facebook_link'],
            website_link=form.website_link.data['website_link'],
            seeking_venue=True if 'seeking_venue' in request.form else False,
            seeking_description=form.seeking_description.data['seeking_description']
        )

        db.session.add(new_artist)
        db.session.commit()

    # TODO: on unsuccessful db insert, flash an error instead.
    except Exception as e:
        error = True
        db.session.rollback()
        print(e)
    finally:
        db.session.close()
        if error:
            flash('Artist ' + request.form['name'] +
                  ' could not be created!!!')
        if not error:
            flash('Artist ' + request.form['name'] +
                  ' was successfully created!!!')
        # on successful db insert, flash success
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------)


@ app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    def displayShows(result):
        data = []
        for show in result:
            data.append({
                "venue_id": show.venue.id,
                "venue_name": show.venue.name,
                "artist_id": show.artist.id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": str(show.start_time)
            })
        return (data)
    data = []
    try:
        shows = Show.query.order_by(Show.start_time).all()
        data = displayShows(shows)
    finally:
        return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    # on successful db insert, flash success
    error = False
    form = ShowForm()
    try:
        new_show = Show(
            artist_id=form.artist_id.data['artist_id'],
            venue_id=form.venue_id.data['venue_id'],
            start_time=form.start_time.data['start_time']
        )

        db.session.add(new_show)
        db.session.commit()
    except Exception as e:
        error = True
        db.session.rollback()
        print(e)
    finally:
        db.session.close()
        if error:
            flash('Show ' +
                  request.form['artist_id'] + 'could not be created!!!')
        if not error:
            flash('Show ' + request.form['artist_id'] +
                  'could successfully be created!!!')
        # flash('Show' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/show/search', methods=['POST', 'GET'])
def search_show():
    form = ShowForm()
    search_Show = request.form.get('search_term', '')
    shows = Show.query.filter(
        Show.name.ilike(f'%{search_Show}%')).all()
    count = Show.query.filter(
        Show.name.ilike(f'%{search_Show}%')).count()

    def SearchShow(artists):
        num_upcoming_shows = 0
        for show in artists.shows:
            if show.start_time > datetime.today():
                num_upcoming_shows += 1

        data = {
            "id": show.id,
            "name": show.name,
            "num_upcoming_shows": artists.num_upcoming_shows
        }
        return data

    response = {
        "count": count,
        "data": [SearchShow(shows) for show in shows]
    }
    print(response)
    return render_template('pages/show.html', form=form, results=response, search_term=request.form.get('search_term', ''))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
