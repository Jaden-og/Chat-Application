import gevent.monkey
gevent.monkey.patch_all()

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='gevent')

# Example user data (username: hashed password)
users = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/validate', methods=['POST'])
def validate():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username in users and check_password_hash(users[username], password):
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username in users:
        return jsonify({'status': 'error', 'message': 'Username already exists'}), 400

    users[username] = generate_password_hash(password)
    return jsonify({'status': 'success'})

@socketio.on('message')
def handle_message(data):
    username = data.get('username')
    message = data.get('message')
    if username:
        formatted_message = f'{username}: {message}'
        emit('message', formatted_message, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
