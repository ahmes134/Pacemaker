from flask import Flask, Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from .models import Note, User, DeviceInformation, EgramData
from serial_connection import SerialCommunication, get_connection_status

# Remove the old check_pacemaker_connection function

from . import db

# Create the Flask app instance
app = Flask(__name__)

# Create the views blueprint
views = Blueprint('views', __name__)

# Initialize serial communication
serial_conn = SerialCommunication(port="COM11", baudrate=115200)
serial_conn.connect()

# Status mapping for styling
STATUS_CLASS_MAPPING = {
    "Connected": "connected",
    "Out of Range": "out-of-range",
    "Noise": "noise",
    "Another Device Detected": "another-device"
}


def check_pacemaker_connection():
    """
    Helper function to check pacemaker connection status.
    Returns:
        tuple: (status message, status class for styling)
    """
    if serial_conn.is_connected():
        return "Connected", "connected"
    else:
        return "Out of Range", "out-of-range"


@views.route('/', methods=['GET'])
@login_required
def home():
    connection_status = get_connection_status()
    return render_template(
        "home.html",
        user=current_user,
        pacemaker_status=connection_status["pacemaker_status"],
        pacemaker_status_class=connection_status["pacemaker_status_class"]
    )


@views.route('/check-connection-status', methods=['GET'])
def check_connection_status():
    connection_status = get_connection_status()
    return jsonify(connection_status)


@views.route("/submit", methods=["POST"])
def handle_submit():
    """
    API route to handle data submission to the pacemaker.
    """
    data = request.json  # Receive JSON data from the frontend
    therapy_type = data.get("therapyType")
    parameters = data.get("parameters", {})

    # Format the data to send to the pacemaker
    formatted_data = f"TherapyType:{therapy_type};" + ";".join(
        f"{key}:{value}" for key, value in parameters.items()
    )

    # Transmit data to the pacemaker
    # serial_conn.send_data(formatted_data)
    # return jsonify({"message": "Data sent to pacemaker", "status": "success"})


@views.route('/get-data', methods=['GET'])
def get_received_data():
    """
    API route to fetch received data from the pacemaker.
    """
    data = serial_conn.get_data()
    if data:
        return jsonify({"received_data": data})
    else:
        return jsonify({"message": "No data available"})


# Register the views Blueprint with the Flask app
app.register_blueprint(views)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database tables
    app.run(debug=True)
