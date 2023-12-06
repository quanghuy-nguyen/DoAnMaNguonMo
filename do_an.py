from tkinter import Tk
from tkinter.ttk import Label, Button
import cv2
from PIL import ImageTk, Image
from twilio.rest import Client
from ultralytics import YOLO

# Load the YOLOv8 model
model = YOLO('Fire.pt')

# Thông tin tài khoản Twilio
account_sid = "ACa500143412b1f6e967fbc7bcdf9f2caf"
auth_token = "a97146171222b703f60d771644901f23"
from_phone_number = "+18584139983"
to_phone_number = "+84352191790"

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
        # print("Original Dimentions: ", frame.shape)
        scale_percent = 30  # percent of original size
        width = int(frame.shape[1] * scale_percent / 100)
        height = int(frame.shape[0] * scale_percent / 100)
        dim = (width, height)

        # Resize image
        resized = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
        # print("Resized Dimensions: ", resized.shape)
        results = model(resized)

        # Kiểm tra xem có phát hiện cháy không
        if any(result.boxes.shape[0] > 0 for result in results):
            # Nếu có cháy, gửi thông báo
            self.send_notification()

        # Visualize the results on the frame
        for result in results:
            annotated_frame = result.plot()

            # Convert cv2 image to PIL Image
            cv2image = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)

            img = Image.fromarray(cv2image)

            # Convert PIL Image to tkinter image
            tkimage = ImageTk.PhotoImage(image=img)
            self.label.imgtk = tkimage
            self.label.configure(image=tkimage)

            # Repeat after an interval to capture continuously
            self.label.after(20, self.show_frames)



    def send_notification(self):
        # Tạo đối tượng Client Twilio
        client = Client(account_sid, auth_token)

        # Nội dung tin nhắn
        message_body = "Cháy được phát hiện! Cần kiểm tra ngay."

        # Gửi tin nhắn
        message = client.messages.create(
            body=message_body,
            from_=from_phone_number,
            to=to_phone_number
        )

        print(f"Đã gửi thông báo: {message.sid}")

if __name__ == "__main__":
    app = Window()
    app.mainloop()
