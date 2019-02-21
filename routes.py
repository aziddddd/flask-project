from flask import Flask, render_template, request, session, redirect, url_for
from models import db, User, Place
from forms import SignupForm, LoginFrom, AddressFrom
import os
import json

# Declare port for Heroku deployment enabled
port = int(os.environ.get('PORT', 5000))

POSTGRES = {
    'user': os.environ.get('USER'),
    'pw': os.environ.get('PASSWORD'),
    'db': os.environ.get('DB'),
    'host': 'postgres'
}

app = Flask(__name__)

# Local run
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://%(user)s:%(pw)s@%(host)s/%(db)s' % POSTGRES

# Heroku run
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://sukmosdzsfjdkz:775b72a705ad601dc0f5fb849715ff2dec0068c66c33c75fc2ecc08dfb3a97be@ec2-23-21-86-22.compute-1.amazonaws.com:5432/dcjmemhhl4qnci'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

app.secret_key = 'development-key'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'email' in session:
        return redirect(url_for('home'))
    form = SignupForm()

    if request.method == 'POST':
        # Validate the submitted signup form
        if form.validate() == False:
            return render_template('signup.html', form=form)
        else:
            newuser = User(form.first_name.data, form.last_name.data, form.email.data, form.password.data)
            db.session.add(newuser)
            db.session.commit()

            # Create a session
            session['email'] = newuser.email
            return redirect(url_for('home'))
    
    elif request.method == 'GET':
        return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'email' in session:
        return redirect(url_for('home'))

    form = LoginFrom()

    if request.method == 'POST':
        # Validate the submitted login form
        if form.validate() == False:
            render_template('login.html', form=form)
        else:
            email = form.email.data
            password = form.password.data

            # Check whether user's data exist in our database
            user = User.query.filter_by(email=email).first()
            if user is not None and user.check_password(password):
                # Create a session
                session['email'] = form.email.data
                return redirect(url_for('home'))
            else:
                return redirect(url_for('login'))
    
    elif request.method == 'GET':
        return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    if 'email' not in session:
        return redirect(url_for('login'))
    session.pop('email', None)
    return redirect(url_for('index'))

@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'email' not in session:
        return redirect(url_for('login'))

    form = AddressFrom()
    places = []
    my_coordinates = (37.4221, -122.0844)

    if request.method == 'POST':
        if form.validate() == False:
            return render_template('home.html', form=form)
        else:
            # Get the address
            address = form.address.data

            # Query for places around the address
            p = Place()
            my_coordinates = p.address_to_latlng(address)
            places = p.query(address)
            return render_template('home.html', form=form, my_coordinates=my_coordinates, places=places)

    elif request.method == 'GET':
        return render_template('home.html', form=form, my_coordinates=my_coordinates, places=places)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=port)