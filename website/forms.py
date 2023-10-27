from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField, SubmitField, StringField, PasswordField, DateTimeField, IntegerField
from wtforms.validators import InputRequired, Email, EqualTo, Length
from flask_wtf.file import FileRequired, FileField, FileAllowed

ALLOWED_FILE = {'PNG', 'JPG', 'JPEG', 'png', 'jpg', 'jpeg'}

#creates the login information
class LoginForm(FlaskForm):
    user_name=StringField("User Name", validators=[InputRequired('Enter user name')])
    password=PasswordField("Password", validators=[InputRequired('Enter user password')])
    submit = SubmitField("Login")

 # this is the registration form
class RegisterForm(FlaskForm):
    user_name=StringField("User Name", validators=[InputRequired()])
    email_id = StringField("Email Address", validators=[Email("Please enter a valid email")])
    #linking two fields - password should be equal to data entered in confirm
    password=PasswordField("Password", validators=[InputRequired(),
                  EqualTo('confirm', message="Passwords should match")])
    confirm = PasswordField("Confirm Password")

    #submit button
    submit = SubmitField("Register")

class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[InputRequired()])
    genre = StringField('Genre')
    artist_or_band = StringField('Artist/Band Name', validators=[InputRequired()])
    location = StringField('Location', validators=[InputRequired()])
    start_date = DateTimeField('Start Date', format='%Y-%m-%d %H:%M:%S', validators=[InputRequired()])
    end_date = DateTimeField('End Date', format='%Y-%m-%d %H:%M:%S', validators=[InputRequired()])
    description = TextAreaField('Description', validators=[InputRequired(), Length(max=500)])
    ticket_count = IntegerField('Ticket Count', validators=[InputRequired()])
    venue = StringField('Event Venue', validators=[InputRequired()])

    image = FileField('Event Image', validators=[
        FileRequired(message='Image cannot be empty'),
        FileAllowed(ALLOWED_FILE, message='Only supports PNG, JPG, png, jpg')
    ])
    submit = SubmitField("Create Event")

#User comment
class CommentForm(FlaskForm):
  text = TextAreaField('Comment', [InputRequired()])
  submit = SubmitField('Create')

#User booking
class BookingForm(FlaskForm):
    quantity = IntegerField('Number of Tickets', validators=[InputRequired(message='Please specify the number of tickets you want to book.')])
    submit = SubmitField('Book Now')
