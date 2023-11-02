from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Event, Comment, Booking
from .forms import EventForm, CommentForm, BookingForm
from . import db
import os
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from datetime import datetime

eventsbp = Blueprint('events', __name__, url_prefix='/events')

@eventsbp.route('/<id>')
def show(id):
    event = db.session.scalar(db.select(Event).where(Event.id==id))
    comment_form = CommentForm()
    booking_form = BookingForm()
    return render_template('events/show.html', event=event, comment_form=comment_form, booking_form=booking_form)

@eventsbp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = EventForm()
    if form.validate_on_submit():
        db_file_path = check_upload_file(form)
        event = Event(
            creator_id=current_user.id,
            title=form.title.data,
            genre=form.genre.data,
            artist_or_band=form.artist_or_band.data,
            location=form.location.data,
            event_date=form.event_date.data,
            description=form.description.data,
            ticket_count=form.ticket_count.data,
            venue=form.venue.data,
            image_path=db_file_path
        )
        db.session.add(event)
        db.session.commit()
        flash('Successfully created new event', 'success')
        return redirect(url_for('events.show', id=event.id))
    return render_template('events/create.html', form=form)

def check_upload_file(form):
    fp = form.image.data
    filename = fp.filename
    BASE_PATH = os.path.dirname(__file__)
    upload_path = os.path.join(BASE_PATH, 'static/image', secure_filename(filename))
    db_upload_path = 'image/' + secure_filename(filename)
    fp.save(upload_path)
    return db_upload_path


@eventsbp.route('/<id>/comment', methods=['GET', 'POST'])
@login_required
def comment(id):
    form = CommentForm()
    # No need to load the event if you're only using the ID
    if form.validate_on_submit():
        # Create a comment with the event_id and user_id
        comment = Comment(text=form.text.data, event_id=id, user_id=current_user.id)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added', 'success')
    return redirect(url_for('events.show', id=id))



@eventsbp.route('/<id>/book', methods=['POST'])
@login_required
def book(id):
    form = BookingForm()
    event = Event.query.get(id)  # Adjusted to a simpler query method
    if form.validate_on_submit():
        # Check if enough tickets are available
        if event.ticket_count >= form.quantity.data:
            # Update the ticket count
            event.ticket_count -= form.quantity.data

            # Check if event is sold out
            if event.ticket_count == 0:
                event.status = 'Sold Out'

            # Create booking
            order_id = f"{id}-{current_user.id}-{int(datetime.now().timestamp())}"
            booking = Booking(quantity=form.quantity.data, user_id=current_user.id, event_id=id, order_id=order_id)
            db.session.add(booking)
            db.session.commit()
            flash(f'Successfully booked {form.quantity.data} tickets for event id {id}', 'success')
        else:
            flash(f'Sorry, only {event.ticket_count} tickets are available for this event.', 'danger')
    return redirect(url_for('events.show', id=id))

@eventsbp.route('/genre/<genre>', methods=['GET'])
def filter_by_genre(genre):
    if genre == 'All':
        filtered_events = Event.query.all()
    else:
        filtered_events = Event.query.filter_by(genre=genre).all()

    return render_template('index.html', events=filtered_events)

@eventsbp.route('/<id>/cancel', methods=['POST'])
@login_required
def cancel(id):
    event = Event.query.get(id)
    if event and current_user.id == event.creator_id:  # Assume event has a creator_id field
        event.status = 'Canceled'
        db.session.commit()
        flash('The event has been canceled.', 'success')
    else:
        flash('You do not have permission to cancel this event.', 'danger')
    return redirect(url_for('events.show', id=id))
