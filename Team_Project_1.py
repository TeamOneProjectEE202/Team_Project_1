# import must be written here
import random
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGridLayout, QPushButton, QLabel, QVBoxLayout, QWidget, QMessageBox, QHBoxLayout, QRadioButton
)
from PyQt5.QtCore import Qt, QProcess


BOARD_SIZE = 10

LETTERS_TO_NUM = {chr(65 + i): i for i in range(BOARD_SIZE)}

# Ship Class
class Ship:
    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.coordinates = []
        self.hits = 0

    def is_sunk(self):
        return self.hits == self.size
# Player Class

# AI Player Class
class AIPlayer(Player):
    def __init__(self, board):
        super().__init__(board)
        self.targets = []
        self.attacked_cells = set()

    def attack(self, player_board):
        row, col = self.get_new_attack_target(player_board)

        if player_board[row][col] == "X":
            player_board[row][col] = "H"
            self.add_surrounding_targets(row, col, player_board)
            print(f"AI hit at {row + 1}, {chr(65 + col)}!")
            return True
        else:
            player_board[row][col] = "O"
            print(f"AI miss at {row + 1}, {chr(65 + col)}.")
            return False

    def get_new_attack_target(self, player_board):
        while True:
            if self.targets:
                row, col = self.targets.pop(0)
            else:
                row, col = random.randint(0, BOARD_SIZE - 1), random.randint(0, BOARD_SIZE - 1)

            if (row, col) not in self.attacked_cells:
                self.attacked_cells.add((row, col))
                break
        return row, col

    def add_surrounding_targets(self, row, col, player_board):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                if player_board[nr][nc] not in ["H", "O"]:
                    self.targets.append((nr, nc))

# Human Player Class
class HumanPlayerShips(Player):
    def __init__(self, board):
        super().__init__(board)

# List of Ships
ship_list = [
    Ship("Aircraft Carrier", 5),
    Ship("Battleship", 4),
    Ship("Submarine", 3),
    Ship("Destroyer", 3),
    Ship("Patrol Boat", 2),
]

# Main Game Class
class BattleshipGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Battleship Game")
        self.setGeometry(100, 100, 800, 600)

        self.player_board = [[" "] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.ai_board = [[" "] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.player_hidden_board = [[" "] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.ai_hidden_board = [[" "] * BOARD_SIZE for _ in range(BOARD_SIZE)]

        self.player = HumanPlayerShips(self.player_board)
        self.ai = AIPlayer(self.ai_board)
        self.score = 0  # Initialize score
        self.elapsed_time = 0  # Initialize elapsed time
        self.ship_counter = 5  # Initialize ship counter (AI has 5 ships)


    def initUI(self):
        pass
#  StartWindow(QMainWindow) class
class StartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Welcome to Battleship!")
        self.setGeometry(100, 100, 800, 600)
        self.initUI()

    def initUI(self):
        # Main layout
        layout = QVBoxLayout()

        # Welcome message
        welcome_label = QLabel("Welcome to the Battleship Game!")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(welcome_label)

        # Instructions
        instructions_label = QLabel(
            "Prepare for a thrilling naval battle! \nPlace your ships and outwit the AI to win."
        )
        instructions_label.setAlignment(Qt.AlignCenter)
        instructions_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(instructions_label)

        # Start button
        start_button = QPushButton("Start Game")
        start_button.setStyleSheet("font-size: 18px; padding: 10px;")
        start_button.clicked.connect(self.start_game)  # Connect to the game start method
        layout.addWidget(start_button)

        # Instructions button
        instructions_button = QPushButton("Instructions")
        instructions_button.setStyleSheet("font-size: 18px; padding: 10px;")
        instructions_button.clicked.connect(self.show_instructions)  # Connect to the instructions method
        layout.addWidget(instructions_button)

        # Set central widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def start_game(self):
        self.close()  # Close the start window
        self.placement_window = PlacementWindow(self.game)
        self.placement_window.show()

    def show_instructions(self):
        # Show a dialog with game instructions
        instructions = (
            "Welcome to Battleship!\n\n"
            "Goal:\n"
            "Sink all the opponent's ships before they sink yours.\n\n"
            "Instructions:\n"
            "1. You can place your ships manually or randomly.\n"
            "2. During your turn, click on the AI's board to attack a cell.\n"
            "3. A hit will be marked in red (H), and a miss in blue (O).\n"
            "4. AI will then take its turn to attack your board.\n\n"
            "Win Condition:\n"
            "Destroy all enemy ships to win the game!\n"
            "Good luck!"
        )
        QMessageBox.information(self, "Instructions", instructions)


    def start_game(self):
        self.close()  # Close the start window
        self.placement_window = PlacementWindow(self.game)
        self.placement_window.show()



#   PlacementWindow class 




# Manual Placement Window
class ManualPlacementWindow(QMainWindow):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.setWindowTitle("Manual Placement")
        self.setGeometry(100, 100, 800, 600)

        self.current_ship_index = 0
        self.direction = 0
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.ship_label = QLabel(f"Place {ship_list[self.current_ship_index].name}")
        self.ship_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.ship_label)

        self.grid = QGridLayout()
        self.buttons = [[QPushButton("~") for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                self.buttons[i][j].setFixedSize(30, 30)
                self.buttons[i][j].clicked.connect(lambda _, r=i, c=j: self.place_ship(r, c))
                self.grid.addWidget(self.buttons[i][j], i, j)
        layout.addLayout(self.grid)

        direction_layout = QHBoxLayout()
        self.horizontal_button = QRadioButton("Horizontal")
        self.horizontal_button.setChecked(True)
        self.horizontal_button.toggled.connect(self.set_horizontal)
        direction_layout.addWidget(self.horizontal_button)

        self.vertical_button = QRadioButton("Vertical")
        self.vertical_button.toggled.connect(self.set_vertical)
        direction_layout.addWidget(self.vertical_button)
        layout.addLayout(direction_layout)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def set_horizontal(self):
        self.direction = 0

    def set_vertical(self):
        self.direction = 1

    def place_ship(self, row, col):
        ship = ship_list[self.current_ship_index]
        if self.game.player.is_space_available(row, col, ship.size, self.direction):
            self.game.player.place_ship(ship, row, col, self.direction)
            for r, c in ship.coordinates:
                self.buttons[r][c].setText("X")
                self.buttons[r][c].setStyleSheet("background-color: gray")
            self.current_ship_index += 1
            if self.current_ship_index < len(ship_list):
                self.ship_label.setText(f"Place {ship_list[self.current_ship_index].name}")
            else:
                self.close()
                self.battle_window = BattleWindow(self.game)
                self.battle_window.show()


# Battle Window
