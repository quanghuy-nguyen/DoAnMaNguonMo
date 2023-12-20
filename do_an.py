import tkinter as tk
from PIL import Image, ImageTk
import cv2
from ultralytics import YOLO
import torch
import time
from datetime import datetime
from telegram import Bot, ParseMode

# Load the YOLOv8 model
model = YOLO('Fire.pt')

# Telegram bot token (initial values)
TELEGRAM_BOT_TOKEN = '6634478065:AAFUNFufu7hj8WoAWa6TAYj6XxW0NRO5swg'
TELEGRAM_CHAT_ID = '1886522458'

# Open the video file
video_path = "Fire.mp4"
start_time = time.time()

class CameraApp:
    def __init__(self, root, camera_index=0):
        self.root = root
        self.root.title("Tkinter Camera GUI")

        tk.Label(root, text="Telegram Bot Token:").place(x=10, y=510)
        self.token_entry = tk.Entry(root, width=30)
        self.token_entry.place(x=150, y=510)
        self.token_entry.insert(0, TELEGRAM_BOT_TOKEN)

        tk.Label(root, text="Telegram Chat ID:").place(x=10, y=540)
        self.chat_id_entry = tk.Entry(root, width=30)
        self.chat_id_entry.place(x=150, y=540)
        self.chat_id_entry.insert(0, TELEGRAM_CHAT_ID)

        self.update_button = tk.Button(root, text="Update Telegram Bot Token & Chat ID", command=self.update_telegram_credentials)
        self.update_button.place(x=350, y=520, width=250, height=25)

        self.capture_button = tk.Button(root, text="Capture Photo", command=self.capture_photo)
        self.capture_button.place(x=310, y=570, width=100, height=50)

        self.record_button = tk.Button(root, text="Record Video", command=self.toggle_record)
        self.record_button.place(x=210, y=570, width=100, height=50)

        self.start_video_button = tk.Button(root, text="Start Video", command=self.start_video)
        self.start_video_button.place(x=110, y=570, width=100, height=50)

        self.exit_button = tk.Button(root, text="Exit", command=self.exit_app)
        self.exit_button.place(x=410, y=570, width=100, height=50)

        self.is_recording = False
        self.video_writer = None
        self.record_start_time = None

        self.canvas = tk.Canvas(root)
        self.canvas.pack()

        self.time_label = tk.Label(root, text="", font=("Helvetica", 12))
        self.time_label.place(x=10, y=10)

        self.record_time_label = tk.Label(root, text="", font=("Helvetica", 12))
        self.record_time_label.place(x=10, y=40)

        self.root.after(1000, self.update)

    def start_video(self):
        self.cap = cv2.VideoCapture(video_path)
        self.update()

    def update_telegram_credentials(self):
        global TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
        TELEGRAM_BOT_TOKEN = self.token_entry.get()
        TELEGRAM_CHAT_ID = self.chat_id_entry.get()

    def fire_detected(self, results_list, confidence_threshold=0.5):
        for results in results_list:
            boxes = results.boxes
            conf = boxes.conf
            cls = boxes.cls

            fire_indices = (cls == 0) & (conf > confidence_threshold)

            fire_predictions = boxes.xyxy[fire_indices]

            if fire_predictions.size(0) > 0:
                return True

        return False

    def send_telegram_message(self, message):
        try:
            bot = Bot(token=TELEGRAM_BOT_TOKEN)
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode=ParseMode.MARKDOWN)
            print("Telegram message sent successfully!")
        except Exception as e:
            print(f"Error sending Telegram message: {e}")

    def update(self):
        global start_time
        current_time = time.time()

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

            img = ImageTk.PhotoImage(Image.fromarray(rgb_image))

            self.canvas.config(width=img.width(), height=img.height())
            self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
            self.canvas.image = img

            if self.is_recording:
                if self.video_writer is None:
                    fourcc = cv2.VideoWriter_fourcc(*"XVID")
                    width, height = frame.shape[1], frame.shape[0]
                    self.video_writer = cv2.VideoWriter("recorded_video.avi", fourcc, 20.0, (width, height))
                    self.record_start_time = time.time()

                elapsed_time = time.time() - self.record_start_time
                formatted_elapsed_time = time.strftime("Elapsed time: %H:%M:%S", time.gmtime(elapsed_time))
                self.record_time_label.config(text=formatted_elapsed_time)

                self.video_writer.write(frame)

            current_datetime = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
            self.time_label.config(text=current_datetime)

        self.root.after(10, self.update)

    def capture_photo(self):
        ret, frame = self.cap.read()
        if ret:
            cv2.imwrite("captured_photo.jpg", frame)
            print("Photo captured!")

    def toggle_record(self):
        self.is_recording = not self.is_recording
        if self.is_recording:
            print("Recording started.")
        else:
            if self.video_writer is not None:
                self.video_writer.release()
                print("Recording stopped.")
            self.video_writer = None

    def exit_app(self):
        if self.cap is not None:
            self.cap.release()
        if self.is_recording:
            self.toggle_record()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("710x600")
    app = CameraApp(root)
    root.mainloop()
