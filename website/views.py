from flask import Blueprint, render_template, request, redirect, url_for
from .models import Event, Booking
from . import db
from flask_login import login_required, current_user
from sqlalchemy import or_

mainbp = Blueprint('main', __name__)

@mainbp.route('/')
def index():
    events = db.session.scalars(db.select(Event)).all()
    return render_template('index.html', events=events)

@mainbp.route('/search')
def search():
    search_term = request.args.get('search')
    if search_term:
        search_term = "%%%s%%" % search_term  # This is an alternative way to format the string with the search term
        events = db.session.scalars(
            db.select(Event).where(
                or_(
                    Event.title.like(search_term),
                    Event.description.like(search_term),
                    Event.genre.like(search_term),
                    Event.artist_or_band.like(search_term)
                )
            )
        ).all()
        return render_template('index.html', events=events)
    else:
        return redirect(url_for('main.index'))

@mainbp.route('/user_booking_history')
@login_required  # Ensure user is logged in to view this page
def user_booking_history():
    # Fetch events booked by the logged-in user
    booked_events = db.session.scalars(
        db.select(Event).join(Booking, Booking.event_id == Event.id).where(Booking.user_id == current_user.id)
    ).all()
    return render_template('booking.html', events=booked_events)
