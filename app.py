
import os
import logging

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash, check_password_hash


logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1) # needed for url_for to generate with https


# Configure MySQL database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", 
    "mysql+pymysql://root:1234@localhost/legalbuddy"
)
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
# initialize the app with the extension, flask-sqlalchemy >= 3.0.x
db.init_app(app)

# Create a models.py file with your database models
# Here's what the models.py file should contain:
"""
from datetime import datetime
from app import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with chat messages
    messages = db.relationship('ChatMessage', backref='user', lazy=True)

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
"""

with app.app_context():
    # Make sure to import the models here or their tables won't be created
    import models  # noqa: F401
    db.create_all()

# Routes
@app.route('/templates/index')
def index():
    return render_template('index.html')

# Fix the duplicate chat route
@app.route('/templates/chat')
def chat():
    if 'user_id' not in session:
        flash('Please log in to access the chat', 'warning')
        return redirect(url_for('login'))

    username = session.get('username', 'Guest')  # <-- retrieve username
    return render_template('chat.html', username=username)


@app.route('/templates/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = models.User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            print("Set session username:", session.get('username'))
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        
        flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/templates/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required', 'danger')
            return render_template('signup.html')
            
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('signup.html')
            
        # Check if user already exists
        existing_user = models.User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists', 'danger')
            return render_template('signup.html')
            
        existing_email = models.User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already exists', 'danger')
            return render_template('signup.html')
            
        # Create new user
        new_user = models.User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('index'))
        
    return render_template('signup.html')

@app.route('/templates/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/api/chat', methods=['POST'])
def process_message():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    message = data.get('message', '')
    
    # Simple response logic for cyber law queries
    response = generate_cyber_law_response(message)
    
    # Save chat message to database
    user_id = session.get('user_id')
    new_message = models.ChatMessage(
        user_id=user_id,
        message=message,
        response=response
    )
    db.session.add(new_message)
    db.session.commit()
    
    return jsonify({
        "response": response
    })

def generate_cyber_law_response(query):
    """Generate a response based on the cyber law query"""
    query = query.lower()
    
    # Pre-defined responses for common cyber law questions
    responses = {
        "what is cyber law": "Cyber law refers to the legal issues related to the use of the internet, computers, and technology. It covers areas such as data protection, privacy, electronic commerce, intellectual property, and cybercrime.",
        
        "what is cybercrime": "Cybercrime refers to criminal activities carried out using computers and the internet. This includes hacking, phishing, identity theft, online fraud, cyber stalking, and distribution of illegal content.",
        
        "data protection": "Data protection laws regulate how personal data should be collected, processed, and stored. They aim to protect individuals' privacy and give them control over their personal information. Key regulations include GDPR in Europe and various data protection acts worldwide.",
        
        "intellectual property online": "Digital intellectual property includes copyrights for online content, trademarks for domain names and digital brands, and patents for software innovations. Infringement occurs through unauthorized use, distribution, or reproduction of protected material.",
        
        "online privacy rights": "Online privacy rights include the right to control personal data, be informed about data collection, access collected data, request data deletion, and object to certain processing activities. Privacy laws aim to protect these rights.",
        
        "hacking consequences": "Unauthorized access to computer systems (hacking) is a criminal offense in most jurisdictions. Penalties can include fines and imprisonment, with severity depending on the intent, damage caused, and targeted systems.",
        
        "gdpr": "The General Data Protection Regulation (GDPR) is a comprehensive EU data protection law that came into effect in 2018. It gives individuals control over their personal data and standardizes data protection laws across EU member states.",
        
        "digital signature legality": "Digital signatures are legally recognized in many countries through legislation like the Electronic Signatures in Global and National Commerce Act (ESIGN) in the US and the eIDAS Regulation in the EU. They're legally binding for most contracts and documents."
    }
    
    # Check if any key phrases match the query
    for key, response in responses.items():
        if key in query:
            return response
    
    # Default responses for general questions
    if "hello" in query or "hi" in query or "hey" in query:
        return "Hello! I'm your Cyber Law Assistant. How can I help you today with cyber law related questions?"
    
    if "thank" in query:
        return "You're welcome! If you have more questions about cyber law, feel free to ask."
    
    if "bye" in query or "goodbye" in query:
        return "Goodbye! Feel free to return if you have more cyber law questions."
    
    # Default response
    return "I'm specialized in cyber law topics. Could you please ask something related to cyber law, such as cybercrime, data protection, online privacy, digital signatures, or intellectual property rights?"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)