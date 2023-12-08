import tkinter as tk
import cv2
from PIL import Image, ImageTk
from ultralytics import YOLO
import torch
import time
from telegram import Bot, ParseMode

# Load the YOLOv8 model
model = YOLO('Fire.pt')

# Telegram bot token
TELEGRAM_BOT_TOKEN = '6634478065:AAFUNFufu7hj8WoAWa6TAYj6XxW0NRO5swg'
TELEGRAM_CHAT_ID = 1886522458

# Open the video file
video_path = "Fire.mp4"
start_time = time.time()

class CameraApp:
    def __init__(self, root, camera_index=0):
        self.root = root
        self.root.title("Tkinter Camera GUI")

        # Open the camera
        self.cap = cv2.VideoCapture(video_path)

        # Create a canvas to display the camera feed
        self.canvas = tk.Canvas(root)
        self.canvas.pack()

        # Create buttons for capturing a photo and recording a video
        self.capture_button = tk.Button(root, text="Capture Photo", command=self.capture_photo)
        self.capture_button.place(x=310, y=510, width=100, height=50)

        self.record_button = tk.Button(root, text="Record Video", command=self.toggle_record)
        self.record_button.place(x=210, y=510, width=100, height=50)

        # Create a button to exit the application
        self.exit_button = tk.Button(root, text="Exit", command=self.exit_app)
        self.exit_button.place(x=410, y=510, width=100, height=50)

        # Video recording variables
        self.is_recording = False
        self.video_writer = None

        # Update the camera feed
        self.update()

    def fire_detected(self, results_list, confidence_threshold=0.5):
        """
        Check if the 'fire' class is detected with confidence greater than the threshold.

        Parameters:
        - results_list: List of Results objects containing detection information.
        - confidence_threshold: Confidence threshold for detection.

        Returns:
        - True if fire is detected in any result, False otherwise.
        """
        for results in results_list:
            boxes = results.boxes  # Assuming boxes are stored in a Boxes object
            conf = boxes.conf
            cls = boxes.cls

            # Assuming 'fire' class has index 0
            fire_indices = (cls == 0) & (conf > confidence_threshold)

            # Filter predictions for the 'fire' class
            fire_predictions = boxes.xyxy[fire_indices]

            if fire_predictions.size(0) > 0:
                return True

        return False

    def send_telegram_message(self, message):
        try:
            # Send message using Telegram bot
            bot = Bot(token=TELEGRAM_BOT_TOKEN)
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode=ParseMode.MARKDOWN)
            print("Telegram message sent successfully!")
        except Exception as e:
            print(f"Error sending Telegram message: {e}")

    def update(self):
        global start_time
        current_time = time.time()

        # Read a frame from the camera
        ret, frame = self.cap.read()

        if ret:
            dim = (700, 500)

            resized = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

            if current_time - start_time >= 0.25:
                results = model(resized)
                if self.fire_detected(results):
                    self.send_telegram_message("Fire detected!")
                annotated_frame = results[0].plot()
                start_time = time.time()
            else:
                annotated_frame = resized

            rgb_image = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)

            # Convert the RGB image to a Tkinter-compatible PhotoImage
            img = ImageTk.PhotoImage(Image.fromarray(rgb_image))

            # Update the canvas with the new image
            self.canvas.config(width=img.width(), height=img.height())
            self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
            self.canvas.image = img

            # Record the frame if video recording is enabled
            if self.is_recording:
                if self.video_writer is None:
                    # Initialize the video writer
                    fourcc = cv2.VideoWriter_fourcc(*"XVID")
                    width, height = frame.shape[1], frame.shape[0]
                    self.video_writer = cv2.VideoWriter("recorded_video.avi", fourcc, 20.0, (width, height))
                # Write the frame to the video file
                self.video_writer.write(frame)

        # Schedule the next update after 10 milliseconds
        self.root.after(10, self.update)

    def capture_photo(self):
        # Capture a photo and save it to a file (you can modify this part)
        ret, frame = self.cap.read()
        if ret:
            cv2.imwrite("captured_photo.jpg", frame)
            print("Photo captured!")

    def toggle_record(self):
        # Toggle video recording
        self.is_recording = not self.is_recording
        if self.is_recording:
            print("Recording started.")
        else:
            # Release the video writer when recording is stopped
            if self.video_writer is not None:
                self.video_writer.release()
                print("Recording stopped.")
            self.video_writer = None

    def exit_app(self):
        # Release the camera and close the application
        if self.is_recording:
            # Stop recording before exiting
            self.toggle_record()
        self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("710x600")
    app = CameraApp(root)
    root.mainloop()
