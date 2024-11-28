from flask import Flask, request, jsonify, make_response, render_template
from datetime import datetime
from .models import Report, DeviceInformation
import pdfkit  # For generating PDFs

# Path to wkhtmltopdf binary (update this to match your system)
PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf='/path/to/wkhtmltopdf')

app = Flask(__name__)

@app.route('/generate-report', methods=['POST'])
def generate_report():
    try:
        # Get data from form submission
        report_type = request.form.get('report_type')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        bradycardia_report_type = request.form.get('bradycardia_report_type', None)  # Optional for bradycardia reports

        # Validate input
        if not report_type or not start_date or not end_date:
            return jsonify({"error": "All fields are required!"}), 400

        # Convert dates to datetime objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

        # Generate report header info
        header_info = {
            "institution_name": "Your Institution Name",
            "date_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "device_model_serial": "Model-12345",
            "dcm_serial": "DCM-67890",
            "application_version": "1.0.0",
            "report_name": report_type
        }

        # Generate the report content
        report_content = render_template('reporttemplate.html', header=header_info, report_type=report_type)

        # Generate the PDF
        pdf = pdfkit.from_string(report_content, False)  # Returns the PDF as a binary object

        # Send the PDF as a response
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename={report_type.replace(" ", "_")}.pdf'
        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500
