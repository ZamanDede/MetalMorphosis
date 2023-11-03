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
    event = db.session.scalar(db.select(Event).where(Event.id == id))
    if event and datetime.now() > event.event_date and event.status != 'Inactive':
        event.status = 'Inactive'
        db.session.commit()

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
            image_path=db_file_path,
            status='Open'
        )
        current_time = datetime.now().date()
        # Check if the event date is in the past
        if current_time > event.event_date:
            event.status = 'Inactive'
        db.session.add(event)
        db.session.commit()
        flash('Successfully created new event', 'success')
        return redirect(url_for('events.show', id=event.id))
    return render_template('events/create.html', form=form)

@eventsbp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    event = Event.query.get_or_404(id)

    # Ensure that the current user is the creator of the event
    if current_user.id != event.creator_id:
        flash("You do not have permission to edit this event.", "danger")
        return redirect(url_for('events.show', id=id))

    form = EventForm(obj=event)

    if form.validate_on_submit():
        if datetime.now().date() > form.event_date.data:
            flash('Cannot update the event with a past date.', 'danger')
            return redirect(url_for('events.edit_event', id=id))

        # Assign form data to the event fields
        event.title = form.title.data
        event.genre = form.genre.data
        event.artist_or_band = form.artist_or_band.data
        event.location = form.location.data
        event.event_date = form.event_date.data
        event.description = form.description.data
        event.ticket_count = form.ticket_count.data
        event.venue = form.venue.data
        if form.image.data:
            event.image_path = check_upload_file(form)

        # Update the database with the new details
        db.session.commit()
        flash('Event updated successfully.', 'success')
        return redirect(url_for('events.show', id=id))

    return render_template('events/edit.html', form=form, event=event)



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
    event = Event.query.get(id)

    if form.validate_on_submit():
        # Check if the event status is not 'Open'
        if event.status != 'Open':
            flash(f'This event is currently {event.status}.', 'danger')
            return redirect(url_for('events.show', id=id))

        # Check for positive ticket quantity
        if form.quantity.data <= 0:
            flash('You cannot book a negative number of tickets.', 'danger')
            return redirect(url_for('events.show', id=id))

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
            flash(f'Successfully booked {form.quantity.data} tickets for event {event.title}.', 'success')
        else:
            flash(f'Sorry, only {event.ticket_count} tickets are available for this event.', 'danger')
    else:
        for error in form.errors.values():
            flash(' '.join(error), 'danger')

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
    if event and current_user.id == event.creator_id:
        event.status = 'Canceled'
        db.session.commit()
        flash('The event has been canceled.', 'success')
    else:
        flash('You do not have permission to cancel this event.', 'danger')
    return redirect(url_for('events.show', id=id))
