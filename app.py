from flask import Flask, render_template, jsonify, request
from multiprocessing import Process
from models import db, User, VisitorHistory
from werkzeug.security import generate_password_hash
from flask_socketio import SocketIO
import os

app = Flask(__name__)
socketio = SocketIO(app)

app.config["UPLOAD_FOLDER"] = 'static'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def init_db():
    try:
        db.create_all()
        print("Tables created successfully")
        admin_user = User.query.filter_by(username='admin').first()
        if admin_user is None:
            default_admin = User(
                username='admin',
                password_hash=generate_password_hash('admin')
            )
            db.session.add(default_admin)
            db.session.commit()
            print("Admin user created successfully")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        db.session.rollback()
        try:
            db.drop_all()
            db.create_all()
            default_admin = User(
                username='admin',
                password_hash=generate_password_hash('admin')
            )
            db.session.add(default_admin)
            db.session.commit()
            print("Database reinitialized successfully")
        except Exception as e:
            print(f"Failed to reinitialize database: {str(e)}")

@app.before_request
def track_visitor():
    if request.path == '/':
        try:
            ip_address = request.remote_addr
            visitor = VisitorHistory(ip_address=ip_address)
            db.session.add(visitor)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error tracking visitor: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/qr_code_updated', methods=['POST'])
def qr_code_updated():
    socketio.emit('new-qr-code', {'data': 'new-qr-code'})
    return jsonify({'status': 'success'}), 200

def run_scrapper():
    os.system("python3 scraper.py")

if __name__ == '__main__':
    scraper_process = Process(target=run_scrapper)
    scraper_process.start()
    with app.app_context():
        init_db()
    socketio.run(app, debug=True, use_reloader=False)
    scraper_process.join()
