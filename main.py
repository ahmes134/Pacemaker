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
    with app.app_context():
        db.create_all()  # Create the tables
    app.run(debug=True)

