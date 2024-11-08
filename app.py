from flask import Flask, render_template, request, jsonify
import os
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
from werkzeug.utils import secure_filename
import base64
from PIL import Image
import io

app = Flask(__name__)

# Configure the upload folder before using it
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Define allowed extensions for uploaded images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Load the trained model
model = tf.keras.models.load_model('models/skin_tone_model.h5')

# Skin tone categories
skin_tone_categories = ['dark', 'light', 'lighten', 'mid dark', 'mid light', 'mid-dark', 'mid-light']

# Makeup product recommendations based on skin tone with Filipino brands
makeup_recommendations = {
    'dark': {
        'Foundation': ['Vice Cosmetics Foundation in Dark', 'Ever Bilena Advanced Foundation in Deep'],
        'Concealer': ['BLK Cosmetics Concealer in Deep Tan', 'Ever Bilena Concealer in Dark'],
        'Skin Tint': ['Happy Skin Flawless Skin Tint in Deep Bronze', 'Color Collection Skin Tint in Mocha'],
    },
    'light': {
        'Foundation': ['Vice Cosmetics Foundation in Light', 'BLK Cosmetics Foundation in Fair'],
        'Concealer': ['Ever Bilena Concealer in Light Beige', 'Happy Skin Concealer in Soft Beige'],
        'Skin Tint': ['Maybelline Fit Me Skin Tint in Light', 'BLK Cosmetics Skin Tint in Natural Beige'],
    },
    'lighten': {
        'Foundation': ['Maybelline Fit Me Foundation in Natural Ivory', 'Ever Bilena Foundation in Light Beige'],
        'Concealer': ['Happy Skin Concealer in Ivory Glow', 'BLK Cosmetics Concealer in Soft Almond'],
        'Skin Tint': ['Color Collection Skin Tint in Sand', 'Vice Cosmetics Skin Tint in Porcelain'],
    },
    'mid dark': {
        'Foundation': ['Maybelline Fit Me Foundation in Medium Brown', 'Vice Cosmetics Foundation in Medium'],
        'Concealer': ['BLK Cosmetics Concealer in Medium Tan', 'Ever Bilena Concealer in Medium'],
        'Skin Tint': ['Happy Skin Flawless Skin Tint in Tan', 'Color Collection Skin Tint in Amber'],
    },
    'mid light': {
        'Foundation': ['BLK Cosmetics Foundation in Medium', 'Maybelline Fit Me Foundation in Buff Beige'],
        'Concealer': ['Happy Skin Concealer in Buff', 'Ever Bilena Concealer in Medium Beige'],
        'Skin Tint': ['Vice Cosmetics Skin Tint in Peach Beige', 'BLK Cosmetics Skin Tint in Medium Tan'],
    },
    'mid-dark': {
        'Foundation': ['Happy Skin Flawless Skin Tint in Medium', 'Vice Cosmetics Foundation in Tawny'],
        'Concealer': ['Ever Bilena Concealer in Tawny', 'Color Collection Concealer in Golden Beige'],
        'Skin Tint': ['Maybelline Fit Me Skin Tint in Medium', 'BLK Cosmetics Skin Tint in Chestnut'],
    },
    'mid-light': {
        'Foundation': ['Maybelline Fit Me Foundation in Natural Beige', 'Vice Cosmetics Foundation in Beige'],
        'Concealer': ['BLK Cosmetics Concealer in Light Tan', 'Ever Bilena Concealer in Fair'],
        'Skin Tint': ['Color Collection Skin Tint in Light Beige', 'Happy Skin Skin Tint in Honey Beige'],
    },
}

# Helper function to check if file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to preprocess the image before predicting
def resize_image(image_path, target_size=(224, 224)):
    with Image.open(image_path) as img:
        img = img.resize(target_size)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        return base64.b64encode(img_byte_arr).decode('utf-8')
    
def preprocess_image(image_path):
    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)  # Convert to array
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    img_array = img_array / 255.0  # Normalize image
    return img_array

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        print("Error: No file part in the request")
        return jsonify({'error': 'No file part'}), 500
    
    file = request.files['file']
    if file.filename == '':
        print("Error: No file selected")
        return jsonify({'error': 'No selected file'}), 500
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(f"Saving file at: {file_path}")
        file.save(file_path)

        # Preprocess the image and predict the skin tone
        img_b64 = resize_image(file_path)  # Process the uploaded image
        img_array = preprocess_image(file_path)  # Replace with your preprocessing function
        if img_array is None:
            print("Error during image preprocessing")
            return jsonify({'error': 'Image processing failed'}), 500
        
        predictions = model.predict(img_array)
        predicted_class = skin_tone_categories[np.argmax(predictions)]
        print(f"Predicted skin tone: {predicted_class}")

        # Fetch makeup recommendations based on the skin tone
        recommendations = makeup_recommendations.get(predicted_class, {})

        response = {
            'skin_tone': predicted_class,
            'makeup_recommendation': recommendations,
            'image_url': f'/static/uploads/{filename}'  # Return the image URL
        }
        print("Returning response:", response)
        return jsonify(response)

    print("Error: Invalid file type")
    return jsonify({'error': 'Invalid file type'}), 500

if __name__ == '__main__':
    app.run(debug=True)
