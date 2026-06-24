import ast
import re
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QMessageBox,
)


class CalculatorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.history = []
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(self)

        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setPlaceholderText("0")
        self.display.setStyleSheet("font-size: 24px; padding: 8px;")
        layout.addWidget(self.display)

        buttons = [
            ["7", "8", "9", "/", "C"],
            ["4", "5", "6", "*", "("],
            ["1", "2", "3", "-", ")"],
            ["0", ".", "=", "+", "⌫"],
        ]

        grid = QGridLayout()
        for row, row_buttons in enumerate(buttons):
            for col, label in enumerate(row_buttons):
                button = QPushButton(label)
                button.setMinimumHeight(48)
                button.setFont(QFont("Arial", 14))
                button.clicked.connect(lambda checked=False, value=label: self.on_button_click(value))
                grid.addWidget(button, row, col)
        layout.addLayout(grid)

        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(140)
        layout.addWidget(QLabel("Recent calculations:"))
        layout.addWidget(self.history_list)

    def safe_eval(self, expression):
        expression = expression.strip()
        if not expression:
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
            tree = ast.parse(expression, mode="eval")
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant):
                    if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
                        raise ValueError("Only numeric values are allowed")
                elif not isinstance(node, allowed_nodes):
                    raise ValueError("Unsafe expression")

            result = eval(compile(tree, filename="", mode="eval"), {"__builtins__": {}}, {})
            if isinstance(result, bool):
                return int(result)
            if isinstance(result, float) and result.is_integer():
                return int(result)
            return result
        except Exception as exc:
            raise ValueError("Invalid expression") from exc

    def on_button_click(self, label):
        current_text = self.display.text()
        if current_text == "Error":
            current_text = ""

        if label == "C":
            self.display.clear()
            return

        if label == "⌫":
            self.display.setText(current_text[:-1] if current_text else "")
            return

        if label == "=":
            if not current_text:
                return
            if current_text.endswith(("+", "-", "*", "/")):
                current_text = current_text[:-1]
            try:
                result = self.safe_eval(current_text)
                entry = f"{current_text} = {result}"
                self.history.append(entry)
                if len(self.history) > 5:
                    self.history.pop(0)
                self.history_list.clear()
                self.history_list.addItems(self.history)
                self.display.setText(str(result))
            except Exception:
                self.display.setText("Error")
            return

        if label in {"+", "-", "*", "/"}:
            if current_text and current_text[-1] in {"+", "-", "*", "/"}:
                current_text = current_text[:-1] + label
            else:
                current_text += label
            self.display.setText(current_text)
            return

        if label == ".":
            parts = re.split(r"[+\-*/]", current_text)
            if not parts or "." not in parts[-1]:
                current_text += "."
            self.display.setText(current_text)
            return

        if current_text == "0" and label.isdigit():
            current_text = label
        else:
            current_text += label
        self.display.setText(current_text)


class TicTacToeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.buttons = []
        self.board = [""] * 9
        self.current_player = "X"
        self.game_over = False
        self.build_ui()
        self.reset_game()

    def build_ui(self):
        layout = QVBoxLayout(self)

        self.status_label = QLabel("Player X's turn")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(self.status_label)

        grid = QGridLayout()
        for index in range(9):
            button = QPushButton("")
            button.setFixedSize(90, 90)
            button.setFont(QFont("Arial", 24, QFont.Bold))
            button.clicked.connect(lambda checked=False, i=index: self.play_turn(i))
            self.buttons.append(button)
            grid.addWidget(button, index // 3, index % 3)
        layout.addLayout(grid)

        reset_button = QPushButton("Reset Game")
        reset_button.clicked.connect(self.reset_game)
        layout.addWidget(reset_button, alignment=Qt.AlignCenter)

    def reset_game(self):
        self.board = [""] * 9
        self.current_player = "X"
        self.game_over = False
        self.status_label.setText("Player X's turn")
        for button in self.buttons:
            button.setText("")
            button.setEnabled(True)

    def play_turn(self, index):
        if self.game_over or self.board[index]:
            return

        self.board[index] = self.current_player
        self.buttons[index].setText(self.current_player)
        self.buttons[index].setEnabled(False)

        winner = self.check_winner()
        if winner:
            self.game_over = True
            self.status_label.setText(f"Player {winner} wins!")
            QMessageBox.information(self, "Tic-Tac-Toe", f"Player {winner} wins!")
            return

        if "" not in self.board:
            self.game_over = True
            self.status_label.setText("It's a draw!")
            QMessageBox.information(self, "Tic-Tac-Toe", "It's a draw!")
            return

        self.current_player = "O" if self.current_player == "X" else "X"
        self.status_label.setText(f"Player {self.current_player}'s turn")

    def check_winner(self):
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
            if self.board[a] and self.board[a] == self.board[b] == self.board[c]:
                return self.board[a]
        return None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculator + Tic-Tac-Toe")
        self.setGeometry(100, 100, 640, 620)

        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        tabs.addTab(CalculatorWidget(), "Calculator")
        tabs.addTab(TicTacToeWidget(), "Tic-Tac-Toe")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
