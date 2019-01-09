from flask import Flask, render_template, request
from models import db, User
from forms import SignupForm
import os

POSTGRES = {
    'user': os.environ.get('USER'),
    'pw': os.environ.get('PASSWORD'),
    'db': os.environ.get('DB'),
    'host': 'postgres'
}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://%(user)s:%(pw)s@%(host)s/%(db)s' % POSTGRES
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
    form = SignupForm()

    if request.method == 'POST':
        if form.validate() == False:
            return render_template('signup.html', form=form)
        else:
            newuser = User(form.first_name.data, form.last_name.data, form.email.data, form.password.data)
            db.session.add(newuser)
            db.session.commit()
            return 'Success!'
    
    elif request.method == 'GET':
        return render_template('signup.html', form=form)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)