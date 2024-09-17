from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit, join_room
import random

app = Flask(__name__)
socketio = SocketIO(app)

# Store chat rooms and their corresponding codes
chat_rooms = {}

# Route to create a new chat room and generate a code
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/create-room', methods=['POST'])
def create_room():
    # Generate a random 4-digit code
    room_code = '{:04d}'.format(random.randint(0, 9999))
    chat_rooms[room_code] = []  # Initialize the chat room with an empty list of messages
    return redirect(url_for('chat_room', room_code=room_code))

# Route to join an existing chat room by entering a code
@app.route('/join-room', methods=['POST'])
def join_room_route():
    room_code = request.form['room_code']
    if room_code in chat_rooms:
        return redirect(url_for('chat_room', room_code=room_code))
    return render_template('home.html', error="Invalid room code.")

# Serve the chat room page for a valid room code
@app.route('/chat/<room_code>')
def chat_room(room_code):
    if room_code not in chat_rooms:
        return redirect(url_for('home'))  # If the room code is invalid, redirect to home
    return render_template('chat.html', room_code=room_code)

# Handle messages in a specific chat room
@socketio.on('message')
def handle_message(data):
    room = data['room']
    msg = data['msg']
    chat_rooms[room].append(msg)  # Store the message in the room
    emit('message', msg, room=room)  # Send message to all clients in the room

# Join the specific chat room with the given room code
@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    emit('message', f"A new user has joined room {room}.", room=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)