import random
import win32gui
import keyboard
import json
import os
import winsound

from animation_loader import load_frames
from PySide6.QtWidgets import QLabel, QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QTransform, QCursor
from animation_loader import load_frames

SKINS = [
    "assets_grey",
    "assets_orange",
    "assets_black",
    "assets_white",
]

MESSAGES = [
    "🐱 Keep working!",
    "☕ Drink some water!",
    "💾 Save your work!",
    "🚀 You're doing great!",
    "😴 Time for a short break!",
    "✨ You're doing awesome!",
    "🧠 One more bug to fix!",
    "🌟 Keep pushing forward!",
    "🐟 I deserve a treat!",
    "📚 Learning never stops!"
]



class Pet(QLabel):
    def __init__(self):
        super().__init__()
        

        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.current_skin = "assets_grey"

        self.idle_frames = load_frames("Idle", 120, self.current_skin)
        self.walk_frames = load_frames("Walk", 120, self.current_skin)
        self.run_frames = load_frames("Run", 120, self.current_skin)
        self.sleep_frames = load_frames("Dead", 120, self.current_skin)

        if not self.idle_frames:
            raise Exception(
                "Idle frames not found! Make sure assets contains "
                "'Idle (1).png', 'Idle (2).png', etc."
            )

        self.current_frames = self.idle_frames
        self.frame_index = 0

        self.setPixmap(self.current_frames[0])
        self.resize(self.pixmap().size())

        # Position (top-right)
        screen = QApplication.primaryScreen().availableGeometry()
        self.screen_width = screen.width()

        self.x_pos = self.screen_width - self.width() - 20
        self.y_pos = 20

        self.move(self.x_pos, self.y_pos)
        self.load_position()

        

        self.bubble = QLabel("", None)
        self.bubble.setWindowFlags(
            Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.bubble.setStyleSheet("""
            QLabel {
                background-color: #ffffff;
                color: black;
                border: 2px solid #444;
                border-radius: 10px;
                padding: 6px;
                font-size: 12px;
            }
        """)
        self.bubble.hide()

        # Walking state
        self.walking = False
        self.direction = -1
        self.steps_left = 0

        # Sleep state
        self.sleeping = False
        self.idle_counter = 0

        # Dragging state
        self.dragging = False
        self.drag_offset = None

        self.pet_enabled = True

        # Animation timer
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_animation)
        self.anim_timer.start(100)

        # Behaviour timer
        self.behaviour_timer = QTimer(self)
        self.behaviour_timer.timeout.connect(self.update_behaviour)
        self.behaviour_timer.start(250)

        # Global shortcut: Ctrl + Alt + C
        keyboard.add_hotkey("ctrl+alt+c", self.toggle_pet)

        # Random speech every 5 minutes
        self.message_timer = QTimer(self)
        self.message_timer.timeout.connect(self.show_random_message)
        self.message_timer.start(300000)

        # Mail reminder every 15 minutes
        self.mail_timer = QTimer(self)
        self.mail_timer.timeout.connect(self.show_mail_reminder)
        self.mail_timer.start(900000)

        # Change skin every 10 minutes
        self.skin_timer = QTimer(self)
        self.skin_timer.timeout.connect(self.change_skin)
        self.skin_timer.start(600000)   # 10 minutes

    def update_animation(self):
        if not self.current_frames:
            return

        self.frame_index = (self.frame_index + 1) % len(self.current_frames)
        pixmap = self.current_frames[self.frame_index]

        if self.direction == -1:
            pixmap = pixmap.transformed(
                QTransform().scale(-1, 1),
                Qt.SmoothTransformation
            )

        self.setPixmap(pixmap)

    def update_behaviour(self):
        

        if self.sleeping:
            return
        

        mouse = QCursor.pos()
        distance = abs(mouse.x() - self.x())

        if not self.walking and not self.dragging and distance < 80:
            self.current_frames = self.run_frames
            self.frame_index = 0

            if mouse.x() > self.x():
                self.direction = 1
            else:
                self.direction = -1

            self.walking = True
            self.steps_left = 30

        if self.bubble.isVisible():
            self.bubble.move(
                self.x(),
                self.y() - self.bubble.height() - 10
            )
       
        

        if self.walking:
            self.x_pos += self.direction * 2

            if self.x_pos < 10:
                self.x_pos = 10
                self.direction = 1

            if self.x_pos > self.screen_width - self.width() - 10:
                self.x_pos = self.screen_width - self.width() - 10
                self.direction = -1

            self.move(self.x_pos, self.y_pos)
            self.steps_left -= 1

            if self.steps_left <= 0:
                self.walking = False
                self.current_frames = self.idle_frames
                self.frame_index = 0

            return

        self.idle_counter += 1

        if (
            self.idle_counter > 200
            and self.sleep_frames
            and random.randint(1, 100) <= 30
        ):
            self.sleeping = True
            self.current_frames = [self.sleep_frames[-1]]
            self.frame_index = 0
            QTimer.singleShot(5000, self.wake_up)
            return

        if random.randint(1, 100) <= 1 and self.walk_frames:
            self.walking = True
            self.idle_counter = 0
            self.current_frames = self.walk_frames
            self.frame_index = 0
            self.direction = random.choice([1, -1])
            self.steps_left = random.randint(20, 40)
    
    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.save_position()
        super().mouseReleaseEvent(event)

    def mousePressEvent(self, event):
        if self.sleeping:
            self.wake_up()
            return

        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_offset = event.position().toPoint()

            action = random.choice(["Jump", "Run", "Slide"])
            frames = load_frames(action, 120,self.current_skin)

            if frames:
                self.current_frames = frames
                self.frame_index = 0

                duration_ms = max(len(frames) * 100, 800)
                QTimer.singleShot(duration_ms, self.back_to_idle)

        

    def mouseMoveEvent(self, event):
        if self.sleeping:
            self.wake_up()
            return

        if self.dragging:
            new_pos = self.pos() + event.position().toPoint() - self.drag_offset
            self.move(new_pos)
            self.x_pos = self.x()
            self.y_pos = self.y()


    def back_to_idle(self):
        self.current_frames = self.idle_frames
        self.frame_index = 0
        self.walking = False
        self.dragging = False
        self.idle_counter = 0

    def wake_up(self):
        self.sleeping = False
        self.idle_counter = 0
        self.current_frames = self.idle_frames
        self.frame_index = 0

    def save_position(self):
        data = {
            "x": self.x(),
            "y": self.y()
        }

        with open("cat_position.json", "w") as f:
            json.dump(data, f)

    def load_position(self):
        if os.path.exists("cat_position.json"):
            try:
                with open("cat_position.json", "r") as f:
                    data = json.load(f)

                self.x_pos = data.get("x", self.x_pos)
                self.y_pos = data.get("y", self.y_pos)

                self.move(self.x_pos, self.y_pos)

            except Exception:
                pass
   
    
    def toggle_pet(self):
        if self.pet_enabled:
            # Turn OFF
            self.pet_enabled = False

            self.setWindowOpacity(0.0)

            self.anim_timer.stop()
            self.behaviour_timer.stop()
            self.message_timer.stop()
            self.mail_timer.stop()
            self.skin_timer.stop()

        else:
            # Turn ON
            self.pet_enabled = True

            self.setWindowOpacity(1.0)

            self.anim_timer.start(100)
            self.behaviour_timer.start(250)
            self.message_timer.start(300000)   # 5 min
            self.mail_timer.start(900000)      # 15 min
            self.skin_timer.start(600000)      # 10 min
        
    def is_fullscreen_window(self):
        hwnd = win32gui.GetForegroundWindow()

        if not hwnd:
            return False

        rect = win32gui.GetWindowRect(hwnd)
        left, top, right, bottom = rect

        screen = QApplication.primaryScreen().availableGeometry()

        return (
            left <= 0
            and top <= 0
            and right >= screen.width()
            and bottom >= screen.height()
        )
    def play_meow(self):
        if random.random() < 0.5:  # 50% chance
            try:
                winsound.PlaySound(
                    "assets\\meow.wav",
                    winsound.SND_FILENAME | winsound.SND_ASYNC
                )
            except Exception:
                pass


    def show_speech_bubble(self, text):
        if not self.isVisible():
            return
        self.bubble.setText(text)
        self.bubble.adjustSize()

        self.bubble.move(
            self.x(),
            self.y() - self.bubble.height() - 10
        )

        self.bubble.show()

        self.play_meow()

        QTimer.singleShot(3000, self.bubble.hide)


    def show_random_message(self):
        if not hasattr(self, "last_message"):
            self.last_message = ""

        choices = [m for m in MESSAGES if m != self.last_message]
        message = random.choice(choices)

        self.last_message = message
        self.show_speech_bubble(message)

    def show_mail_reminder(self):
        if not self.bubble.isVisible():
            self.show_speech_bubble("📧 Check your mail!")

    def change_skin(self):
        available = [s for s in SKINS if s != self.current_skin]
        self.current_skin = random.choice(available)

        print("Switched to:", self.current_skin)

        self.idle_frames = load_frames("Idle", 120, self.current_skin)
        self.walk_frames = load_frames("Walk", 120, self.current_skin)
        self.run_frames = load_frames("Run", 120, self.current_skin)
        self.sleep_frames = load_frames("Dead", 120, self.current_skin)

        if self.idle_frames:
            self.current_frames = self.idle_frames
            self.frame_index = 0
            self.setPixmap(self.current_frames[0])