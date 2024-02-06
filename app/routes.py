from flask import Blueprint, request, jsonify, current_app
from .utils import (extract_text_from_pdf_with_images, extract_name, extract_email, 
                    extract_website, extract_and_format_phone_numbers, extract_skills,
                    write_to_csv, get_access_token)

main = Blueprint('main', __name__)


@main.route('/upload', methods=['POST'])
def upload_and_process():
    current_app.logger.info("Upload endpoint hit")

    if 'file' not in request.files:
        current_app.logger.error("No file part")
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    current_app.logger.info(f"Processing file: {file.filename}")
    content = file.read()  # Read the content of the file uploaded

    # Process the uploaded file content
    text = extract_text_from_pdf_with_images(content)
    if text:
        name = extract_name(text)
        email = extract_email(text)
        website = extract_website(text)
        phone_numbers = extract_and_format_phone_numbers([text])
        
        access_token = get_access_token()
        skills = extract_skills(text, access_token) if access_token else "Skills extraction failed due to missing access token."

        # Compile extracted data into a list of dictionaries (one entry for simplicity)
        extracted_data = [{
            'Full Name': name,
            'Email Address': email,
            'Website': website,
            'Phone Number': ', '.join(phone_numbers),  
            'Skills': skills
        }]

        # Define the CSV file path
        csv_file_path = 'output.csv'
        write_to_csv(extracted_data, csv_file_path)

        # Return a success message with file path
        return jsonify({"message": "Data extraction complete. Output saved to CSV.", "File Path": csv_file_path}), 200
    else:
        return jsonify({"error": "Failed to extract text from file."}), 500
