from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .models import Event, User, Booking  # Assuming Booking relates User with Event
from . import db
from flask_login import login_required, current_user  # Assuming you're using Flask-Login for user management

mainbp = Blueprint('main', __name__)

@mainbp.route('/')
def index():
    events = db.session.scalars(db.select(Event)).all()
    return render_template('index.html', events=events)

@mainbp.route('/search')
def search():
    if request.args['search'] and request.args['search'] != "":
        query = "%" + request.args['search'] + "%"
        events = db.session.scalars(db.select(Event).where(Event.description.like(query)))
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
