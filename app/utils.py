import os
import re
import csv
import requests
import json
from io import BytesIO
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
import nltk
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.tree import Tree
from nameparser.parser import HumanName
from flask import current_app
import logging


logger = logging.getLogger(__name__)


# Ensure NLTK resources are pre-downloaded
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('maxent_ne_chunker', quiet=True)
nltk.download('words', quiet=True)
nltk.download('punkt', quiet=True)

# Set Tesseract command path
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'  # Adjust as per your environment

def extract_text_from_pdf_with_images(content):
    text = ""
    try:
        # If content is bytes, no need to read again
        if isinstance(content, bytes):
            pdf_stream = BytesIO(content)
        else:
            pdf_stream = BytesIO(content.read())
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        for page in doc:
            text += page.get_text()
            for img_index, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image['image']
                image = Image.open(BytesIO(image_bytes))
                image_text = pytesseract.image_to_string(image)
                text += "\n" + image_text
    except Exception as e:
        current_app.logger.error(f"Error processing PDF with images: {e}")
    finally:
        if 'doc' in locals():
            doc.close()
    return text

def extract_name(text):
    names = []
    try:
        tokens = word_tokenize(text)
        tags = pos_tag(tokens)
        chunks = ne_chunk(tags)
        for chunk in chunks:
            if isinstance(chunk, Tree) and chunk.label() == 'PERSON':
                names.append(' '.join([c[0] for c in chunk]))
        name = HumanName(names[0]).full_name if names else ""
    except Exception as e:
        current_app.logger.error(f"Error extracting name: {e}")
        name = ""
    return name

def extract_email(text):
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(pattern, text)
    return matches[0] if matches else ""

def extract_website(text):
    pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    matches = re.findall(pattern, text)
    return matches[0] if matches else ""


def extract_and_format_phone_numbers(texts, default_country_code="+1"):
    formatted_numbers = []
    for text in texts:
        # Enhanced regex pattern for accurate and flexible matching:
        phone_pattern = r'(\+?\d{1,4})?[\s.-]*\(?\s*(\d{3})\s*\)?[\s.-]*(\d{1,4})[\s.-]*(\d{1,4})[\s.-]*(\d{0,4})'
        matches = re.findall(phone_pattern, text)
        for match in matches:
            country_code, area_code, first_part, second_part, last_part = match

            # Log step 1: Extracted phone number parts from the regex match
            logger.info(f"Step 1: Extracted parts - Country Code: {country_code}, Area Code: {area_code}, First Part: {first_part}, Second Part: {second_part}, Last Part: {last_part}")

            # Ensure a valid country code:
            country_code = country_code if country_code else default_country_code
            country_code = '+' + country_code if not country_code.startswith('+') else country_code

            # Log step 2: Country code adjustment
            logger.info(f"Step 2: Country Code Adjustment - Country Code: {country_code}")

            # Concatenate parts to count total digits excluding country code:
            concatenated_parts = area_code + first_part + second_part + last_part

            # Log step 3: Concatenated parts
            logger.info(f"Step 3: Concatenated Parts - {concatenated_parts}")

            # Only proceed if the total digits are at least 10:
            if len(concatenated_parts) >= 10:
                # Trim to first 10 digits if more than 10 digits are present:
                concatenated_parts = concatenated_parts[:10]

                # Reassign trimmed parts to their respective variables:
                area_code = concatenated_parts[:3]
                first_part = concatenated_parts[3:6]
                second_part = concatenated_parts[6:10]

                # Log step 4: Trimming and reassigning parts
                logger.info(f"Step 4: Trimmed and Reassigned Parts - Area Code: {area_code}, First Part: {first_part}, Second Part: {second_part}")

                # Format the number:
                formatted_number = f"{country_code} ({area_code}) {first_part}-{second_part}"

                # Remove redundant zeroes from country code adjustments:
                formatted_number = formatted_number.replace('(0)', '()').replace(' 0', ' ').strip()

                # Log step 5: Formatted number
                logger.info(f"Step 5: Formatted Number - {formatted_number}")

                formatted_numbers.append(formatted_number)

    return formatted_numbers

def get_access_token():
    url = "https://auth.emsicloud.com/connect/token"
    payload = "client_id=p68g24qn9dnh4hks&client_secret=Z9ZH1e0r&grant_type=client_credentials&scope=emsi_open"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(url, data=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        current_app.logger.error("Failed to obtain access token")
        return None

def extract_skills(text, access_token):
    url = "https://emsiservices.com/skills/versions/latest/extract"
    headers = {'Authorization': f"Bearer {access_token}", 'Content-Type': "application/json"}
    payload = {"text": text, "confidenceThreshold": 0.6}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        skills_data = response.json().get('data', [])
        skills = [skill['skill']['name'] for skill in skills_data]
        return ", ".join(skills)
    else:
        current_app.logger.error("Failed to extract skills")
        return ""

def write_to_csv(data, csv_file_path):
    fieldnames = ['Full Name', 'Email Address', 'Website', 'Phone Number', 'Skills']  # Added 'Website'
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

