from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask import jsonify
from datetime import datetime
import os
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'




# quran verse stock
quran_verses = [
    {"text": "Indeed, with hardship comes ease.", "surah": "Al-Inshirah", "ayah": 6},
    {"text": "And Allah is Forgiving and Merciful.", "surah": "Al-Baqarah", "ayah": 173},
    {"text": "Do not despair of the mercy of Allah.", "surah": "Az-Zumar", "ayah": 53},
    {"text": "And We have certainly made the Quran easy for remembrance, so is there any who will remember?", "surah": "Al-Qamar", "ayah": 17},
    {"text": "So remember Me; I will remember you.", "surah": "Al-Baqarah", "ayah": 152},
    {"text": "Indeed, Allah does not burden a soul beyond that it can bear.", "surah": "Al-Baqarah", "ayah": 286},
    {"text": "And He found you lost and guided you.", "surah": "Ad-Duhaa", "ayah": 7},
    {"text": "My mercy encompasses all things.", "surah": "Al-A'raf", "ayah": 156},
    {"text": "And We have not sent you, [O Muhammad], except as a mercy to the worlds.", "surah": "Al-Anbiya", "ayah": 107},
    {"text": "Indeed, prayer prohibits immorality and wrongdoing.", "surah": "Al-Ankabut", "ayah": 45},
    {"text": "Indeed, the patient will be given their reward without account.", "surah": "Az-Zumar", "ayah": 10},
    {"text": "Call upon Me; I will respond to you.", "surah": "Ghafir", "ayah": 60},
    {"text": "And He is with you wherever you are.", "surah": "Al-Hadid", "ayah": 4},
    {"text": "Whoever puts their trust in Allah, He will be enough for them.", "surah": "At-Talaq", "ayah": 3},
    {"text": "And those who strive for Us - We will surely guide them to Our ways.", "surah": "Al-Ankabut", "ayah": 69}
]







# Modèle Utilisateur
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)

# Modèle de récitation du Coran
class QuranRecitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    reciter = db.Column(db.String(100), nullable=False)
    surah = db.Column(db.String(100))
    link = db.Column(db.String(500), nullable=False)  
    mood_id = db.Column(db.Integer, db.ForeignKey('mood.id'))

# Mood Model  
class Mood(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    recitations = db.relationship('QuranRecitation', backref='mood', lazy=True)




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))




@app.route('/')
def home():
    return render_template('index.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('dashboard'))
        else:
            flash('Échec de la connexion. Vérifiez votre nom d\'utilisateur et mot de passe.', 'danger')
    
    return render_template('login.html')




@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        first_name = request.form.get('first_name', '')
        last_name = request.form.get('last_name', '')
        
        
        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            flash('Le nom d\'utilisateur ou l\'email existe déjà.', 'danger')
            return redirect(url_for('register'))
            
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_password, 
                   first_name=first_name, last_name=last_name)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Votre compte a été créé ! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')




@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))



@app.route('/dashboard')
@login_required
def dashboard():
    moods = Mood.query.all()
    verse = random.choice(quran_verses)
    return render_template('dashboard.html', verse=verse,user=current_user)





@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)




@app.route('/choose_mood')
@login_required
def choose_mood():
    return render_template('choose_mood.html')




@app.route('/recommend', methods=['GET','POST'])
@login_required
def recommend():
    mood = request.form.get('mood')
    
    
    recitation = None
    link = None
    
    if mood == 'peaceful':
        recitation = "Peaceful Quran Recitation for you"
        link = "https://www.youtube.com/watch?v=MXfk8QbgAeU"
    elif mood == 'stressed':
        recitation = "Stressed Quran Recitation for you"
        link = "https://www.youtube.com/watch?v=LPpYmqb8ug4"
    elif mood == 'sad':
        recitation = "Sad Quran Recitation for you"
        link = "https://www.youtube.com/watch?v=ROWSGdQR1D8"
    elif mood == 'focused':
        recitation = "Focused Quran Recitation for you"
        link = "https://www.youtube.com/watch?v=rC0xbs-zmUg"
    
    return render_template('choose_mood.html', user=current_user, recitation=recitation, link=link)







with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)


