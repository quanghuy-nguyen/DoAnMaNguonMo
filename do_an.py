import tkinter as tk
from PIL import Image, ImageTk
import cv2
from ultralytics import YOLO
import time
from datetime import datetime
from telegram import Bot, ParseMode
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox


# Load the YOLOv8 model
model = YOLO('FireDetection.pt')

# Telegram bot token (initial values)
# TELEGRAM_BOT_TOKEN = '6634478065:AAFUNFufu7hj8WoAWa6TAYj6XxW0NRO5swg'
# TELEGRAM_CHAT_ID = '1886522458'


# Open the video file
video_path = "Fire.mp4"

cascadePath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath)

class CameraApp:
    def __init__(self, root):
        self.root = root
        self.cameraID = 0
        self.cap = cv2.VideoCapture(self.cameraID)
        self.cap.set(3, 640)
        self.cap.set(4, 480)
        self.minW = 0.1 * self.cap.get(3)
        self.minH = 0.1 * self.cap.get(4)
        self.file_path = ""
        self.moreBotToken = tk.StringVar()
        self.moreChatID = tk.StringVar()
        self.token = ["6634478065:AAFUNFufu7hj8WoAWa6TAYj6XxW0NRO5swg", ". . ."]
        self.chat_ID = ["1886522458", ". . ."]

        self.root.title("Camera System")

        # Tạo thanh menu
        menu_bar = tk.Menu(root)

        # Tạo menu File
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Choose Bot Token", command=self.addBotToken)
        file_menu.add_command(label="Choose Telegram Chat ID", command=self.addChatID)
        file_menu.add_command(label="Save", command=self.save)
        file_menu.add_command(label="Open", command=self.open)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Tạo menu Edit
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Config Camera ID", command=self.ChoosecameraID)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        # Tạo menu Help
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About us", command=self.about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        # Thiết lập thanh menu cho cửa sổ chính
        root.config(menu=menu_bar)

        self.BotToken = tk.StringVar()
        self.ChatID = tk.StringVar()
        self.CamerasID = tk.StringVar()

        self.capture_button = tk.Button(root, text="Capture", command=self.capture_photo, bg="LIGHTBLUE", font=('Helvetica',11))
        self.capture_button.place(x=610, y=510, width=100, height=50)

        self.record_button = tk.Button(root, text="Record", command=self.toggle_record, bg="LIGHTBLUE", font=('Helvetica',11))
        self.record_button.place(x=510, y=510, width=100, height=50)

        self.exit_button = tk.Button(root, text="Exit", command=self.exit_app, bg="LIGHTBLUE", font=('Helvetica',11))
        self.exit_button.place(x=710, y=510, width=100, height=50)

        self.is_recording = False
        self.video_writer = None
        self.record_start_time = None

        self.canvas = tk.Canvas(root, bg="sky blue")
        self.canvas.pack()

        # self.time_label = tk.Label(root, text="", font=("Helvetica", 12))
        # self.time_label.place(x=10, y=10)
        #
        # self.record_time_label = tk.Label(root, text="", font=("Helvetica", 12))
        # self.record_time_label.place(x=10, y=40)

        self.root.after(1000, self.update)


    ############### Menu commands: #############
    def addBotToken(self):
        self.label_teleBot = tk.Label(self.root, bg="steelblue", fg="white", text="Telegram Bot Token", font=('Helvetica', 15))
        self.label_teleBot.place(x=10, y=570)
        # self.token_entry = tk.Entry(root, width=30)
        # self.token_entry.place(x=150, y=510)
        # self.token_entry.insert(0, TELEGRAM_BOT_TOKEN)

        self.comboBox_ChooseBotToken = ttk.Combobox(self.root, width=27, textvariable=self.BotToken)
        self.comboBox_ChooseBotToken['values'] = ("6634478065:AAFUNFufu7hj8WoAWa6TAYj6XxW0NRO5swg",
                                         ". . .",
                                         )

        self.comboBox_ChooseBotToken.place(x=210, y=575)

        self.close_Btoken = tk.Button(self.root, text="Close",
                                   command=self.closeBotTokenWidget, bg="LIGHTBLUE", font=('Helvetica', 15))
        self.close_Btoken.place(x=410, y=575, width=55, height=25)

        self.update_button1 = tk.Button(self.root, text="Update Telegram Bot Token & Chat ID",
                                       command=self.update_telegram_BotToken, bg="LIGHTBLUE", font=('Helvetica', 15))
        self.update_button1.place(x=490, y=575, width=400, height=25)

    def addChatID(self):
        self.label_ChatID = tk.Label(self.root, bg="steelblue", fg="white", text="Telegram Chat ID", font=('Helvetica', 15))
        self.label_ChatID.place(x=10, y=620)
        # self.chat_id_entry = tk.Entry(root, width=30)
        # self.chat_id_entry.place(x=150, y=540)
        # self.chat_id_entry.insert(0, TELEGRAM_CHAT_ID)
        # 1886522458

        self.comboBox_ChooseChatID = ttk.Combobox(self.root, width=27, textvariable=self.ChatID)
        self.comboBox_ChooseChatID['values'] = ("1886522458",
                                       ". . .",
                                       )
        self.comboBox_ChooseChatID.place(x=210, y=625)

        self.close_cID = tk.Button(self.root, text="Close",
                                   command=self.closeChatIDWidget, bg="LIGHTBLUE", font=('Helvetica', 15))
        self.close_cID.place(x=410, y=625, width=55, height=25)

        self.update_button2 = tk.Button(self.root, text="Update Telegram Bot Token & Chat ID",
                                       command=self.update_telegramChatID, bg="LIGHTBLUE", font=('Helvetica', 15))
        self.update_button2.place(x=490, y=625, width=400, height=25)

    def save(self):
        browse_button = ttk.Button(self.root, text="Browse", command=lambda: print("Browse"))
        browse_button.place(x=10, y=10)
        browse_button.place_forget()

        self.file_path = filedialog.askdirectory()
        # print(self.file_path)

        # if self.file_path:
        #     browse_button.place(x=10, y=10)
        #     browse_button.config(command=lambda: self.browse_path(self.file_path))

    def open(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi")])
        if file_path:
            print("Đường dẫn file:", file_path)
            self.cameraID = file_path
            self.cap = cv2.VideoCapture(self.cameraID)
            self.ret, self.frame = self.cap.read()
            self.cap.set(3, 640)
            self.cap.set(4, 480)
            self.minW = 0.1 * self.cap.get(3)
            self.minH = 0.1 * self.cap.get(4)


    def ChoosecameraID(self):
        self.label_chooseID = tk.Label(self.root, bg="steelblue", fg="white", text="Choose Camera ID", font=('Helvetica', 15))
        self.label_chooseID.place(x=10, y=570)

        self.chooseID = ttk.Combobox(self.root, width=27, textvariable=self.CamerasID)
        self.chooseID['values'] = ("0", "1", "video_path")
        self.chooseID.place(x=210, y=575)

        self.confirm_button = tk.Button(self.root, text="Confirm",
                                      command=self.confirmCameraID, bg="LIGHTBLUE", font=('Helvetica', 15))
        self.confirm_button.place(x=410, y=575, width=100, height=25)

    def about(self):
        print("About command selected")
        new_window = tk.Toplevel(root)
        new_window.title("About us")

        label = tk.Label(new_window, text="Nhóm 5 xin chào người dùng! \n "
                                          "Nhóm 5 gồm những thành viên sau: \n"
                                          "Nguyễn Quang Huy \n"
                                          "Chử Tiến Duy \n"
                                          "Vũ Hoàng Anh \n"
                                          "Đỗ Nhật Anh")
        label.pack(padx=20, pady=20)

    def exit_app(self):
        if self.cap is not None:
            self.cap.release()
        if self.is_recording:
            self.toggle_record()
        self.root.destroy()

    # def browse_path(self):
    #     print(f"Selected path: {self.file_path}")

    def closeBotTokenWidget(self):
        if self.label_teleBot is not None:
            self.label_teleBot.place_forget()
        if self.comboBox_ChooseBotToken is not None:
            self.comboBox_ChooseBotToken.place_forget()
        self.update_button1.place_forget()
        self.close_Btoken.place_forget()

    def closeChatIDWidget(self):
        if self.label_ChatID is not None:
            self.label_ChatID.place_forget()
        if self.comboBox_ChooseChatID is not None:
            self.comboBox_ChooseChatID.place_forget()
        self.update_button2.place_forget()
        self.close_cID.place_forget()

    def confirmCameraID(self):
        self.ID = self.CamerasID.get()
        if self.ID is not None:
            if self.ID == "video_path":
                self.cameraID = video_path
            elif self.ID == "0":
                self.cameraID = 0
            elif self.ID == "1":
                self.cameraID = 1
            else:
                self.cameraID = 0
                messagebox.showerror('Camera ID Error', 'Error: Only accept interger!')

        print(self.cameraID)
        self.cap = cv2.VideoCapture(self.cameraID)
        self.ret, self.frame = self.cap.read()
        self.cap.set(3, 640)
        self.cap.set(4, 480)
        self.minW = 0.1 * self.cap.get(3)
        self.minH = 0.1 * self.cap.get(4)

        self.chooseID.place_forget()
        self.label_chooseID.place_forget()
        self.confirm_button.place_forget()


    def update_telegram_BotToken(self):
        global TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

        if self.BotToken.get() == ". . .":
            self.label_MorepBotToken = tk.Label(self.root, bg="steelblue", fg="white", text="Add more Bot Token",
                                           font=('Helvetica', 15))
            self.label_MorepBotToken.place(x=900, y=573)

            self.entryMoreBotToken = ttk.Entry(self.root, textvariable=self.moreBotToken)
            self.entryMoreBotToken.place(x=1110, y=575)

            self.buttonAddMoreToken = tk.Button(self.root, text="Add",
                                       command=self.closeAddMoreToken, bg="LIGHTBLUE", font=('Helvetica', 15))
            self.buttonAddMoreToken.place(x=1250, y=573, width=55, height=25)
        else:
            TELEGRAM_BOT_TOKEN = self.BotToken.get()

    def closeAddMoreToken(self):
        self.token.remove(". . .")
        self.moreBotToken = self.entryMoreBotToken.get()
        self.token.append(self.moreBotToken)
        self.token.append(". . .")
        tp = tuple(self.token)
        self.comboBox_ChooseBotToken['values'] = tp
        self.label_MorepBotToken.place_forget()
        self.entryMoreBotToken.place_forget()
        self.buttonAddMoreToken.place_forget()

    def update_telegramChatID(self):
        global TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

        if self.ChatID.get() == ". . .":
            self.label_MorepChatID = tk.Label(self.root, bg="steelblue", fg="white", text="Add more Chat ID",
                                                font=('Helvetica', 15))
            self.label_MorepChatID.place(x=920, y=623)

            self.entryMoreChatID = ttk.Entry(self.root, textvariable=self.moreChatID)
            self.entryMoreChatID.place(x=1110, y=627)

            self.buttonAddMoreChatID = tk.Button(self.root, text="Add",
                                                command=self.closeAddMoreChatID, bg="LIGHTBLUE", font=('Helvetica', 15))
            self.buttonAddMoreChatID.place(x=1250, y=623, width=55, height=25)
        else:
            TELEGRAM_CHAT_ID = self.ChatID.get()

    def closeAddMoreChatID(self):
        self.chat_ID.remove(". . .")
        self.moreChatID = self.entryMoreChatID.get()
        self.chat_ID.append(self.moreChatID)
        self.chat_ID.append(". . .")
        tp = tuple(self.chat_ID)
        self.comboBox_ChooseChatID['values'] = tp
        self.label_MorepChatID.place_forget()
        self.entryMoreChatID.place_forget()
        self.buttonAddMoreChatID.place_forget()

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
        self.ret, self.frame = self.cap.read()

        if self.ret:
            if self.cameraID == 0:
                dim = (700, 500)
            elif self.cameraID == video_path:
                dim = (760, 500)
            else:
                dim = dim = (700, 500)

            resized = cv2.resize(self.frame, dim, interpolation=cv2.INTER_AREA)

            results = model(resized)
            if self.fire_detected(results):
                self.send_telegram_message("Fire detected!")
            self.annotated_frame = results[0].plot()
            cv2.putText(self.annotated_frame, datetime.now().strftime('%d/%m/%Y %H:%M:%S'), (10, 20), cv2.FONT_HERSHEY_DUPLEX, 0.5,
                        (0, 210, 255))

            gray = cv2.cvtColor(self.annotated_frame, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.2,
                minNeighbors=5,
                minSize=(int(self.minW), int(self.minH)), )

            for (x, y, w, h) in faces:
                cv2.rectangle(self.annotated_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            self.rgb_image = cv2.cvtColor(self.annotated_frame, cv2.COLOR_BGR2RGB)

            img = ImageTk.PhotoImage(Image.fromarray(self.rgb_image))

            self.canvas.config(width=img.width(), height=img.height())
            self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
            self.canvas.image = img

            if self.is_recording:
                if self.video_writer is None:
                    fourcc = cv2.VideoWriter_fourcc(*"XVID")
                    width, height = self.annotated_frame.shape[1], self.annotated_frame.shape[0]
                    self.video_path = self.file_path + "/" + datetime.now().strftime("%H_%M_%S_%M_%d_%m_%Y") + ".avi"
                    self.video_writer = cv2.VideoWriter(self.video_path, fourcc, 5.0, (width, height))
                    self.record_start_time = time.time()

                # elapsed_time = time.time() - self.record_start_time
                # formatted_elapsed_time = time.strftime("Elapsed time: %H:%M:%S", time.gmtime(elapsed_time))
                # self.record_time_label.config(text=formatted_elapsed_time)

                self.video_writer.write(self.annotated_frame)

        self.root.after(10, self.update)

    def get_video(self):
        return self.rgb_image

    def capture_photo(self):
        # ret, frame = self.cap.read()
        # if ret:
        if self.file_path != "":
            self.path_pic = self.file_path + "/" + datetime.now().strftime("%H_%M_%S_%M_%d_%m_%Y") + "_photo.jpg"
            cv2.imwrite(self.path_pic, self.annotated_frame)
            print("Photo captured!")
        else:
            messagebox.showerror('File path Error', 'Error: You must choose a file path!')

    def toggle_record(self):
        if self.file_path != "":
            self.is_recording = not self.is_recording
            if self.is_recording:
                self.record_button.config(text="Stop Record")
                print("Recording started.")
            else:
                self.record_button.config(text="Record")
                if self.video_writer is not None:
                    self.video_writer.release()
                    print("Recording stopped.")
                self.video_writer = None
        else:
            messagebox.showerror('File path Error', 'Error: You must choose a file path!')


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1340x700")
    root.resizable(True, True)
    root.configure(background="sky blue")
    app = CameraApp(root)
    root.mainloop()