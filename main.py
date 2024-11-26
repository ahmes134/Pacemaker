#!/usr/bin/env python3.8
from website import create_app
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from website.views import views
from website.models import db
from flask_socketio import SocketIO, emit
from website.serial import SerialCommunication 


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)  # debug mode for development

app = Flask(__name__)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pacemaker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Register the views blueprint
app.register_blueprint(views, url_prefix='/')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the tables
    app.run(debug=True)

# Initialize WebSocket (SocketIO)
socketio = SocketIO(app)

# Serial Communication Setup
serial_conn = SerialCommunication(port="COM11", baudrate=11520)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('check_status')
def check_status():
    """
    Check the pacemaker connection status and emit the result.
    """
    if serial_conn.is_connected():
        pacemaker_status = "Connected"
        pacemaker_status_class = "connected"
    else:
        pacemaker_status = "Not Connected"
        pacemaker_status_class = "out-of-range"
    
    emit('status_update', {
        'pacemaker_status': pacemaker_status,
        'pacemaker_status_class': pacemaker_status_class
    })

# Run Flask with SocketIO
if __name__ == "__main__":
    socketio.run(app, debug=True, host="127.0.0.1", port=5000)
