from flask import Flask, Blueprint, render_template, request, jsonify, send_file, make_response
from flask_login import login_required, current_user
from .serial_connection import SerialCommunication
from . import db
import time
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask import make_response


# Create the Flask app instance
app = Flask(__name__)

# Create the views blueprint
views = Blueprint('views', __name__)

@views.route("/generate-report", methods=["POST"])
def generate_report():
    # Get the user input from the form
    report_type = request.form.get("report_type", "Unknown Report")
    start_date = request.form.get("start_date", "N/A")
    end_date = request.form.get("end_date", "N/A")

    # Example header information
    institution_name = "McMaster Children's Hospital"
    device_model = "Pacemaker X100"
    serial_number = "789123"
    dcm_serial_number = "DCM98765"
    application_version = "v1.2.3"

    # Generate PDF using ReportLab
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Add report content
    c.setFont("Helvetica", 12)
    c.drawString(100, 750, f"Report Type: {report_type}")
    c.drawString(100, 730, f"Date Range: {start_date} to {end_date}")
    c.drawString(100, 710, f"Institution Name: {institution_name}")
    c.drawString(100, 690, f"Device Model: {device_model} ({serial_number})")
    c.drawString(100, 670, f"DCM Serial Number: {dcm_serial_number}")
    c.drawString(100, 650, f"Application Version: {application_version}")
    
    c.drawString(100, 630, f"Generated Content: Content for {report_type}:")
    c.save()

    # Return the PDF as a response
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="report.pdf", mimetype="application/pdf")


serial_conn = SerialCommunication(port="/dev/cu.usbmodem21103")
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


# Route for bradycardia therapy page (if not already present)
@views.route("/bradycardia-therapy", methods=["GET", "POST"])
@login_required
def bradycardia_therapy():
    """
    Handles form submission for bradycardia therapy parameters and sends the data to the pacemaker device.
    """
    
    if request.method == "POST":
        try:
            # Retrieve form data from bradycardia.html
            therapy_type = request.form.get("therapy_type", "")
            lrl = request.form.get("lrl", 30)  # Default if not provided
            url = request.form.get("url", 50)
            max_sensor_rate = request.form.get("max_sensor_rate", 50)
            fixed_av_delay = request.form.get("fixed_av_delay", 70)
            atrial_amp = request.form.get("atrial_pulse_amp_value", 0)
            ventricular_amp = request.form.get("ventricular_amp_value", 0)
            atrial_pulse_width = request.form.get("atrial_pulse_width", 1)
            ventricular_pulse_width = request.form.get("ventricular_pulse_width", 1)
            atrial_sensitivity = request.form.get("atrial_sensitivity", 0)
            ventricular_sensitivity = request.form.get("ventricular_sensitivity", 0)
            vrp = request.form.get("vrp", 150)
            arp = request.form.get("arp", 150)
            pvarp = request.form.get("pvarp", 150)
            activity_threshold = request.form.get("activity_threshold", 0)
            reaction_time = request.form.get("reaction_time", 10)
            response_factor = request.form.get("response_factor", 1)
            recovery_time = request.form.get("recovery_time", 2)

            # Log the parameters for debugging
            print("Received parameters from form:")
            print(f"Therapy Type: {therapy_type}, LRL: {lrl}, URL: {url}")
            print(f"Max Sensor Rate: {max_sensor_rate}, Fixed AV Delay: {fixed_av_delay}")
            print(f"Atrial Amp: {atrial_amp}, Ventricular Amp: {ventricular_amp}")
            print(f"Atrial Pulse Width: {atrial_pulse_width}, Ventricular Pulse Width: {ventricular_pulse_width}")
            print(f"Atrial Sensitivity: {atrial_sensitivity}, Ventricular Sensitivity: {ventricular_sensitivity}")
            print(f"VRP: {vrp}, ARP: {arp}, PVARP: {pvarp}")
            print(f"Reaction Time: {reaction_time}, Response Factor: {response_factor}")
            print(f"Recovery Time: {recovery_time}")
            
            print(f"Received therapy type: {therapy_type}")
            

            if therapy_type not in serial_conn.mode_map:
                print(f"Invalid therapy type: {therapy_type}")
                return jsonify({"error": "Invalid therapy type provided"}), 400
            
            if not therapy_type:
              return jsonify({"error": "Therapy Type is required"}), 400
            
            # Call the sendSerial method to send data via serial connection
            serial_conn.sendSerial(
                mode= therapy_type,
                LRL=lrl,
                URL=url,
                Max_Sensor_Rate=max_sensor_rate,
                AV_Delay=fixed_av_delay,
                A_Amplitude=atrial_amp,
                V_Amplitude=ventricular_amp,
                A_Pulse_Width=atrial_pulse_width,
                V_Pulse_Width=ventricular_pulse_width,
                A_Sensitivity=atrial_sensitivity,
                V_Sensitivity=ventricular_sensitivity,
                VRP=vrp,
                ARP=arp,
                PVARP=pvarp,
                Activity_Threshold=activity_threshold,
                Reaction_Time=reaction_time,
                Response_Factor=response_factor,
                Recovery_Time=recovery_time,
                port="/dev/cu.usbmodem21103"  # Update with your COM port
            )

            return jsonify({"message": "Parameters sent successfully!"}), 200

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"message": "Failed to send data.", "error": str(e)}), 500

    # Render the Bradycardia Therapy page
    return render_template("bradycardia_therapy.html", user=current_user)


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
