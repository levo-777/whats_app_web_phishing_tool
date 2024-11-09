from flask import Flask, render_template, jsonify, request, make_response
from flask_cors import CORS
from flask_socketio import SocketIO
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
app.config["UPLOAD_FOLDER"] = 'static'
CORS(app, resources={r"/*": {"origins": "*"}})

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
    response = make_response(render_template('index.html'))
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/qr_code_updated', methods=['POST'])
def qr_code_updated():
    socketio.emit('new-qr-code', {'data': 'new-qr-code'})
    response = jsonify({'status': 'success'})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/upload', methods=['POST'])
def upload_img():
    if 'file' in request.files:
        qr_code_img = request.files['file']
        filename = qr_code_img.filename  
        qr_code_img_path = os.path.join('./static', filename)
        if os.path.exists('./static/qr_code.png'):
            os.remove('./static/qr_code.png')
        qr_code_img.save(qr_code_img_path)
        response = make_response("OK")
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "*")
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        socketio.emit('new-qr-code', {'data': 'new-qr-code'})
        
        return response

if __name__ == '__main__':
    socketio.run(app, debug=True, use_reloader=False)