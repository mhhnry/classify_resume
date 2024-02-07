from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from .utils import ( write_to_csv, extract_text_based_on_file_type, process_extracted_text)


ALLOWED_EXTENSIONS = {'pdf', 'docx', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

main = Blueprint('main', __name__)

@main.route('/upload', methods=['POST'])
def upload_and_process():
    current_app.logger.info("Upload endpoint hit")

    if not request.files:
        current_app.logger.error("No file part")
        return jsonify({"error": "No file part"}), 400

    extracted_data = []

    files = request.files.getlist('files[]')

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            current_app.logger.info(f"Processing file: {filename}")
            
            # Extract text based on file type
            text = extract_text_based_on_file_type(file, filename)
            
            # Process extracted text (common for all file types)
            if text:
                name, email, website, phone_numbers, skills = process_extracted_text(text)
                extracted_data.append({
                    'Full Name': name,
                    'Email Address': email,
                    'Website': website,
                    'Phone Number': ', '.join(phone_numbers),
                    'Skills': skills
                })

    # Write to CSV and return response
    if extracted_data:
        csv_file_path = write_to_csv(extracted_data, 'output.csv')
        return jsonify({"message": "Data extraction complete. Output saved to CSV.", "File Path": csv_file_path}), 200
    else:
        return jsonify({"error": "Failed to extract text from files."}), 500
