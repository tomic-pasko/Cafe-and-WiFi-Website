from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, URL, ValidationError
import csv
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['S_VAR']
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

##User table in cafes db
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

##Cafe table in cafes db
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True)
    map_url = db.Column(db.String(500))
    img_url = db.Column(db.String(500))
    location = db.Column(db.String(250))
    has_sockets = db.Column(db.Boolean)
    has_toilet = db.Column(db.Boolean)
    has_wifi = db.Column(db.Boolean)
    can_take_calls = db.Column(db.Boolean)
    seats = db.Column(db.String(250))
    coffee_price = db.Column(db.String(250))
    coffee_rating = db.Column(db.String(250))
    wifi_rating = db.Column(db.String(250))
    power_rating = db.Column(db.String(250))

##Line below only required once, when creating db
#db.create_all()

Bootstrap(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class CafeForm(FlaskForm):
    cafe = StringField(label='Cafe name', validators=[DataRequired()])
    map_url = StringField(label='Cafe location on Google Maps (URL)', validators=[DataRequired(), URL()])
    img_url = StringField(label='Cafe image (URL)', validators=[DataRequired(), URL()])
    # open_time = StringField(label='Opening Time e.g. 5AM', validators=[DataRequired()])
    # closing_time = StringField(label='Closing Time e.g. 5PM', validators=[DataRequired()])
    location = StringField(label='Name of Cafe location', validators=[DataRequired()])
    has_sockets = BooleanField(label='Sockets available')
    has_toilet = BooleanField(label='Toilet available')
    has_wifi = BooleanField(label='WiFi available')
    can_take_calls = BooleanField(label='Can take calls')

    seats = StringField(label='Number of seats', validators=[DataRequired()])
    coffee_price = StringField(label='Coffee price', validators=[DataRequired()])
    coffee_rating = SelectField(label='Coffee Rating', choices=['☕', '☕☕', '☕☕☕', '☕☕☕☕', '☕☕☕☕☕'],
                                validators=[DataRequired()])
    wifi_rating = SelectField(label='WiFi Signal Strength', choices=['✘', '💪', '💪💪', '💪💪💪', '💪💪💪💪', '💪💪💪💪💪'],
                              validators=[DataRequired()])
    power_outlet_rating = SelectField(label='Power Socket availability',
                                      choices=['✘', '🔌', '🔌🔌', '🔌🔌🔌', '🔌🔌🔌🔌', '🔌🔌🔌🔌🔌'],
                                      validators=[DataRequired()])
    submit = SubmitField('Submit')


# all Flask routes below
@app.route("/")
def home():
    return render_template("index.html")


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        print("True")

        new_cafe = Cafe(
            name=form.cafe.data,
            map_url=form.map_url.data,
            img_url=form.img_url.data,
            location=form.location.data,
            has_sockets=form.has_sockets.data,
            has_toilet=form.has_toilet.data,
            has_wifi=form.has_wifi.data,
            can_take_calls=form.can_take_calls.data,
            seats=form.seats.data,
            coffee_price=form.coffee_price.data,
            coffee_rating=form.coffee_rating.data,
            wifi_rating=form.wifi_rating.data,
            power_rating=form.power_outlet_rating.data
        )

        db.session.add(new_cafe)
        db.session.commit()

        return redirect(url_for('cafes'))

    return render_template('add.html', form=form)


@app.route('/cafes')
def cafes():
    cafe_list = []

    ##Db to list of dict
    all_cafes = db.session.query(Cafe).all()
    for i in range(len(all_cafes)):
        cafe_list.append(Cafe.query.get(i+1).__dict__)

    # return render_template('cafes.html', cafes=list_of_rows, len=length)
    return render_template('cafes.html', cafes=cafe_list)

# TODO: Handle Email Confirmation During Registration

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        plain_pass = request.form.get('password')
        ##Hashed and salted password
        hash_pass = generate_password_hash(plain_pass, method='pbkdf2:sha256', salt_length=8)

        user = User(
            email=request.form.get('email'),
            password=hash_pass,
            name=request.form.get('name')
        )

        db.session.add(user)
        db.session.commit()

        #Log in and authenticate user after adding details to database.
        login_user(user)
        return render_template('index.html')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')

        #Find user by email
        user = User.query.filter_by(email=email).first()

        #Flash user if wrong email was entered
        if user is None:
            error = 'That email does not exist'
        else:
            # Check stored password hash against entered password that is going to be hashed
            if check_password_hash(user.password, request.form.get('password')):
                # Login user after verifying password in db
                login_user(user)
                return redirect(url_for('cafes'))
            else:
                error = 'Wrong password'
    return render_template('login.html', error_msg=error)


@app.route('/logout')
def logout():
    logout_user()
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)
