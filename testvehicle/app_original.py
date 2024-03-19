import numpy
import cv2
import pytesseract
from PIL import Image
from flask import Flask, render_template, Response
import threading

app = Flask(__name__)

# Mock database for vehicle information
vehicle_database = {
    "HR26DK8337": {"owner_name": "Sankalp Patra", "make": "Toyota", "model": "Camry", "color": "Blue"},
    "DL2C P 5428": {"owner_name": "John Doe", "make": "OLA", "model": "S1 PRO", "color": "Red"}
}

# List to store recognized license plate information
recognized_plates = []

# Load the pre-trained license plate detection cascade
plate_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_russian_plate_number.xml')

# Path to Tesseract OCR executable (update this based on your installation)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

# Function to perform OCR on an image region
def perform_ocr(img):
    custom_config = r'--oem 3 --psm 6'  # OCR engine mode and page segmentation mode
    plate_number = pytesseract.image_to_string(img, config=custom_config)
    return plate_number.strip()

# Function to process the video stream
def process_video():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect license plates in the frame
        plates = plate_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in plates:
            # Crop the region of interest (ROI) containing the license plate
            plate_roi = frame[y:y + h, x:x + w]

            # Perform OCR on the license plate region
            pil_image = Image.fromarray(cv2.cvtColor(plate_roi, cv2.COLOR_BGR2RGB))
            plate_number = perform_ocr(pil_image)

            # Match the plate number with the database
            if plate_number in vehicle_database:
                vehicle_info = vehicle_database[plate_number]

                # Check if the plate is already recognized
                if plate_number not in [plate['plate_number'] for plate in recognized_plates]:
                    # Store the recognized plate information in the list
                    recognized_plates.append({
                        "plate_number": plate_number,
                        "owner_name": vehicle_info['owner_name'],
                        "make": vehicle_info['make'],
                        "model": vehicle_info['model'],
                        "color": vehicle_info['color']
                    })

                # Display the vehicle information on the frame including owner name
                info_text = f"Owner: {vehicle_info['owner_name']}, Make: {vehicle_info['make']}, Model: {vehicle_info['model']}, Color: {vehicle_info['color']}"
                cv2.putText(frame, info_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Display the original frame with the license plate highlighted
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Display the processed frame
        ret, jpeg = cv2.imencode('.jpg', frame)
        frame_bytes = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

    cap.release()

# Function to run the video processing in a separate thread
def run_video_processing():
    with app.app_context():
        app.video_thread = threading.Thread(target=process_video)
        app.video_thread.start()

# Route for the home page (scanning image)
@app.route('/')
def index():
    return render_template('index.html')

# Route for the video feed (scanning image)
@app.route('/video_feed')
def video_feed():
    return Response(process_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Route for displaying recognized plates (showing information)
@app.route('/recognized_plates')
def recognized_plates_page():
    return render_template('recognized_plates.html', recognized_plates=recognized_plates)

if __name__ == '__main__':
    run_video_processing()
    app.run(debug=True)

