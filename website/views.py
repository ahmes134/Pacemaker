from flask import Flask, Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from .serial_connection import SerialCommunication
from . import db
import time

# Create the Flask app instance
app = Flask(__name__)

# Create the views blueprint
views = Blueprint('views', __name__)

# Initialize serial communication
serial_conn = SerialCommunication(port="COM6", baudrate=115200)
serial_conn.connect()

# Status mapping for styling
STATUS_CLASS_MAPPING = {
    "Connected": "connected",
    "Out of Range": "out-of-range",
    "Noise": "noise",
    "Another Device Detected": "another-device"
}

# Helper function to check pacemaker connection
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
    """
    Home page route. Displays pacemaker connection status.
    """
    connection_status = serial_conn.is_connected()
    return render_template(
        "home.html",
        user=current_user,
        pacemaker_status="Connected" if connection_status else "Out of Range",
        pacemaker_status_class="connected" if connection_status else "out-of-range"
    )


@views.route("/submit", methods=["POST"])
def submit():
    """
    Route to handle parameter submission and send it to the pacemaker.
    """
    try:
        # Parse the data from the POST request
        data = request.get_json()

        # Extract parameters
        mode = data['mode']
        LRL = int(data['LRL'])
        URL = int(data['URL'])
        Max_Sensor_Rate = int(data.get('Max_Sensor_Rate', 0))
        AV_Delay = int(data.get('AV_Delay', 150))
        A_Amplitude = float(data.get('A_Amplitude', 0.0))
        V_Amplitude = float(data.get('V_Amplitude', 0.0))
        A_Pulse_Width = int(data.get('A_Pulse_Width', 0))
        V_Pulse_Width = int(data.get('V_Pulse_Width', 0))
        A_Sensitivity = float(data.get('A_Sensitivity', 0.0))
        V_Sensitivity = float(data.get('V_Sensitivity', 0.0))
        VRP = int(data.get('VRP', 0))
        ARP = int(data.get('ARP', 0))
        PVARP = int(data.get('PVARP', 0))
        Rate_Smoothing = int(data.get('Rate_Smoothing', 0))
        Activity_Threshold = float(data.get('Activity_Threshold', 0.0))
        Reaction_Time = int(data.get('Reaction_Time', 0))
        Response_Factor = int(data.get('Response_Factor', 0))
        Recovery_Time = int(data.get('Recovery_Time', 0))
        Function_Call = int(data.get('Function_Call', 0))
        port = data.get('port', "COM6")

        # Print the received parameters for debugging
        print("Received Parameters:")
        print(f"Mode: {mode}")
        print(f"Lower Rate Limit (LRL): {LRL}")
        print(f"Upper Rate Limit (URL): {URL}")
        print(f"Max Sensor Rate: {Max_Sensor_Rate}")
        print(f"AV Delay: {AV_Delay}")
        print(f"Atrial Amplitude: {A_Amplitude}")
        print(f"Ventricular Amplitude: {V_Amplitude}")
        print(f"Atrial Pulse Width: {A_Pulse_Width}")
        print(f"Ventricular Pulse Width: {V_Pulse_Width}")
        print(f"Atrial Sensitivity: {A_Sensitivity}")
        print(f"Ventricular Sensitivity: {V_Sensitivity}")
        print(f"VRP: {VRP}")
        print(f"ARP: {ARP}")
        print(f"PVARP: {PVARP}")
        print(f"Rate Smoothing: {Rate_Smoothing}")
        print(f"Activity Threshold: {Activity_Threshold}")
        print(f"Reaction Time: {Reaction_Time}")
        print(f"Response Factor: {Response_Factor}")
        print(f"Recovery Time: {Recovery_Time}")
        print(f"Function Call: {Function_Call}")
        print(f"Port: {port}")

        # Send the parameters to the pacemaker
        serial_conn.sendSerial(
            mode, LRL, URL, Max_Sensor_Rate, AV_Delay, A_Amplitude, V_Amplitude,
            A_Pulse_Width, V_Pulse_Width, A_Sensitivity, V_Sensitivity, VRP,
            ARP, PVARP, Rate_Smoothing, Activity_Threshold, Reaction_Time,
            Response_Factor, Recovery_Time, Function_Call, port
        )

        return jsonify({"message": "Data successfully sent to pacemaker!"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"message": "Failed to send data.", "error": str(e)}), 500


@views.route('/get-data', methods=['GET'])
def get_received_data():
    """
    Route to fetch data from the pacemaker for debugging or verification.
    """
    data = serial_conn.receive_data()
    if data:
        return jsonify({"received_data": data})
    else:
        return jsonify({"message": "No data available"})


# Register the views blueprint with the Flask app
app.register_blueprint(views)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)
