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
        search_term = "%%%s%%" % search_term
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
@login_required
def user_booking_history():
    # Fetch bookings and events for the logged-in user
    bookings_with_events = db.session.query(Booking, Event).join(Event).filter(Booking.user_id == current_user.id).all()

    # Pass bookings and their corresponding events to the template
    return render_template('booking.html', bookings_with_events=bookings_with_events)
