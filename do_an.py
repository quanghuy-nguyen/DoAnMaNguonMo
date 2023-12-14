from tkinter import Tk, Entry, StringVar
from tkinter.ttk import Label, Button
import cv2
from PIL import ImageTk, Image
from ultralytics import YOLO
from telegram import Bot, ParseMode

# Load the YOLOv8 model
model = YOLO('Fire.pt')

# Default values for Telegram token and chat ID
DEFAULT_TELEGRAM_BOT_TOKEN = 'YOUR_DEFAULT_TELEGRAM_BOT_TOKEN'
DEFAULT_TELEGRAM_CHAT_ID = 'YOUR_DEFAULT_TELEGRAM_CHAT_ID'

# Open the video file
video_path = "Fire.mp4"


class Window(Tk):
    def __init__(self):
        super().__init__()
        self.wm_title("Camera")
        self.geometry("550x420")

        # Add entry fields for Telegram Bot Token and Chat ID
        self.telegram_token_var = StringVar(value=DEFAULT_TELEGRAM_BOT_TOKEN)
        self.telegram_chat_id_var = StringVar(value=DEFAULT_TELEGRAM_CHAT_ID)

        Label(self, text="Telegram Bot Token:").place(x=50, y=320)
        Entry(self, textvariable=self.telegram_token_var).place(x=200, y=320, width=200)

        Label(self, text="Telegram Chat ID:").place(x=50, y=350)
        Entry(self, textvariable=self.telegram_chat_id_var).place(x=200, y=350, width=200)

        # Add button
        button_1 = Button(self, text="Show Camera", command=self.show_frames)
        button_1.place(x=235, y=380, width=100, height=30)

        # Add a label
        self.label = Label(self, text="Camera Interface")
        self.label.place(x=80, y=20)

        # Initialize OpenCV video capture
        self.cap = cv2.VideoCapture(video_path)

    def show_frames(self):
        # Update TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID with user input
        TELEGRAM_BOT_TOKEN = self.telegram_token_var.get()
        TELEGRAM_CHAT_ID = int(self.telegram_chat_id_var.get())

        ret, frame = self.cap.read()
        # take width, height of image
        scale_percent = 30  # percent of original size
        width = int(frame.shape[1] * scale_percent / 100)
        height = int(frame.shape[0] * scale_percent / 100)
        dim = (width, height)

        # Resize image
        resized = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
        results = model(resized)

        # Visualize the results on the frame
        annotated_frame = results[0].plot()

        # Convert cv2 image to PIL Image
        cv2image = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)

        # Convert PIL Image to tkinter image
        tkimage = ImageTk.PhotoImage(image=img)
        self.label.imgtk = tkimage
        self.label.configure(image=tkimage)

        # Check if fire is detected and send Telegram message if true
        if fire_detected(results):
            send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, "Fire detected!")

        # Repeat after an interval to capture continuously
        self.label.after(20, self.show_frames)

def fire_detected(results_list, confidence_threshold=0.5):
    for results in results_list:
        boxes = results.boxes
        conf = boxes.conf
        cls = boxes.cls

        fire_indices = (cls == 0) & (conf > confidence_threshold)

        fire_predictions = boxes.xyxy[fire_indices]

        if fire_predictions.size(0) > 0:
            return True

    return False

def send_telegram_message(telegram_bot_token, telegram_chat_id, message):
    try:
        # Send message using Telegram bot
        bot = Bot(token=telegram_bot_token)
        bot.send_message(chat_id=telegram_chat_id, text=message, parse_mode=ParseMode.MARKDOWN)
        print("Telegram message sent successfully!")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

if __name__ == "__main__":
    app = Window()
    app.mainloop()
