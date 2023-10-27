from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Event, Comment, Booking
from .forms import EventForm, CommentForm, BookingForm
from . import db
import os
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user

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
            title=form.title.data,
            genre=form.genre.data,
            artist_or_band=form.artist_or_band.data,
            location=form.location.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            description=form.description.data,
            ticket_count=form.ticket_count.data,
            venue=form.venue.data,
            image_paths=db_file_path
        )
        db.session.add(event)
        db.session.commit()
        flash('Successfully created new event', 'success')
        return redirect(url_for('events.create'))
    return render_template('events/create.html', form=form)

def check_upload_file(form):
    fp = form.image.data
    filename = fp.filename
    BASE_PATH = os.path.dirname(__file__)
    upload_path = os.path.join(BASE_PATH, 'static/image', secure_filename(filename))
    db_upload_path = '/static/image/' + secure_filename(filename)
    fp.save(upload_path)
    return db_upload_path

@eventsbp.route('/<id>/comment', methods=['GET', 'POST'])
@login_required
def comment(id):
    form = CommentForm()
    event = db.session.scalar(db.select(Event).where(Event.id==id))
    if form.validate_on_submit():
        comment = Comment(text=form.text.data, event=event, user=current_user)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added', 'success')
    return redirect(url_for('events.show', id=id))

@eventsbp.route('/<id>/book', methods=['POST'])
@login_required
def book(id):
    form = BookingForm()
    event = db.session.scalar(db.select(Event).where(Event.id==id))
    if form.validate_on_submit():
        booking = Booking(quantity=form.quantity.data, user=current_user, event=event)
        db.session.add(booking)
        db.session.commit()
        flash(f'Successfully booked {form.quantity.data} tickets for {event.title}', 'success')
    return redirect(url_for('events.show', id=id))
