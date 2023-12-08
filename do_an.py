from tkinter import Tk
from tkinter.ttk import Label, Button
import cv2
from PIL import ImageTk, Image
from ultralytics import YOLO


from telegram import Bot, ParseMode



# Load the YOLOv8 model
model = YOLO('Fire.pt')

# Telegram bot token
TELEGRAM_BOT_TOKEN = '6634478065:AAFUNFufu7hj8WoAWa6TAYj6XxW0NRO5swg'
TELEGRAM_CHAT_ID = 1886522458

# Open the video file
video_path = "Fire.mp4"


class Window(Tk):
    def __init__(self):
        super().__init__()
        self.wm_title("Camera")
        self.geometry("550x420")

        # add button
        button_1 = Button(self, text="show camera", command=self.show_frames)
        button_1.place(x=235, y=350, width=100, height=50)
        # add a label
        self.label = Label(self, text="Giao dien camera")
        self.label.place(x=80, y=20)

        # ================== cv2 ===============
        self.cap = cv2.VideoCapture("Fire.mp4")

    def show_frames(self):
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
            send_telegram_message("Fire detected!")

        # Repeat after an interval to capture continuously
        self.label.after(20, self.show_frames)


def fire_detected(results_list, confidence_threshold=0.5):
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


def send_telegram_message(message):
    try:
        # Send message using Telegram bot
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode=ParseMode.MARKDOWN)
        print("Telegram message sent successfully!")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")


if __name__ == "__main__":
    app = Window()
    app.mainloop()
