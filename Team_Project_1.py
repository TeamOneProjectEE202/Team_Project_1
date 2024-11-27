import random
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGridLayout, QPushButton, QLabel, QVBoxLayout, QWidget, QMessageBox, QHBoxLayout, QRadioButton
    QSlider, QDialog, QCheckBox)
from PyQt5.QtCore import Qt, QProcess, QTimer 
from PyQt5.QtMultimedia import QMediaPlayer


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
class Player:
    def __init__(self, board):
        self.board = board
        self.ships = []
        
    def all_ships_sunk(self):
        return all(ship.is_sunk() for ship in self.ships)
        
    def is_space_available(self, row, column, size, direction):
        if direction == 0:
            if column + size > BOARD_SIZE:
                return False
            for i in range(size):
                if self.board[row][column + i] != " ":
                    return False
        else:
            if row + size > BOARD_SIZE:
                return False
            for i in range(size):
                if self.board[row + i][column] != " ":
                    return False
            return True
            
    def place_ship(self, ship, row, column, direction):
        if direction == 0:
            for i in range(ship.size):
                self.board[row][column + i] = "X"
                ship.coordinates.append((row, column + i))
        else:
            for i in range(ship.size):
                self.board[row + i][column] = "X"
                ship.coordinates.append((row + i, column))
        self.ships.append(ship)

# AI Player Class
class AIPlayer(Player):
    def __init__(self, board):
        super().__init__(board)
        self.targets = []
        self.attacked_cells = set()

    def attack(self, player_board):
        row, column = self.get_new_attack_target(player_board)

        if player_board[row][column] == "X":
            player_board[row][column] = "H"
            self.add_surrounding_targets(row, column, player_board)
            print(f"AI hit at {row + 1}, {chr(65 + column)}!")
            return True
        else:
            player_board[row][column] = "O"
            print(f"AI miss at {row + 1}, {chr(65 + column)}.")
            return False

    def get_new_attack_target(self, player_board):
        while True:
            if self.targets:
                row, column = self.targets.pop(0)
            else:
                row, column = random.randint(0, BOARD_SIZE - 1), random.randint(0, BOARD_SIZE - 1)

            if (row, column) not in self.attacked_cells:
                self.attacked_cells.add((row, column))
                break
        return row, column

    def add_surrounding_targets(self, row, column, player_board):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for row_direction, column_direction in directions:
            new_row, new_column = row + row_direction, column + column_direction
            if 0 <= new_row < BOARD_SIZE and 0 <= new_column < BOARD_SIZE:
                if player_board[new_row][new_column] not in ["H", "O"]:
                    self.targets.append((new_row, new_column))

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
    def __init__(self, music):
        super().__init__()
        self.setWindowTitle("Welcome to Battleship!")
        self.setGeometry(100, 100, 800, 600)

        self.background_label = QLabel(self)
        pixmap = QPixmap("c:/Users/welcome/OneDrive/سطح المكتب/Fall-2024/EE 202 LAB/Menu.jpeg") 
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        
        self.initUI()
        
    def resizeEvent(self, event):
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    def initUI(self):
        # Main layout
        layout = QVBoxLayout()

        # Welcome message
        welcome_label = QLabel("Welcome to the Battleship Game!")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        layout.addWidget(welcome_label)

        # Instructions
        instructions_label = QLabel(
            "Prepare for a thrilling naval battle! \nPlace your ships and outwit the AI to win."
        )
        instructions_label.setAlignment(Qt.AlignCenter)
        instructions_label.setStyleSheet("font-size: 16px; color: white;")
        layout.addWidget(instructions_label)

        # Start button
        start_button = QPushButton("New Game")
        start_button.setStyleSheet("font-size: 18px; padding: 10px; color: white; background-color: black;")
        start_button.clicked.connect(self.start_game)  # Connect to the game start method
        layout.addWidget(start_button)

        # Instructions button
        instructions_button = QPushButton("Instructions")
        instructions_button.setStyleSheet("font-size: 18px; padding: 10px; color: white; background-color: black;")
        instructions_button.clicked.connect(self.show_instructions)  # Connect to the instructions method
        layout.addWidget(instructions_button)

        # Load game button
        load_button = QPushButton("Load Game")
        load_button.setStyleSheet("font-size: 18px; padding: 10px; color: white; background-color:black;")
        load_button.clicked.connect(self.load_game)  # Connect to load game method
        layout.addWidget(load_button)

        # Set central widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Settings button
        settings_button = QPushButton("Settings")
        settings_button.setStyleSheet("font-size: 18px; color: white; background-color: black;")
        settings_button.clicked.connect(self.open_settings)
        layout.addWidget(settings_button)

    def open_settings(self):
        # Open the Settings window and pass the music object
        self.settings_window = SettingsWindow(self.music)  # Pass the music object
        self.settings_window.exec_()

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


    def load_game(self):
        # Load the latest game state
        self.game = BattleshipGame()
        self.game.load_game()
        self.close()
        self.battle_window = BattleWindow(self.game)
        self.battle_window.update_boards()  # Update boards in BattleWindow
        self.battle_window.show() 

class SettingsWindow(QDialog):
    def __init__(self, music):
        super().__init__()
        self.music = music  # Store the music object
        self.setWindowTitle("Settings")
        self.setGeometry(200, 200, 400, 300)
        
        layout = QVBoxLayout()
    
        # Volume Slider
        volume_label = QLabel("Volume:")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.music.player.volume())  # Set initial value based on current volume
        layout.addWidget(volume_label)
        layout.addWidget(self.volume_slider)
        
#   PlacementWindow class
class PlacementWindow(QMainWindow):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.setWindowTitle("Place your Ships: ")
        self.setGeometry(100, 100, 800, 600)
        self.initUI()
    def initUI(self):
        layout = QVBoxLayout()
        
        label = QLabel("Choose your Ship Placement Method: ")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        self.manual_button = QPushButton("Manual Placement")
        self.manual_button.clicked.connect(self.manual_placement)
        layout.addWidget(self.manual_button)
        
        self.random_button = QPushButton("Random Placement")
        self.random_button.clicked.connect(self.random_placement)
        layout.addWidget(self.random_button)
        
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
    
    def manual_placement(self):
        self.close()
        self.manual_window = ManualPlacementWindow(self.game)
        self.manual_window.show()
    def random_placement(self):
        for ship in ship_list:
            placed = False
            while not placed:
                row = random.randint(0, BOARD_SIZE - 1)
                col = random.randint(0, BOARD_SIZE - 1)
                direction = random.randint(0, 1)
                if self.game.player.is_space_available(row, col, ship.size, direction):
                    self.game.player.place_ship(ship, row, col, direction)
                    placed = True
        self.close()
        self.battle_window = BattleWindow(self.game)
        self.battle_window.show()

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
class BattleWindow(QMainWindow):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.setWindowTitle("Battle - Player vs AI")
        self.setGeometry(100, 100, 800, 600)
        self.timer = QTimer(self)  # Create a QTimer instance
        self.timer.timeout.connect(self.update_timer)  # Connect timer to update function
        self.timer.start(1000)  # Update every 1 second
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        # Timer Label
        self.timer_label = QLabel("Time: 0s")
        self.timer_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.timer_label)

        # Ship Counter Label
        self.counter_label = QLabel(f"Remaining AI Ships: {self.game.ship_counter}")
        self.counter_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.counter_label)

        # Score Label
        self.score_label = QLabel(f"Score: {self.game.score}")
        self.score_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.score_label)

        # Player and AI Board
        player_label = QLabel("Your Board:")
        self.player_grid = QGridLayout()
        self.player_buttons = [[QPushButton("~") for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                self.player_buttons[i][j].setFixedSize(30, 30)
                self.player_grid.addWidget(self.player_buttons[i][j], i, j)
        main_layout.addWidget(player_label)
        main_layout.addLayout(self.player_grid)

        ai_label = QLabel("AI Board (Hidden):")
        self.ai_grid = QGridLayout()
        self.ai_buttons = [[QPushButton("~") for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                self.ai_buttons[i][j].setFixedSize(30, 30)
                self.ai_buttons[i][j].clicked.connect(lambda _, r=i, c=j: self.player_attack(r, c))
                self.ai_grid.addWidget(self.ai_buttons[i][j], i, j)
        main_layout.addWidget(ai_label)
        main_layout.addLayout(self.ai_grid)

        restart_button = QPushButton("Restart Game")
        restart_button.clicked.connect(self.restart_game)
        main_layout.addWidget(restart_button)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.start_game()

    def update_timer(self):
        self.game.elapsed_time += 1
        self.timer_label.setText(f"Time: {self.game.elapsed_time}s")

    def restart_game(self):
        QMessageBox.information(self, "Restarting", "The game will restart.")
        QApplication.quit()
        QProcess.startDetached(sys.executable, sys.argv)


    def start_game(self):
        for ship in ship_list:
            placed = False
            while not placed:
                row = random.randint(0, BOARD_SIZE - 1)
                col = random.randint(0, BOARD_SIZE - 1)
                direction = random.randint(0, 1)
                if self.game.ai.is_space_available(row, col, ship.size, direction):
                    self.game.ai.place_ship(ship, row, col, direction)
                    placed = True
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.game.player_board[row][col] == "X":
                    self.player_buttons[row][col].setText("X")
                    self.player_buttons[row][col].setStyleSheet("background-color: gray")

    def player_attack(self, row, col):
        if self.game.ai_hidden_board[row][col] in ["H", "O"]:
            QMessageBox.information(self, "Invalid Move", "You already attacked this spot!")
            return

        if self.game.ai_board[row][col] == "X":
            self.game.ai_hidden_board[row][col] = "H"
            self.game.ai_board[row][col] = "H"
            self.ai_buttons[row][col].setText("H")
            self.ai_buttons[row][col].setStyleSheet("background-color: red")
            self.game.score += 10
            QMessageBox.information(self, "Hit", "You hit an AI ship!")

            for ship in self.game.ai.ships:
                if (row, col) in ship.coordinates:
                    ship.hits += 1
                    if ship.is_sunk():
                        self.game.score += 50
                        self.game.ship_counter -= 1
                        self.counter_label.setText(f"Remaining AI Ships: {self.game.ship_counter}")
                        QMessageBox.information(self, "Ship Sunk", f"You sunk the AI's {ship.name}!")

        else:
            self.game.ai_hidden_board[row][col] = "O"
            self.game.ai_board[row][col] = "O"
            self.ai_buttons[row][col].setText("O")
            self.ai_buttons[row][col].setStyleSheet("background-color: blue")
            self.game.score -= 1

        self.score_label.setText(f"Score: {self.game.score}")

        if all(cell != "X" for row in self.game.ai_board for cell in row):
            QMessageBox.information(self, "Victory", "You sank all AI ships!")
            sys.exit()

        self.ai_turn()


    def ai_turn(self):
        hit = self.game.ai.attack(self.game.player_board)

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.game.player_board[row][col] == "H":
                    self.player_buttons[row][col].setText("H")
                    self.player_buttons[row][col].setStyleSheet("background-color: red")
                elif self.game.player_board[row][col] == "O":
                    self.player_buttons[row][col].setText("O")
                    self.player_buttons[row][col].setStyleSheet("background-color: blue")

        if all(cell != "X" for row in self.game.player_board for cell in row):
            QMessageBox.information(self, "Defeat", "AI sank all your ships!")
            sys.exit()

def main():
    app = QApplication(sys.argv)
    game = BattleshipGame()
    start_window = StartWindow()
    start_window.game = game
    start_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    




