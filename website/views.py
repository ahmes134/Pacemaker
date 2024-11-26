from flask import Flask, Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from .models import Note, User, DeviceInformation, EgramData, PacemakerStatus
from .serial import SerialCommunication
from . import db
import json

# Create the Flask app instance
app = Flask(__name__)

views = Blueprint('views', __name__)

# Initialize serial communication
serial_conn = SerialCommunication(port="COM11", baudrate=9600)
serial_conn.connect()

@views.route('/', methods=['GET'])
@login_required
def home():
    # Check the pacemaker connection status
    pacemaker_status, pacemaker_status_class = check_pacemaker_connection()

    # Fetch the latest status from the database
    latest_status = PacemakerStatus.query.order_by(PacemakerStatus.id.desc()).first()
    db_status = latest_status.status if latest_status else "Out of Range"

    # Use database status if available, otherwise fallback to live status
    current_status = db_status or pacemaker_status
    status_class = {
        "Connected": "connected",
        "Out of Range": "out-of-range",
        "Noise": "noise",
        "Another Device Detected": "another-device"
    }.get(current_status, "out-of-range")  # Default to 'out-of-range' if unknown

    return render_template(
        "home.html",
        user=current_user,
        pacemaker_status=current_status,
        pacemaker_status_class=status_class
    )
def check_pacemaker_connection():
    """
    Check if the pacemaker device is connected.
    :return: Tuple (status, css_class)
    """
    if serial_conn.is_connected():
        return "Connected", "connected"
    else:
        return "Not Connected", "out-of-range"


def check_pacemaker_connection():
    if serial_conn.serial_conn and serial_conn.serial_conn.is_open:
        return "Connected", "connected"
    else:
        try:
            serial_conn.connect()  # Attempt reconnection
            if serial_conn.serial_conn.is_open:
                return "Connected", "connected"
        except Exception as e:
            print(f"Error reconnecting: {e}")
        return "Not Connected", "out-of-range"

@views.route('/check-connection-status', methods=['GET'])
def check_connection_status():
    pacemaker_status, pacemaker_status_class = check_pacemaker_connection()
    return {
        "pacemaker_status": pacemaker_status,
        "pacemaker_status_class": pacemaker_status_class
    }

@views.route("/submit", methods=["POST"])
def handle_submit():
    data = request.json  # Receive JSON data from the frontend
    therapy_type = data.get("therapyType")
    parameters = data.get("parameters")

    # Format the data to send to the pacemaker
    formatted_data = f"TherapyType:{therapy_type};" + ";".join(
        f"{key}:{value}" for key, value in parameters.items()
    )

    # Transmit data to the pacemaker
    serial_conn.send_data(formatted_data)

    return jsonify({"message": "Data sent to pacemaker", "status": "success"})

@views.route('/user/<int:user_id>')
def get_user_data(user_id):
    # Function implementation here
    # Fetch the user by their ID
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return "User not found", 404

    # Fetch the associated device information (if any)
    device = DeviceInformation.query.filter_by(user_id=user.id).first()

    # Pass both user and device data to the template
    return render_template('about.html', user=user, device=device)

    # Register your views Blueprint with the Flask app
    app.register_blueprint(views)

@app.route('/set_clock', methods=['GET'])
def set_clock():
    # Get the current date and time
    current_date = datetime.now().strftime('%Y-%m-%d')
    current_time = datetime.now().strftime('%H:%M:%S')

    # Render the HTML template with the current date and time
    return render_template('set_clock.html', current_date=current_date, current_time=current_time)

@views.route('/view_egram', methods=['GET'])
@login_required 
def view_egram():
    # Sample temporary data for demonstration
    egram_data = [
        {'timestamp': '2024-10-25 10:00:00', 'signal_value': 1.5, 'event_marker': 'AS'},
        {'timestamp': '2024-10-25 10:01:00', 'signal_value': 2.3, 'event_marker': 'AP'},
        {'timestamp': '2024-10-25 10:02:00', 'signal_value': 1.8, 'event_marker': 'VS'},
        {'timestamp': '2024-10-25 10:03:00', 'signal_value': 2.0, 'event_marker': 'VP'}
    ]
    return render_template('view_egram_data.html', egram_data=egram_data, user=current_user)

@views.route('/update_status/<new_status>')
@login_required
def update_status(new_status):
    if current_user.role != 'admin':  # Example admin role check
        return "Unauthorized", 403
    if new_status not in ["Connected", "Out of Range", "Noise", "Another Device Detected"]:
        return "Invalid status", 400

    new_entry = PacemakerStatus(status=new_status)
    db.session.add(new_entry)
    db.session.commit()
    return f"Status updated to {new_status}", 200

if __name__ == '__main__':
    app.run(debug=True)
