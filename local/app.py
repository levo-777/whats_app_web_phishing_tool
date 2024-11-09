from flask import Flask, render_template, jsonify, request, make_response
from flask_cors import CORS
from flask_socketio import SocketIO
from multiprocessing import Process
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
app.config["UPLOAD_FOLDER"] = 'static'
CORS(app, resources={r"/*": {"origins": "*"}})
def run_scrapper():
    os.system("python3 scraper.py")

@app.before_request
def track_visitor():
    if request.path == '/':
        try:
            ip_address = request.remote_addr
            print(f"Visitor IP Address: {ip_address}")
        except Exception as e:
            print(f"Error tracking visitor: {str(e)}")

@app.route('/')
def index():
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    response = make_response(render_template('index.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/qr_code_updated', methods=['POST'])
def qr_code_updated():
    socketio.emit('new-qr-code', {'data': 'new-qr-code'})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    response = jsonify({'status': 'success'})
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route("/user_logged_in", methods=['POST'])
def user_logged_in():
    scraper_process = Process(target=run_scrapper)
    scraper_process.start()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    response = jsonify({'status': 'success'})
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    scraper_process = Process(target=run_scrapper)
    scraper_process.start()
    socketio.run(app, debug=True, use_reloader=False)