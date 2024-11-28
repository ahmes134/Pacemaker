from wsgiref.simple_server import software_version
from . import db
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, String, func
from . import db


class Note(db.Model):  # define a new type of object
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    # relationship between databases (one to many relationship)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class DeviceInformation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_model_num = db.Column(db.Integer)
    software_version = db.Column(db.String(10000))
    dcm_serial_num = db.Column(db.Integer)
    institution_name = db.Column(db.String(10000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Parameters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # lower rate limit - number of generator pace pulses delivered per min
    lrl = db.Column(db.Integer)
    # upper rate limit - max rate at which the paced ventricular rate will track sensed atrial events
    url = db.Column(db.Integer)
    max_sensor_rate = db.Column(db.Integer)
    fixed_av_delay = db.Column(db.Integer)
    dynamic_av_delay = db.Column(db.Integer)
    sensed_av_delay_offset = db.Column(db.Integer)
    atrial_amp = db.Column(db.Integer)
    ventricular_amp = db.Column(db.Integer)
    atrial_pulse_width = db.Column(db.Integer)
    ventricular_pulse_width = db.Column(db.Integer)
    atrial_sensitivity = db.Column(db.Integer)
    ventricular_sensitivity = db.Column(db.Integer)
    vrp = db.Column(db.Integer)  # ventricular refractory period
    arp = db.Column(db.Integer)  # atrial refractory period
    pvarp = db.Column(db.Integer)  # post ventricular atrial refractory period
    pvarp_ext = db.Column(db.Integer)
    hysteresis = db.Column(db.Integer)
    atr_duration = db.Column(db.Integer)
    atr_fallback_mode = db.Column(db.Integer)
    atr_fallback_time = db.Column(db.Integer)
    activity_threshold = db.Column(db.Integer)
    reaction_time = db.Column(db.Integer)
    # accelerometer determines the pacing rate that occurs at various levels of steady state patient activity (1 - 16)
    response_factor = db.Column(db.Integer)
    recovery_time = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class User(db.Model, UserMixin):  # inherit from Usermixin ONLY for the user object
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')
    device_information = db.relationship('DeviceInformation')
    parameters = db.relationship('Parameters')
   # language = db.Column(db.String(50))

# Model representing electrogram (Egram) data


class EgramData(db.Model):
    __tablename__ = 'egram_data'  # Name of the database table
    # Primary key for the table, an auto-incrementing integer
    id = Column(Integer, primary_key=True)
    # Timestamp of the data entry, defaults to current time
    timestamp = Column(DateTime, default=datetime.utcnow)
    # Signal value associated with the Egram
    signal_value = Column(Float, nullable=False)
    # event marker that indicates the type of event
    # Event markers: AS, AP, VS, VP
    event_marker = Column(String(50), nullable=True)

    # Constructor for initializing an EgramData object
    def __init__(self, signal_value, event_marker=None):
        self.signal_value = signal_value
        self.event_marker = event_marker


class Report(db.Model):  # Define a new type of object for reports
    __tablename__ = 'reports'  # Table name in the database

    # Unique identifier for each report
    id = db.Column(db.Integer, primary_key=True)
    # Foreign key to associate report with user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Type of report (e.g., Bradycardia Parameters)
    report_type = db.Column(db.String(50), nullable=False)
    # Start date for the report
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)  # End date for the report
    # Timestamp of report creation
    created_at = db.Column(db.DateTime, default=func.now())
    # to store report data in JSON format
    data = db.Column(db.JSON, nullable=True)

    # Define a relationship with User
    user = db.relationship('User', backref='reports')

    def __repr__(self):
        return f'<Report {self.id}, Type: {self.report_type}, User: {self.user_id}>'
