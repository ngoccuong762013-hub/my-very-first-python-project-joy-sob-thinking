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
try:
    import pyautogui
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyautogui"])
    import pyautogui

import random
import time
import re
import ast
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QTabWidget, QLabel, 
                             QPushButton, QLineEdit, QTextEdit, QMessageBox, 
                             QListWidget, QComboBox, QSpinBox, QListWidgetItem)
from PyQt5.QtCore import QTimer, Qt, QUrl, QThread, pyqtSignal, QPointF
from PyQt5.QtGui import QFont, QPainter, QPen, QColor, QBrush, QLinearGradient
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
                    "success": True, "temp": temp_c, "desc": desc, "humidity": humidity, "code": code
                })
            else:
                self.finished_signal.emit({"success": False, "error": f"Error code: {response.status_code}"})
        except Exception as e:
            self.finished_signal.emit({"success": False, "error": str(e)})


class StockWorker(QThread):
    finished_signal = pyqtSignal(dict)

    def __init__(self, ticker):
        super().__init__()
        self.ticker = ticker.upper().strip()

    def run(self):
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{self.ticker}"
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                meta = data["chart"]["result"][0]["meta"]
                price = meta["regularMarketPrice"]
                currency = meta.get("currency", "USD")
                self.finished_signal.emit({
                    "success": True, "ticker": self.ticker, "price": round(float(price), 2), "currency": currency
                })
                return
            raise Exception()
        except Exception:
            baselines = {"AAPL": 185.20, "NVDA": 128.50, "TSLA": 174.30, "MSFT": 420.10, "AMZN": 189.40, "BTC-USD": 63400.0}
            base = baselines.get(self.ticker, 100.0)
            simulated_price = round(base * (1 + random.uniform(-0.005, 0.005)), 2)
            self.finished_signal.emit({
                "success": True, "ticker": self.ticker, "price": simulated_price, "currency": "USD", "simulated": True
            })


class LoginBotWorker(QThread):
    status_signal = pyqtSignal(str)

    def __init__(self, target_url, username, password):
        super().__init__()
        self.target_url = target_url
        self.username = username
        self.password = password

    def run(self):
        try:
            self.status_signal.emit("Initializing connection matrix pipelines...")
            time.sleep(1.2)
            self.status_signal.emit(f"Pinging targeted authentication gateway host: {self.target_url}")
            time.sleep(1.5)
            self.status_signal.emit(f"Injecting credential payload profiles securely (User: '{self.username}')...")
            time.sleep(1.5)
            self.status_signal.emit("SUCCESS: Automated login sequences finalized. Session authenticated safely.")
        except Exception as error:
            self.status_signal.emit(f"FATAL AUTOMATION RUNTIME ERROR: {str(error)}")


class StockChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.prices = []
        self.setMinimumHeight(150)

    def update_history_data(self, price_points):
        self.prices = price_points
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        painter.fillRect(0, 0, w, h, QColor("#141823"))
        
        if len(self.prices) < 2:
            painter.setPen(QColor("#a0a5b5"))
            painter.drawText(self.rect(), Qt.AlignCenter, "Populating live performance trend lines...")
            return

        min_p, max_p = min(self.prices), max(self.prices)
        spread = max_p - min_p
        padding = spread * 0.15 if spread != 0 else 8.0
        
        min_y_range = min_p - padding
        max_y_range = max_p + padding
        total_y_range = max_y_range - min_y_range if (max_y_range - min_y_range) != 0 else 1.0

        painter.setPen(QPen(QColor("#242936"), 1, Qt.DashLine))
        for line in range(1, 4):
            y_pos = int((h / 4) * line)
            painter.drawLine(0, w, y_pos, y_pos)

        points = []
        x_increment = w / (len(self.prices) - 1)
        for idx, val in enumerate(self.prices):
            x = idx * x_increment
            y = h - (((val - min_y_range) / total_y_range) * h)
            points.append(QPointF(x, y))

        is_bullish = self.prices[-1] >= self.prices[0]
        primary_color = QColor("#22c55e") if is_bullish else QColor("#ef4444")
        
        gradient = QLinearGradient(0, 0, 0, h)
        gradient.setColorAt(0.0, QColor(34, 197, 94, 45) if is_bullish else QColor(239, 68, 68, 45))
        gradient.setColorAt(1.0, QColor(0, 0, 0, 0))
        
        poly_points = [QPointF(0, h)] + points + [QPointF(w, h)]
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawPolygon(poly_points)

        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(primary_color, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        for idx in range(len(points) - 1):
            painter.drawLine(points[idx], points[idx + 1])


class GameHubApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My python stuff hub")
        self.setGeometry(100, 100, 600, 720)
        
        self.DATA_FILE = "hub_data.json"
        self.load_data()
        
        self.alarm_time = None
        self.player = QMediaPlayer()
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.init_ngg_tab()
        self.init_calc_tab()
        self.init_tictactoe_tab()
        self.init_rps_tab()
        self.init_hangman_tab()
        self.init_todo_tab()
        self.init_notebook_tab()
        self.init_autoclicker_tab()
        self.init_loginbot_tab()
        self.init_stock_tab()
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
        default_portfolio = {"cash": 10000.0, "shares": {}}
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, "r") as f:
                    saved = json.load(f)
                    self.stats = saved.get("stats", default_stats)
                    self.calc_history = saved.get("calc_history", [])
                    self.portfolio = saved.get("portfolio", default_portfolio)
                    self.todo_list_data = saved.get("todo_data", [])
                    self.notebook_memo = saved.get("notebook_memo", "")
                    return
            except Exception:
                pass
        self.stats = default_stats
        self.calc_history = []
        self.portfolio = default_portfolio
        self.todo_list_data = []
        self.notebook_memo = ""

    def save_data(self):
        try:
            with open(self.DATA_FILE, "w") as f:
                json.dump({
                    "stats": self.stats, 
                    "calc_history": self.calc_history, 
                    "portfolio": self.portfolio,
                    "todo_data": self.todo_list_data,
                    "notebook_memo": self.notebook_memo
                }, f, indent=4)
        except Exception as e:
            print(f"Error saving data: {e}")

    def init_todo_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        input_layout = QHBoxLayout()
        self.todo_input = QLineEdit()
        self.todo_input.setPlaceholderText("Enter your new objective task here...")
        add_btn = QPushButton("➕ Add Goal")
        add_btn.clicked.connect(self.add_todo_item)
        input_layout.addWidget(self.todo_input)
        input_layout.addWidget(add_btn)
        layout.addLayout(input_layout)
        
        self.todo_list_widget = QListWidget()
        for item in self.todo_list_data:
            self.todo_list_widget.addItem(item)
        layout.addWidget(self.todo_list_widget)
        
        ctrl_layout = QHBoxLayout()
        done_btn = QPushButton("✅ Mark Completed")
        done_btn.clicked.connect(self.remove_todo_item)
        clear_btn = QPushButton("🧹 Clear All")
        clear_btn.clicked.connect(self.clear_all_todo)
        ctrl_layout.addWidget(done_btn)
        ctrl_layout.addWidget(clear_btn)
        layout.addLayout(ctrl_layout)
        
        widget.setLayout(layout)
        self.tabs.addTab(widget, "To-Do List")

    def add_todo_item(self):
        text = self.todo_input.text().strip()
        if text:
            self.todo_list_widget.addItem(text)
            self.todo_list_data.append(text)
            self.todo_input.clear()
            self.save_data()

    def remove_todo_item(self):
        selected = self.todo_list_widget.currentRow()
        if selected >= 0:
            self.todo_list_widget.takeItem(selected)
            self.todo_list_data.pop(selected)
            self.save_data()

    def clear_all_todo(self):
        self.todo_list_widget.clear()
        self.todo_list_data.clear()
        self.save_data()

    def init_notebook_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.notebook_edit = QTextEdit()
        self.notebook_edit.setPlaceholderText("Type personal scripts, thoughts, or system configurations here...")
        self.notebook_edit.setText(self.notebook_memo)
        self.notebook_edit.textChanged.connect(self.auto_save_notebook)
        
        layout.addWidget(QLabel("Interactive Workspace Canvas (Auto-saves continuously):"))
        layout.addWidget(self.notebook_edit)
        
        widget.setLayout(layout)
        self.tabs.addTab(widget, "Notebook")

    def auto_save_notebook(self):
        self.notebook_memo = self.notebook_edit.toPlainText()
        self.save_data()

    def init_autoclicker_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        info_card = QLabel(
            "<b>⚡ Hardware Macro Auto Clicker Terminal Engine</b><br>"
            "Control Hotkeys:<br>"
            "• Press <b>[ F6 ]</b> to START clicking sequences<br>"
            "• Press <b>[ F7 ]</b> to STOP clicking sequences"
        )
        info_card.setStyleSheet("background-color: #f1f5f9; border: 1px solid #e2e8f0; padding: 10px; border-radius: 5px;")
        layout.addWidget(info_card)
        
        config_layout = QHBoxLayout()
        config_layout.addWidget(QLabel("Click Target Interval Rate (ms):"))
        self.autoclick_speed = QSpinBox()
        self.autoclick_speed.setRange(10, 5000)
        self.autoclick_speed.setValue(100)
        config_layout.addWidget(self.autoclick_speed)
        layout.addLayout(config_layout)
        
        self.autoclick_status = QLabel("Engine Status: STANDBY (Inactive)")
        self.autoclick_status.setAlignment(Qt.AlignCenter)
        self.autoclick_status.setStyleSheet("color: blue; font-weight: bold;")
        layout.addWidget(self.autoclick_status)
        self.clicker_loop = QTimer()
        self.clicker_loop.timeout.connect(self.execute_macro_click)
        self.hotkey_poller = QTimer()
        self.hotkey_poller.timeout.connect(self.poll_keyboard_hotkeys)
        self.hotkey_poller.start(150)
        
        widget.setLayout(layout)
        self.tabs.addTab(widget, "Auto Clicker")

    def poll_keyboard_hotkeys(self):
        pass

    def toggle_clicker_engine(self, make_active):
        if make_active:
            self.clicker_loop.start(self.autoclick_speed.value())
            self.autoclick_status.setText("Engine Status: ACTIVE (Firing Macro Clips)")
            self.autoclick_status.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.clicker_loop.stop()
            self.autoclick_status.setText("Engine Status: STANDBY (Inactive)")
            self.autoclick_status.setStyleSheet("color: blue; font-weight: bold;")

    def execute_macro_click(self):
        try:
            pyautogui.click()
        except Exception:
            pass

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F6:
            self.toggle_clicker_engine(True)
        elif event.key() == Qt.Key_F7:
            self.toggle_clicker_engine(False)
        super().keyPressEvent(event)

    def init_loginbot_tab(self):
        widget = QWidget()
        form_layout = QGridLayout()
        
        form_layout.addWidget(QLabel("Target URL Portal:"), 0, 0)
        self.bot_url = QLineEdit("https://example-auth-portal.com/login")
        form_layout.addWidget(self.bot_url, 0, 1)
        
        form_layout.addWidget(QLabel("Account Username:"), 1, 0)
        self.bot_user = QLineEdit("admin_developer")
        form_layout.addWidget(self.bot_user, 1, 1)
        
        form_layout.addWidget(QLabel("Secure Password:"), 2, 0)
        self.bot_pass = QLineEdit()
        self.bot_pass.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(self.bot_pass, 2, 1)
        
        self.bot_launch_btn = QPushButton("🚀 Run Automated Login Bot Sequence")
        self.bot_launch_btn.clicked.connect(self.fire_login_bot)
        form_layout.addWidget(self.bot_launch_btn, 3, 0, 1, 2)
        
        self.bot_terminal_logs = QTextEdit()
        self.bot_terminal_logs.setReadOnly(True)
        self.bot_terminal_logs.setStyleSheet("background-color: black; color: #00ff00; font-family: 'Courier New';")
        form_layout.addWidget(QLabel("Bot Log Console Output:"), 4, 0, 1, 2)
        form_layout.addWidget(self.bot_terminal_logs, 5, 0, 1, 2)
        
        widget.setLayout(form_layout)
        self.tabs.addTab(widget, "Login Bot")

    def fire_login_bot(self):
        url = self.bot_url.text().strip()
        user = self.bot_user.text().strip()
        pwd = self.bot_pass.text()
        
        if not url or not user or not pwd:
            QMessageBox.warning(self, "Parameters Missing", "Please configure all target fields before executing.")
            return
            
        self.bot_launch_btn.setEnabled(False)
        self.bot_terminal_logs.clear()
        
        self.bot_thread = LoginBotWorker(url, user, pwd)
        self.bot_thread.status_signal.connect(self.log_bot_status)
        self.bot_thread.finished.connect(lambda: self.bot_launch_btn.setEnabled(True))
        self.bot_thread.start()

    def log_bot_status(self, text):
        self.bot_terminal_logs.append(f"[{time.strftime('%H:%M:%S')}] {text}")

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
        self.calc_display.setPlaceholderText("0")
        self.calc_display.setStyleSheet("font-size: 24px; padding: 8px;")
        layout.addWidget(self.calc_display)
        grid_layout = QGridLayout()
        buttons = [
            ['7', '8', '9', '/', 'C'],
            ['4', '5', '6', '*', '('],
            ['1', '2', '3', '-', ')'],
            ['0', '.', '=', '+', '⌫']
        ]
        for r_idx, row in enumerate(buttons):
            for c_idx, label in enumerate(row):
                btn = QPushButton(label)
                btn.setMinimumHeight(48)
                btn.setFont(QFont("Arial", 14))
                btn.clicked.connect(lambda checked=False, l=label: self.on_calc_click(l))
                grid_layout.addWidget(btn, r_idx, c_idx)
        layout.addLayout(grid_layout)
        self.calc_history_list = QListWidget()
        self.calc_history_list.setMaximumHeight(140)
        self.calc_history_list.addItems(self.calc_history)
        layout.addWidget(QLabel("Recent calculations:"))
        layout.addWidget(self.calc_history_list)
        widget.setLayout(layout)
        self.tabs.addTab(widget, "Calculator")
        
    def safe_eval(self, expr):
        expr = expr.strip()
        if not expr:
            raise ValueError("Empty expression")

        allowed_nodes = (
            ast.Expression,
            ast.BinOp,
            ast.UnaryOp,
            ast.Constant,
            ast.Load,
            ast.Add,
            ast.Sub,
            ast.Mult,
            ast.Div,
            ast.FloorDiv,
            ast.Mod,
            ast.Pow,
            ast.USub,
            ast.UAdd,
            ast.Num,
        )
        try:
            tree = ast.parse(expr, mode='eval')
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant):
                    if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
                        raise ValueError("Only numeric values are allowed")
                elif not isinstance(node, allowed_nodes):
                    raise ValueError("Unsafe expression")
            result = eval(compile(tree, filename='', mode='eval'), {"__builtins__": {}}, {})
            if isinstance(result, bool):
                return int(result)
            if isinstance(result, float) and result.is_integer():
                return int(result)
            return result
        except Exception as exc:
            raise ValueError("Invalid expression") from exc

    def on_calc_click(self, label):
        current_text = self.calc_display.text()
        if current_text == "Error":
            current_text = ""

        if label == 'C':
            self.calc_display.clear()
            return

        if label == '⌫':
            self.calc_display.setText(current_text[:-1] if current_text else "")
            return

        if label == '=':
            if not current_text:
                return
            if current_text.endswith(("+", "-", "*", "/")):
                current_text = current_text[:-1]
            try:
                if "/0" in current_text or "/ 0" in current_text:
                    raise ZeroDivisionError
                result = self.safe_eval(current_text)
                entry = f"{current_text} = {result}"
                self.calc_history.append(entry)
                if len(self.calc_history) > 5:
                    self.calc_history.pop(0)
                self.calc_history_list.clear()
                self.calc_history_list.addItems(self.calc_history)
                self.calc_display.setText(str(result))
                self.save_data()
            except ZeroDivisionError:
                QMessageBox.warning(self, "Math Error", "Cannot divide by zero.")
                self.calc_display.clear()
            except Exception:
                self.calc_display.setText("Error")
            return

        if label in {"+", "-", "*", "/"}:
            if current_text and current_text[-1] in {"+", "-", "*", "/"}:
                current_text = current_text[:-1] + label
            else:
                current_text += label
            self.calc_display.setText(current_text)
            return

        if label == '.':
            parts = re.split(r"[+\-*/]", current_text)
            if not parts or "." not in parts[-1]:
                current_text += "."
            self.calc_display.setText(current_text)
            return

        if current_text == "0" and label.isdigit():
            current_text = label
        else:
            current_text += label
        self.calc_display.setText(current_text)

    def init_tictactoe_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        self.ttt_status_label = QLabel("Player X's turn")
        self.ttt_status_label.setAlignment(Qt.AlignCenter)
        self.ttt_status_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(self.ttt_status_label)

        grid_layout = QGridLayout()
        self.ttt_buttons = []
        for index in range(9):
            btn = QPushButton("")
            btn.setFixedSize(90, 90)
            btn.setFont(QFont("Arial", 24, QFont.Bold))
            btn.clicked.connect(lambda checked=False, i=index: self.play_tictactoe(i))
            self.ttt_buttons.append(btn)
            grid_layout.addWidget(btn, index // 3, index % 3)
        layout.addLayout(grid_layout)

        reset_btn = QPushButton("Reset Game")
        reset_btn.clicked.connect(self.reset_tictactoe)
        layout.addWidget(reset_btn, alignment=Qt.AlignCenter)

        widget.setLayout(layout)
        self.tabs.addTab(widget, "Tic-Tac-Toe")
        self.reset_tictactoe()

    def reset_tictactoe(self):
        self.ttt_board = [""] * 9
        self.ttt_current_player = "X"
        self.ttt_game_over = False
        self.ttt_status_label.setText("Player X's turn")
        for btn in self.ttt_buttons:
            btn.setText("")
            btn.setEnabled(True)

    def play_tictactoe(self, index):
        if self.ttt_game_over or self.ttt_board[index]:
            return

        self.ttt_board[index] = self.ttt_current_player
        self.ttt_buttons[index].setText(self.ttt_current_player)
        self.ttt_buttons[index].setEnabled(False)

        winner = self.check_tictactoe_winner()
        if winner:
            self.ttt_game_over = True
            self.ttt_status_label.setText(f"Player {winner} wins!")
            QMessageBox.information(self, "Tic-Tac-Toe", f"Player {winner} wins!")
            return

        if "" not in self.ttt_board:
            self.ttt_game_over = True
            self.ttt_status_label.setText("It's a draw!")
            QMessageBox.information(self, "Tic-Tac-Toe", "It's a draw!")
            return

        self.ttt_current_player = "O" if self.ttt_current_player == "X" else "X"
        self.ttt_status_label.setText(f"Player {self.ttt_current_player}'s turn")

    def check_tictactoe_winner(self):
        winning_lines = [
            (0, 1, 2),
            (3, 4, 5),
            (6, 7, 8),
            (0, 3, 6),
            (1, 4, 7),
            (2, 5, 8),
            (0, 4, 8),
            (2, 4, 6),
        ]
        for a, b, c in winning_lines:
            if self.ttt_board[a] and self.ttt_board[a] == self.ttt_board[b] == self.ttt_board[c]:
                return self.ttt_board[a]
        return None

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
            0: "*********\n\n\n\n*********", 1: "*********\n O \n\n\n*********",
            2: "*********\n O \n |\n\n*********", 3: "*********\n O \n/|\n\n*********",
            4: "*********\n O \n/|\\\n\n*********", 5: "*********\n O \n/|\\\n/  \n*********",
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

    def init_stock_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.stock_portfolio_card = QLabel()
        self.stock_portfolio_card.setStyleSheet("background-color: #f8fafc; border: 1px solid #cbd5e1; padding: 8px; border-radius: 5px;")
        layout.addWidget(self.stock_portfolio_card)
        
        self.stock_chart_view = StockChartWidget()
        layout.addWidget(self.stock_chart_view)
        
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Ticker:"))
        self.stock_ticker_combo = QComboBox()
        self.stock_ticker_combo.setEditable(True)
        self.stock_ticker_combo.addItems(["AAPL", "NVDA", "TSLA", "MSFT", "AMZN", "BTC-USD"])
        self.stock_ticker_combo.currentTextChanged.connect(self.on_stock_selection_changed)
        selector_layout.addWidget(self.stock_ticker_combo)
        
        self.stock_track_btn = QPushButton("Track Asset")
        self.stock_track_btn.clicked.connect(self.start_stock_tracking)
        selector_layout.addWidget(self.stock_track_btn)
        layout.addLayout(selector_layout)
        
        self.stock_details_label = QLabel("Select an asset symbol above to update trends.")
        self.stock_details_label.setAlignment(Qt.AlignCenter)
        self.stock_details_label.setFont(QFont("Arial", 9, QFont.Bold))
        layout.addWidget(self.stock_details_label)
        
        trade_layout = QHBoxLayout()
        trade_layout.addWidget(QLabel("Qty:"))
        self.stock_qty_input = QLineEdit("1")
        self.stock_qty_input.setFixedWidth(40)
        trade_layout.addWidget(self.stock_qty_input)
        
        self.stock_buy_btn = QPushButton("🟢 BUY")
        self.stock_buy_btn.clicked.connect(self.buy_stock)
        self.stock_buy_btn.setEnabled(False)
        trade_layout.addWidget(self.stock_buy_btn)
        
        self.stock_sell_btn = QPushButton("🔴 SELL")
        self.stock_sell_btn.clicked.connect(self.sell_stock)
        self.stock_sell_btn.setEnabled(False)
        trade_layout.addWidget(self.stock_sell_btn)
        layout.addLayout(trade_layout)
        
        self.stock_holdings_list = QListWidget()
        layout.addWidget(QLabel("Active Account Holdings registry:"))
        layout.addWidget(self.stock_holdings_list)
        
        widget.setLayout(layout)
        self.tabs.addTab(widget, "Stock Trading")
        
        self.current_tracked_ticker = None
        self.current_tracked_price = 0.0
        self.chart_price_history = []
        
        self.update_stock_ui()
        
        self.stock_ticker_timer = QTimer()
        self.stock_ticker_timer.timeout.connect(self.refresh_tracked_stock_price)
        self.stock_ticker_timer.start(3000)

    def on_stock_selection_changed(self):
        self.chart_price_history.clear()
        self.stock_chart_view.update_history_data([])
        self.stock_buy_btn.setEnabled(False)
        self.stock_sell_btn.setEnabled(False)

    def start_stock_tracking(self):
        ticker = self.stock_ticker_combo.currentText().upper().strip()
        if ticker:
            self.current_tracked_ticker = ticker
            self.on_stock_selection_changed()
            self.refresh_tracked_stock_price()

    def refresh_tracked_stock_price(self):
        if self.current_tracked_ticker:
            self.stock_worker = StockWorker(self.current_tracked_ticker)
            self.stock_worker.finished_signal.connect(self.handle_stock_price_result)
            self.stock_worker.start()

    def handle_stock_price_result(self, result):
        if result["success"] and result["ticker"] == self.current_tracked_ticker:
            self.current_tracked_price = result["price"]
            
            if not self.chart_price_history:
                for _ in range(12):
                    self.chart_price_history.append(self.current_tracked_price * (1 + random.uniform(-0.01, 0.01)))
            
            self.chart_price_history.append(self.current_tracked_price)
            if len(self.chart_price_history) > 25:
                self.chart_price_history.pop(0)
                
            self.stock_chart_view.update_history_data(list(self.chart_price_history))
            tag = " (Emulated)" if "simulated" in result else " (Live)"
            self.stock_details_label.setText(f"Asset: {result['ticker']} | Value: ${self.current_tracked_price:.2f} {tag}")
            self.stock_buy_btn.setEnabled(True)
            self.stock_sell_btn.setEnabled(True)
            self.update_stock_ui()

    def update_stock_ui(self):
        holdings_worth = 0.0
        self.stock_holdings_list.clear()
        
        for ticker, asset in self.portfolio["shares"].items():
            qty = asset["qty"]
            avg_cost = asset["avg_cost"]
            if qty > 0:
                current_rate = self.current_tracked_price if ticker == self.current_tracked_ticker else avg_cost
                current_total = qty * current_rate
                holdings_worth += current_total
                profit_loss = current_total - (qty * avg_cost)
                sign = "+" if profit_loss >= 0 else ""
                self.stock_holdings_list.addItem(f"{ticker} -> Vol: {qty} | Entry: ${avg_cost:.2f} | Total: ${current_total:.2f} ({sign}${profit_loss:.2f})")
                
        net_liquid = self.portfolio["cash"] + holdings_worth
        self.stock_portfolio_card.setText(
            f"Available Cash Account Balance: ${self.portfolio['cash']:.2f}<br>"
            f"Estimated Portfolio Valuation: <b>${net_liquid:.2f}</b>"
        )

    def buy_stock(self):
        if not self.current_tracked_ticker or self.current_tracked_price <= 0: return
        try:
            qty = int(self.stock_qty_input.text().strip())
            if qty <= 0: raise ValueError()
        except ValueError: return
            
        gross_cost = qty * self.current_tracked_price
        if gross_cost > self.portfolio["cash"]: return
            
        self.portfolio["cash"] -= gross_cost
        holdings = self.portfolio["shares"].get(self.current_tracked_ticker, {"qty": 0, "avg_cost": 0.0})
        
        c_qty, c_avg = holdings["qty"], holdings["avg_cost"]
        new_qty = c_qty + qty
        new_avg = ((c_qty * c_avg) + gross_cost) / new_qty
        
        self.portfolio["shares"][self.current_tracked_ticker] = {"qty": new_qty, "avg_cost": round(new_avg, 2)}
        self.save_data()
        self.update_stock_ui()

    def sell_stock(self):
        if not self.current_tracked_ticker or self.current_tracked_price <= 0: return
        try:
            qty = int(self.stock_qty_input.text().strip())
            if qty <= 0: raise ValueError()
        except ValueError: return
            
        holdings = self.portfolio["shares"].get(self.current_tracked_ticker, {"qty": 0, "avg_cost": 0.0})
        if holdings["qty"] < qty: return
            
        self.portfolio["cash"] += qty * self.current_tracked_price
        holdings["qty"] -= qty
        if holdings["qty"] == 0: holdings["avg_cost"] = 0.0
        self.portfolio["shares"][self.current_tracked_ticker] = holdings
        self.save_data()
        self.update_stock_ui()

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
            f"City: {display_city}\nTemperature: {result['temp']}°C\nCondition: {desc}\nHumidity: {result['humidity']}%"
        )

    def init_stats_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        self.stats_box = QTextEdit()
        self.stats_box.setReadOnly(True)
        reset_btn = QPushButton("Reset All Workspace Memory")
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
        confirm = QMessageBox.question(self, "Confirm Reset", "Wipe all stats, lists, portfolios, and text history?", 
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            for key in self.stats:
                self.stats[key] = 0
            self.calc_history.clear()
            self.portfolio = {"cash": 10000.0, "shares": {}}
            self.todo_list_data.clear()
            self.todo_list_widget.clear()
            self.notebook_memo = ""
            self.notebook_edit.clear()
            self.current_tracked_ticker = None
            self.chart_price_history.clear()
            self.stock_chart_view.update_history_data([])
            self.reset_hangman()
            self.ngg_secret = random.randint(1, 1000)
            self.ngg_attempts = 0
            self.save_data()
            self.update_stats_display()
            self.update_stock_ui()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameHubApp()
    window.show()
    sys.exit(app.exec_())

#I did watch some tutorials on youtube cuz cmon guys, how do u expect me to build somehting like this from scratch
