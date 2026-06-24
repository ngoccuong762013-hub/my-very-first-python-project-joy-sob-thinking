import subprocess
import sys
try:
    import PyQt5
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt5"])

try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])

import random
import time
import re
import ast
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QTabWidget, QLabel, 
                             QPushButton, QLineEdit, QTextEdit, QMessageBox, 
                             QListWidget)
from PyQt5.QtCore import QTimer, Qt, QUrl, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
class StopwatchLogic:
    def __init__(self):
        self.start_time = None
        self.elapsed_time = 0
        self.running = False

    def start(self):
        if not self.running:
            self.start_time = time.time() - self.elapsed_time
            self.running = True

    def stop(self):
        if self.running:
            self.elapsed_time = time.time() - self.start_time
            self.running = False

    def reset(self):
        self.start_time = None
        self.elapsed_time = 0
        self.running = False

    def get_elapsed(self):
        if self.running:
            return time.time() - self.start_time
        return self.elapsed_time


class WeatherWorker(QThread):
    finished_signal = pyqtSignal(dict)

    def __init__(self, city):
        super().__init__()
        self.city = city

    def run(self):
        try:
            cleaned_city = self.city.strip().lower()
            safe_city = requests.utils.quote(cleaned_city)
            url = f"https://wttr.in/{safe_city}?format=j1"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                current = data["current_condition"][0]
                temp_c = current["temp_C"]
                desc = current["weatherDesc"][0]["value"]
                humidity = current["humidity"]
                code = current["weatherCode"]
                
                self.finished_signal.emit({
                    "success": True,
                    "temp": temp_c,
                    "desc": desc,
                    "humidity": humidity,
                    "code": code
                })
            else:
                self.finished_signal.emit({"success": False, "error": f"Error code: {response.status_code}"})
        except Exception as e:
            self.finished_signal.emit({"success": False, "error": str(e)})


class GameHubApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LIL GAME HUB")
        self.setGeometry(100, 100, 500, 600)
        
        self.DATA_FILE = "hub_data.json"
        self.load_data()
        
        self.alarm_time = None
        self.player = QMediaPlayer()
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.init_ngg_tab()
        self.init_calc_tab()
        self.init_rps_tab()
        self.init_hangman_tab()
        self.init_alarm_tab()
        self.init_stopwatch_tab()
        self.init_digital_clock_tab()
        self.init_weather_tab()
        self.init_stats_tab()
        
        self.alarm_timer = QTimer()
        self.alarm_timer.timeout.connect(self.check_alarm)
        self.alarm_timer.start(1000)

    def load_data(self):
        default_stats = {
            "ngg win(s)": 0, "rps win(s)": 0, "rps_comp_win(s)": 0,
            "ngg miss(es)": 0, "ngg total attempt(s)": 0,
            "hangman win(s)": 0, "hangman loss(es)": 0
        }
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, "r") as f:
                    saved = json.load(f)
                    self.stats = saved.get("stats", default_stats)
                    self.calc_history = saved.get("calc_history", [])
                    return
            except Exception:
                pass
        self.stats = default_stats
        self.calc_history = []

    def save_data(self):
        try:
            with open(self.DATA_FILE, "w") as f:
                json.dump({"stats": self.stats, "calc_history": self.calc_history}, f, indent=4)
        except Exception as e:
            print(f"Error saving data: {e}")

    def init_ngg_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        self.ngg_secret = random.randint(1, 1000)
        self.ngg_attempts = 0
        self.ngg_label = QLabel("Guess a number between 1 and 1000:")
        self.ngg_input = QLineEdit()
        btn = QPushButton("Submit Guess")
        btn.clicked.connect(self.play_ngg)
        self.ngg_output = QLabel("")
        layout.addWidget(self.ngg_label)
        layout.addWidget(self.ngg_input)
        layout.addWidget(btn)
        layout.addWidget(self.ngg_output)
        widget.setLayout(layout)
        self.tabs.addTab(widget, "Guessing Game")
        
    def play_ngg(self):
        try:
            guess = int(self.ngg_input.text())
        except ValueError:
            self.ngg_output.setText("Invalid input! Please enter a number.")
            return
        self.ngg_attempts += 1
        self.stats["ngg total attempt(s)"] += 1
        if guess == self.ngg_secret:
            self.ngg_output.setText(f"You guessed it! Attempts: {self.ngg_attempts}")
            self.stats["ngg win(s)"] += 1
            self.ngg_secret = random.randint(1, 1000)  
            self.ngg_attempts = 0
        elif guess < self.ngg_secret:
            self.ngg_output.setText("Too low!")
            self.stats["ngg miss(es)"] += 1
        else:
            self.ngg_output.setText("Too high!")
            self.stats["ngg miss(es)"] += 1
        self.ngg_input.clear()
        self.save_data()
        self.update_stats_display()

    def init_calc_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        self.calc_display = QLineEdit()
        self.calc_display.setReadOnly(True)
        self.calc_display.setAlignment(Qt.AlignRight)
        layout.addWidget(self.calc_display)
        grid_layout = QGridLayout()
        buttons = [
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['C', '0', '=', '+']
        ]
        for r_idx, row in enumerate(buttons):
            for c_idx, label in enumerate(row):
                btn = QPushButton(label)
                btn.clicked.connect(lambda checked, l=label: self.on_calc_click(l))
                grid_layout.addWidget(btn, r_idx, c_idx)
        layout.addLayout(grid_layout)
        self.calc_history_list = QListWidget()
        self.calc_history_list.addItems(self.calc_history)
        layout.addWidget(QLabel("Last 5 Calculations:"))
        layout.addWidget(self.calc_history_list)
        widget.setLayout(layout)
        self.tabs.addTab(widget, "Calculator")
        
    def safe_eval(self, expr):
        allowed_nodes = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Constant)
        try:
            tree = ast.parse(expr, mode='eval')
            for node in ast.walk(tree):
                if not isinstance(node, allowed_nodes):
                    raise ValueError("Unsafe node detected")
            return eval(compile(tree, filename='', mode='eval'))
        except Exception:
            raise ValueError("Invalid Expression")

    def on_calc_click(self, label):
        current_text = self.calc_display.text()
        if label == 'C':
            self.calc_display.clear()
        elif label == '=':
            if not current_text:
                return
            if "/0" in current_text or "/ 0" in current_text:
                QMessageBox.warning(self, "Math Error", "Cannot divide by zero.")
                self.calc_display.clear()
                return
            try:
                result = self.safe_eval(current_text)
                entry = f"{current_text} = {result}"
                self.calc_display.setText(str(result))
                self.calc_history.append(entry)
                if len(self.calc_history) > 5:
                    self.calc_history.pop(0)
                self.calc_history_list.clear()
                self.calc_history_list.addItems(self.calc_history)
                self.save_data()
            except Exception:
                self.calc_display.setText("Error")
        else:
            self.calc_display.setText(current_text + label)

    def init_rps_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        self.rps_output = QLabel("Choose your weapon!")
        layout.addWidget(self.rps_output)
        h_layout = QHBoxLayout()
        for choice in ["rock", "paper", "scissors"]:
            btn = QPushButton(choice.capitalize())
            btn.clicked.connect(lambda checked, c=choice: self.play_rps(c))
            h_layout.addWidget(btn)
        layout.addLayout(h_layout)
        widget.setLayout(layout)
        self.tabs.addTab(widget, "RPS")
        
    def play_rps(self, user_choice):
        options = ["rock", "paper", "scissors"]
        winning_combos = [("rock", "scissors"), ("scissors", "paper"), ("paper", "rock")]
        computer_choice = random.choice(options)
        result_str = f"You picked: {user_choice}.\nComputer picked: {computer_choice}.\n"
        if user_choice == computer_choice:
            result_str += "It's a tie!"
        elif (user_choice, computer_choice) in winning_combos:
            result_str += "You won!"
            self.stats["rps win(s)"] += 1
        else:
            result_str += "Computer won!"
            self.stats["rps_comp_win(s)"] += 1
        self.rps_output.setText(result_str)
        self.save_data()
        self.update_stats_display()

    def init_hangman_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        self.hm_words = ["python", "programming", "challenge", "developer", "algorithm"]
        self.hangman_art = {
            0: "*********\n\n\n\n*********",
            1: "*********\n O \n\n\n*********",
            2: "*********\n O \n |\n\n*********",
            3: "*********\n O \n/|\n\n*********",
            4: "*********\n O \n/|\\\n\n*********",
            5: "*********\n O \n/|\\\n/  \n*********",
            6: "*********\n O \n/|\\\n/ \\\n*********"
        }
        self.hm_display_art = QLabel(self.hangman_art[0])
        self.hm_display_art.setFont(QFont("Courier New", 12))
        self.hm_display_hint = QLabel("")
        self.hm_input = QLineEdit()
        self.hm_btn = QPushButton("Guess Letter")
        self.hm_btn.clicked.connect(self.play_hangman)
        layout.addWidget(self.hm_display_art)
        layout.addWidget(self.hm_display_hint)
        layout.addWidget(self.hm_input)
        layout.addWidget(self.hm_btn)
        widget.setLayout(layout)
        self.tabs.addTab(widget, "Hangman")
        self.reset_hangman()
        
    def reset_hangman(self):
        self.hm_answer = random.choice(self.hm_words)
        self.hm_hint = ["_"] * len(self.hm_answer)
        self.hm_wrong = 0
        self.hm_guessed = set()
        self.hm_display_art.setText(self.hangman_art[0])
        self.hm_display_hint.setText(" ".join(self.hm_hint))
        
    def play_hangman(self):
        guess = self.hm_input.text().lower().strip()
        self.hm_input.clear()
        if not guess or len(guess) != 1 or not guess.isalpha():
            return
        if guess in self.hm_guessed:
            return
        self.hm_guessed.add(guess)
        if guess in self.hm_answer:
            for i, letter in enumerate(self.hm_answer):
                if letter == guess:
                    self.hm_hint[i] = guess
            self.hm_display_hint.setText(" ".join(self.hm_hint))
            if "_" not in self.hm_hint:
                QMessageBox.information(self, "Winner", f"You win! The word was {self.hm_answer}")
                self.stats["hangman win(s)"] += 1
                self.save_data()
                self.reset_hangman()
        else:
            self.hm_wrong += 1
            if self.hm_wrong in self.hangman_art:
                self.hm_display_art.setText(self.hangman_art[self.hm_wrong])
            if self.hm_wrong >= 6:
                QMessageBox.critical(self, "Game Over", f"You lost! The answer was: {self.hm_answer}")
                self.stats["hangman loss(es)"] += 1
                self.save_data()
                self.reset_hangman()
        self.update_stats_display()

    def init_alarm_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        self.alarm_input = QLineEdit()
        self.alarm_input.setPlaceholderText("HH:MM (e.g. 15:30)")
        btn = QPushButton("Set Alarm")
        btn.clicked.connect(self.set_gui_alarm)
        self.alarm_status = QLabel("No alarm active.")
        self.stop_sound_btn = QPushButton("🔴 STOP MUSIC")
        self.stop_sound_btn.setStyleSheet("background-color: #ff4d4d; color: white; font-weight: bold;")
        self.stop_sound_btn.clicked.connect(self.stop_alarm_music)
        self.stop_sound_btn.hide() 
        layout.addWidget(QLabel("Set 24-Hour Alarm:"))
        layout.addWidget(self.alarm_input)
        layout.addWidget(btn)
        layout.addWidget(self.alarm_status)
        layout.addWidget(self.stop_sound_btn) 
        widget.setLayout(layout)
        self.tabs.addTab(widget, "Alarm")
        
    def set_gui_alarm(self):
        self.alarm_time = self.alarm_input.text().strip()
        if re.match(r"^\d{2}:\d{2}$", self.alarm_time):
            self.alarm_status.setText(f"Alarm initialized for {self.alarm_time}")
            self.stop_sound_btn.hide()
        else:
            QMessageBox.warning(self, "Format Error", "Please use HH:MM format (24-hour style).")
            self.alarm_time = None
        
    def check_alarm(self):
        if self.alarm_time and time.strftime("%H:%M") == self.alarm_time:
            self.alarm_time = None 
            self.alarm_status.setText("Alarm Ringing!")           
            try:
                url = QUrl.fromLocalFile("Never Gonna Give You Up.wav")
                content = QMediaContent(url)
                self.player.setMedia(content)
                self.player.play()
                self.stop_sound_btn.show()
            except Exception as e:
                print(f"Error playing sound: {e}")
            QMessageBox.warning(self, "Alarm", "Wake up son 😂😭)")

    def stop_alarm_music(self):
        self.player.stop()
        self.stop_sound_btn.hide()
        self.alarm_status.setText("No alarm active.")

    def init_stopwatch_tab(self):
        self.sw_logic = StopwatchLogic()
        widget = QWidget()
        layout = QVBoxLayout()
        self.sw_label = QLabel("00:00:00.00")
        self.sw_label.setAlignment(Qt.AlignCenter)
        self.sw_label.setFont(QFont("Courier New", 28, QFont.Bold))
        layout.addWidget(self.sw_label)
        btn_layout = QHBoxLayout()
        start_btn = QPushButton("Start")
        start_btn.clicked.connect(self.start_sw)
        stop_btn = QPushButton("Stop")
        stop_btn.clicked.connect(self.stop_sw)
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_sw)
        btn_layout.addWidget(start_btn)
        btn_layout.addWidget(stop_btn)
        btn_layout.addWidget(reset_btn)
        layout.addLayout(btn_layout)
        widget.setLayout(layout)
        self.tabs.addTab(widget, "Stopwatch")
        self.sw_display_timer = QTimer()
        self.sw_display_timer.timeout.connect(self.update_sw_display)

    def start_sw(self):
        self.sw_logic.start()
        self.sw_display_timer.start(10)

    def stop_sw(self):
        self.sw_logic.stop()
        self.sw_display_timer.stop()

    def reset_sw(self):
        self.sw_logic.reset()
        self.sw_display_timer.stop()
        self.sw_label.setText("00:00:00.00")

    def update_sw_display(self):
        total_seconds = self.sw_logic.get_elapsed()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        centiseconds = int((total_seconds % 1) * 100)
        self.sw_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}")

    def init_digital_clock_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        self.clock_label = QLabel()
        self.clock_label.setAlignment(Qt.AlignCenter)
        self.clock_label.setFont(QFont("Courier New", 28, QFont.Bold))
        layout.addWidget(self.clock_label)
        widget.setLayout(layout)
        self.tabs.addTab(widget, "Digital Clock")
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock_display)
        self.clock_timer.start(1000)
        
    def update_clock_display(self):
        self.clock_label.setText(time.strftime("%H:%M:%S"))

    def init_weather_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.weather_city_input = QLineEdit()
        self.weather_city_input.setPlaceholderText("Enter city name (e.g., London, New York)...")
        
        self.weather_btn = QPushButton("Get Weather")
        self.weather_btn.clicked.connect(self.fetch_weather)
        
        self.weather_output_icon = QLabel("")
        self.weather_output_icon.setAlignment(Qt.AlignCenter)
        self.weather_output_icon.setFont(QFont("Arial", 48))
        
        self.weather_output_text = QLabel("Enter a city to check the forecast.")
        self.weather_output_text.setAlignment(Qt.AlignCenter)
        self.weather_output_text.setFont(QFont("Arial", 12))
        
        layout.addWidget(QLabel("Global Weather Tracker (No API Key Required):"))
        layout.addWidget(self.weather_city_input)
        layout.addWidget(self.weather_btn)
        layout.addWidget(self.weather_output_icon)
        layout.addWidget(self.weather_output_text)
        widget.setLayout(layout)
        self.tabs.addTab(widget, "Weather")

    def fetch_weather(self):
        city = self.weather_city_input.text().strip()
        if not city:
            QMessageBox.warning(self, "Input Error", "Please provide a valid city name.")
            return
        
        self.weather_btn.setEnabled(False)
        self.weather_output_text.setText("Loading matching data stream...")
        self.weather_output_icon.setText("⏳")
        
        self.weather_thread = WeatherWorker(city)
        self.weather_thread.finished_signal.connect(self.handle_weather_result)
        self.weather_thread.start()

    def handle_weather_result(self, result):
        self.weather_btn.setEnabled(True)
        if not result["success"]:
            self.weather_output_icon.setText("❌")
            self.weather_output_text.setText(f"Failed to find weather info.\n{result['error']}")
            return

        emoji_map = {
            "113": "☀️", "116": "⛅", "119": "☁️", "122": "☁️", 
            "143": "🌫️", "176": "🌦️", "179": "🌨️", "182": "🌨️",
            "200": "⛈️", "227": "💨", "230": "❄️", "248": "🌫️",
            "260": "🌫️", "263": "🌦️", "266": "🌧️", "293": "🌧️",
            "296": "🌧️", "299": "🌧️", "302": "🌧️", "305": "🌧️",
            "308": "🌧️", "353": "🌦️", "356": "🌧️", "359": "🌧️"
        }
        
        code = result["code"]
        emoji = "🌡️"
        for prefix in emoji_map:
            if code.startswith(prefix):
                emoji = emoji_map[prefix]
                break
        
        desc = result["desc"]
        if "sunny" in desc.lower(): emoji = "☀️"
        elif "clear" in desc.lower(): emoji = "🌙" if "night" in desc.lower() else "☀️"
        elif "rain" in desc.lower(): emoji = "🌧️"
        elif "snow" in desc.lower(): emoji = "❄️"
        elif "thunder" in desc.lower(): emoji = "⛈️"
        elif "cloud" in desc.lower(): emoji = "☁️"

        self.weather_output_icon.setText(emoji)
        
        display_city = self.weather_city_input.text().strip().title()
        self.weather_output_text.setText(
            f"City: {display_city}\n"
            f"Temperature: {result['temp']}°C\n"
            f"Condition: {desc}\n"
            f"Humidity: {result['humidity']}%"
        )

    def init_stats_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        self.stats_box = QTextEdit()
        self.stats_box.setReadOnly(True)
        reset_btn = QPushButton("Reset Stats and History")
        reset_btn.clicked.connect(self.reset_gui_stats)
        layout.addWidget(self.stats_box)
        layout.addWidget(reset_btn)
        widget.setLayout(layout)
        self.tabs.addTab(widget, "Stats")
        self.update_stats_display()
        
    def update_stats_display(self):
        display_text = "==== STATS ====\n"
        for game, wins in self.stats.items():
            display_text += f"{game}: {wins}\n"
        if self.stats["ngg win(s)"] > 0:
            avg = self.stats["ngg total attempt(s)"] / self.stats["ngg win(s)"]
            display_text += f"Average attempts: {round(avg, 2)}\n"
        self.stats_box.setText(display_text)
        
    def reset_gui_stats(self):
        confirm = QMessageBox.question(self, "Confirm Reset", "Wipe stats and history?", 
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            for key in self.stats:
                self.stats[key] = 0
            self.calc_history.clear()
            self.calc_history_list.clear()
            self.reset_hangman() 
            self.ngg_secret = random.randint(1, 1000)
            self.ngg_attempts = 0
            self.save_data()
            self.update_stats_display()
            QMessageBox.information(self, "Reset", "rip stats lol")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameHubApp()
    window.show()
    sys.exit(app.exec_())

    #I did use ai but the purpose was to fix my spacing, formatting issues and make the code more readable :joy
    #I did follow some tutorials on Youtube cuz cmon, how do u expect me to start making something this much from scratch :thinking:
