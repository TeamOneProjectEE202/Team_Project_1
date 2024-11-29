import random
import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGridLayout, QPushButton, QLabel, QVBoxLayout, QWidget, QMessageBox, QHBoxLayout, QRadioButton,
    QSlider, QDialog, QCheckBox)
from PyQt5.QtCore import Qt, QProcess, QTimer 
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtGui import QPixmap

BOARD_SIZE = 10

LETTERS_TO_NUM = {chr(65 + i): i for i in range(BOARD_SIZE)}

# Ship Class
class Ship:
    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.coordinates = [] 
        self.hits = 0  # The number of times the ship has been hit

    def is_sunk(self):
        return self.hits >= self.size  # Checks whether the ship is "sunk"
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
        ship.coordinates.clear()
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
        self.targets = []  # Target coordinates for the next attack
        self.attacked_cells = set()

    def attack(self, player_board):  # AI attack on the player board
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

    def get_new_attack_target(self, player_board): # Gets the next target for the AI
        while True:
            if self.targets:
                row, column = self.targets.pop(0)
            else:
                row, column = random.randint(0, BOARD_SIZE - 1), random.randint(0, BOARD_SIZE - 1)

            if (row, column) not in self.attacked_cells:
                self.attacked_cells.add((row, column))
                break
        return row, column

    def add_surrounding_targets(self, row, column, player_board):  # Adds the coordinates of the hits to the targets list
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for row_direction, column_direction in directions:
            new_row, new_column = row + row_direction, column + column_direction
            if 0 <= new_row < BOARD_SIZE and 0 <= new_column < BOARD_SIZE:
                if player_board[new_row][new_column] not in ["H", "O"]:
                    self.targets.append((new_row, new_column))

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
        self.player_score = 0
        self.ai_score = 0

        self.player_board = [[" "] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.ai_board = [[" "] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.player_hidden_board = [[" "] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.ai_hidden_board = [[" "] * BOARD_SIZE for _ in range(BOARD_SIZE)]

        self.player = Player(self.player_board)
        self.ai = AIPlayer(self.ai_board)
        self.score = 0  # Initialize score
        self.elapsed_time = 0  # Initialize elapsed time
        self.ship_counter = 5  # Initialize ship counter (AI has 5 ships)
        # Creating Datastores using le sqlite daetbaese:
        self.database = sqlite3.connect("BattleShipGame_1.db")
        self.cursor = self.database.cursor()
        self.create_tables()

    def create_tables(self):
        # Making the tables for our datastore][.
        self.cursor.execute('''
            create table if not exists game_state(
            id integer primary key autoincrement,
            player_board text,
            ai_board text,
            player_hidden_board text,
            ai_hidden_board text,
            score integer,
            elapsed_time integer,
            ship_counter integer, 
            ai_ships_state text
        )
    ''')
        self.database.commit()
    def save_game(self):
        player_board_str = "\n".join(["".join(row) for row in self.player_board])
        ai_board_str = "\n".join(["".join(row) for row in self.ai_board])
        player_hidden_board_str = "\n".join(["".join(row) for row in self.player_hidden_board])
        ai_hidden_board_str = "\n".join(["".join(row) for row in self.ai_hidden_board])

        # making a nice little dictionary for our ships
        ai_ships_state = [
            {
                "name" : ship.name,
                "size" : ship.size,
                "coordinates" : ship.coordinates,
                "hits" : ship.hits
            }
            for ship in self.ai.ships
        ]
        self.cursor.execute('''
            INSERT INTO game_state (player_board, ai_board, player_hidden_board, ai_hidden_board, score, elapsed_time, ship_counter, ai_ships_state)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            player_board_str,
            ai_board_str,
            player_hidden_board_str,
            ai_hidden_board_str,
            self.score,
            self.elapsed_time,
            self.ship_counter,
            str(ai_ships_state)  # Save AI ship state as a string
        ))
        self.database.commit()
        QMessageBox.information(self, "Game Saved", "Your game has been saved successfully!")

    def load_game(self):
        # Load the latest game state from the database
        self.cursor.execute('SELECT * FROM game_state ORDER BY id DESC LIMIT 1')
        row = self.cursor.fetchone()
        if row:
            player_board_str, ai_board_str, player_hidden_board_str, ai_hidden_board_str, self.score, self.elapsed_time, self.ship_counter, ai_ships_state_str = row[1:]

            self.player_board = [list(row) for row in player_board_str.split("\n")]
            self.ai_board = [list(row) for row in ai_board_str.split("\n")]
            self.player_hidden_board = [list(row) for row in player_hidden_board_str.split("\n")]
            self.ai_hidden_board = [list(row) for row in ai_hidden_board_str.split("\n")]

            # Restore AI ships state
            ai_ships_state = eval(ai_ships_state_str)  # Convert the string back to a list of dictionaries
            self.ai.ships = []
            for ship_data in ai_ships_state:
                ship = Ship(ship_data["name"], ship_data["size"])
                ship.coordinates = ship_data["coordinates"]
                ship.hits = ship_data["hits"]
                self.ai.ships.append(ship)

            QMessageBox.information(self, "Game Loaded", "Your game has been loaded successfully!")
        else:
            QMessageBox.warning(self, "No Save Found", "No saved game to load.")

    def closeEvent(self, event):
        # Close database connection when the app is closed
        self.database.close()
        super().closeEvent(event)

#  Start Window class
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
        self.placement_window = PlacementWindow(BattleshipGame())
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
        
        # Music Toggle
        self.music_toggle = QCheckBox("Enable Music")
        self.music_toggle.setStyleSheet("font-size: 18px; color: white; background-color: black;")
        self.music_toggle.setChecked(self.music.player.state() == QMediaPlayer.PlayingState)  # Check state
        layout.addWidget(self.music_toggle)

        # Save Button
        save_button = QPushButton("Save Settings")
        save_button.setStyleSheet("font-size: 18px; color: white; background-color: black;")
        save_button.clicked.connect(self.save_settings)  # Connect the correct method
        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_settings(self):
        # Save volume
        volume = self.volume_slider.value()
        self.music.set_volume(volume)

        # Enable/disable music
        if self.music_toggle.isChecked():
            if self.music.player.state() != QMediaPlayer.PlayingState:
                self.music.play()
        else:
            if self.music.player.state() == QMediaPlayer.PlayingState:
                self.music.pause()

        QMessageBox.information(self, "Settings Saved", "Your settings have been saved.")
        self.accept()  # Close the settings window
        
# Placement Window
class PlacementWindow(QMainWindow):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.setWindowTitle("Place Your Ships")
        self.setGeometry(100, 100, 800, 600)
    
        self.background_label = QLabel(self)
        pixmap = QPixmap("Main.jpg") 
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)
        self.background_label.setGeometry(0, 0, self.width(), self.height())

        self.initUI()
    def resizeEvent(self, event):
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    def initUI(self):
        layout = QVBoxLayout()

        # Title
        label = QLabel("Choose Ship Placement Method:")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        layout.addWidget(label)

        # Options
        self.manual_button = QPushButton("Manual Placement")
        self.manual_button.setStyleSheet("font-size: 18px; padding: 10px; color: white; background-color:black;")
        self.manual_button.clicked.connect(self.manual_placement)
        layout.addWidget(self.manual_button)

        self.random_button = QPushButton("Random Placement")
        self.random_button.setStyleSheet("font-size: 18px; padding: 10px; color: white; background-color:black;")
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
                column = random.randint(0, BOARD_SIZE - 1)
                direction = random.randint(0, 1)  # 0 = Horizontal, 1 = Vertical
                if self.game.player.is_space_available(row, column, ship.size, direction):
                    self.game.player.place_ship(ship, row, column, direction)
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

        self.background_label = QLabel(self)
        pixmap = QPixmap("Battle.jpg") 
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)
        self.background_label.setGeometry(0, 0, self.width(), self.height())

        self.initUI()

    def resizeEvent(self, event):
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

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
                self.buttons[i][j].clicked.connect(lambda _, row=i, column=j: self.place_ship(row, column))
                self.grid.addWidget(self.buttons[i][j], i, j)
        layout.addLayout(self.grid)

        direction_layout = QHBoxLayout()
        self.horizontal_button = QRadioButton("Horizontal")
        self.horizontal_button.setChecked(True)
        self.horizontal_button.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        self.horizontal_button.toggled.connect(self.set_horizontal)
        direction_layout.addWidget(self.horizontal_button)

        self.vertical_button = QRadioButton("Vertical")
        self.vertical_button.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
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

    def place_ship(self, row, column):
        ship = ship_list[self.current_ship_index]
        if self.game.player.is_space_available(row, column, ship.size, self.direction):
            self.game.player.place_ship(ship, row, column, self.direction)
            for row, column in ship.coordinates:
                self.buttons[row][column].setText("X")
                self.buttons[row][column].setStyleSheet("background-color: green")
            self.current_ship_index += 1
            if self.current_ship_index < len(ship_list):
                self.ship_label.setText(f"Place {ship_list[self.current_ship_index].name}")
                self.ship_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
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
        self.background_label = QLabel(self)
        
        pixmap = QPixmap("Battle2.png")
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)
        self.background_label.setGeometry(0, 0, self.width() , self.height())

        self.initUI()

    def reszieEvent(self,event):
        self.background_label.setGeometry(0,0,self.width(),self.height())
        super().resizeEvent(event)

    def initUI(self):
        main_layout = QVBoxLayout()

        # Timer Label #A
        timer_layout = QVBoxLayout()
        self.timer_label = QLabel("Time: 0s")
        self.timer_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        timer_layout.addWidget(self.timer_label)
        main_layout.addLayout(timer_layout)


        # Ship Counter Label #A
        self.counter_label = QLabel(f"Remaining AI Ships: {self.game.ship_counter}")
        self.counter_label.setAlignment(Qt.AlignCenter)
        self.counter_label.setStyleSheet("font-size: 18px; color: red; font-weight: bold;") #A
        main_layout.addWidget(self.counter_label)

        # player Score Label #A
        player_score_layout = QVBoxLayout()
        player_score_label_title = QLabel("Player Score")
        player_score_label_title.setStyleSheet("color: green; font-size: 18px; font-weight: bold;")
        player_score_layout.addWidget(player_score_label_title)

        self.player_score_label = QLabel("0")
        self.player_score_label.setStyleSheet("color: green; font-size: 16px;")
        player_score_layout.addWidget(self.player_score_label)
        main_layout.addLayout(player_score_layout)
        # Ai score A
        ai_score_layout = QVBoxLayout()
        ai_score_label_title = QLabel("AI Score")
        ai_score_label_title.setStyleSheet("color: red; font-size: 18px; font-weight: bold;")
        ai_score_layout.addWidget(ai_score_label_title)

        self.ai_score_label = QLabel("0")
        self.ai_score_label.setStyleSheet("color: red; font-size: 16px;")
        ai_score_layout.addWidget(self.ai_score_label)

        main_layout.addLayout(ai_score_layout)
        # AI HEALTH A
        ai_health_layout = QVBoxLayout()
        ai_health_label_title = QLabel("AI Ships Health")
        ai_health_label_title.setStyleSheet("color: red; font-size: 18px; font-weight: bold;")
        ai_health_layout.addWidget(ai_health_label_title)

        self.ai_health_label = QLabel("\n".join([f"{ship.name}: {ship.size}" for ship in ship_list]))
        self.ai_health_label.setStyleSheet("color: red; font-size: 16px;")
        ai_health_layout.addWidget(self.ai_health_label)

        main_layout.addLayout(ai_health_layout)

        # Score Label  A
        self.score_label = QLabel(f"Score: {self.game.score}")
        self.score_label.setAlignment(Qt.AlignCenter)
        self.score_label.setStyleSheet("font-size: 15px; font-weight: bold; color: white;")
        main_layout.addWidget(self.score_label)
        
        # Save and Load Buttons
        save_load_layout = QHBoxLayout()
        save_button = QPushButton("Save Game")
        save_button.setStyleSheet("font-size: 18px; padding: 10px; color: white; background-color:black;")
        save_button.clicked.connect(self.save_game)
        save_load_layout.addWidget(save_button)

        load_button = QPushButton("Quick Load")
        load_button.setStyleSheet("font-size: 18px; padding: 10px; color: white; background-color:black;")
        load_button.clicked.connect(self.load_game)
        save_load_layout.addWidget(load_button)

        main_layout.addLayout(save_load_layout)

        # Player and AI Board
        player_label = QLabel("Your Board:")
        player_label.setStyleSheet("font-size: 15px; font-weight: bold; color: white;")
        self.player_grid = QGridLayout()
        self.player_buttons = [[QPushButton("~") for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                self.player_buttons[i][j].setFixedSize(30, 30)
                self.player_grid.addWidget(self.player_buttons[i][j], i, j)
        main_layout.addWidget(player_label)
        main_layout.addLayout(self.player_grid)

        ai_label = QLabel("Enemy Board :")
        ai_label.setStyleSheet("font-size: 15px; font-weight: bold; color: white;")
        self.ai_grid = QGridLayout()
        self.ai_buttons = [[QPushButton("~") for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                self.ai_buttons[i][j].setFixedSize(30, 30)
                self.ai_buttons[i][j].clicked.connect(lambda _, row=i, column=j: self.player_attack(row, column))
                self.ai_grid.addWidget(self.ai_buttons[i][j], i, j)
        main_layout.addWidget(ai_label)
        main_layout.addLayout(self.ai_grid)

        restart_button = QPushButton("Back to Menu")
        restart_button.setStyleSheet("font-size: 18px; padding: 10px; color: white; background-color:black;")
        restart_button.clicked.connect(self.restart_game)
        main_layout.addWidget(restart_button)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.start_game()

    def update_timer(self):
        self.game.elapsed_time += 1
        self.timer_label.setText(f"Time: {self.game.elapsed_time}s")
        self.timer_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")

    def restart_game(self):
        QMessageBox.information(self, "Ending Game...", "The game will end and you will be sent to the Main Menu.")
        QApplication.quit()
        QProcess.startDetached(sys.executable, sys.argv)

    def update_ship_status(self): # update resualt #A
        ai_status = "\n".join([
            f"{ship.name}: {max(ship.size - ship.hits, 0)}" 
            for ship in self.game.ai.ships 
        ])
        self.ai_health_label.setText(f"AI Ships:\n{ai_status}")  # Update AI ship health only based on player's attacks
   
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
        self.update_ship_status()
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.game.player_board[row][col] == "X":
                    self.player_buttons[row][col].setText("X")
                    self.player_buttons[row][col].setStyleSheet("background-color: green")
                    
                      
    def save_game(self):
        self.game.save_game()
        self.update_ship_status() #A

    def load_game(self):
        self.game.load_game()
        self.update_boards()
        self.update_ship_status() #A

    def update_boards(self):
        # Update the player board UI
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                cell = self.game.player_board[row][col]
                button = self.player_buttons[row][col]
                if cell == "X":
                    button.setText("X")
                    button.setStyleSheet("background-color: green")
                elif cell == "H":
                    button.setText("H")
                    button.setStyleSheet("background-color: red")
                elif cell == "O":
                    button.setText("O")
                    button.setStyleSheet("background-color: blue")
                else:
                    button.setText("~")
                    button.setStyleSheet("background-color: none")
        # Add Update the AI board UI here 

    def player_attack(self, row, col):
        if self.game.ai_hidden_board[row][col] in ["H", "O"]:
            QMessageBox.information(self, "Invalid Move", "You already attacked this spot!")
            return

        if self.game.ai_board[row][col] == "X":
            self.game.ai_hidden_board[row][col] = "H"
            self.game.ai_board[row][col] = "H"
            self.ai_buttons[row][col].setText("H")
            self.ai_buttons[row][col].setStyleSheet("background-color: red")
            self.game.player_score += 10
            QMessageBox.information(self, "Hit", "You hit an AI ship!")

            for ship in self.game.ai.ships:
                if (row, col) in ship.coordinates:
                    ship.hits += 1
                    if ship.is_sunk() and not hasattr(ship, 'sunk_announced'):  # Check if the ship is fully sunk
                        ship.sunk_announced = True
                        self.game.player_score += 50
                        self.game.ship_counter -= 1
                        self.counter_label.setText(f"Remaining AI Ships: {self.game.ship_counter}")
                        QMessageBox.information(self, "Ship Sunk", f"You sunk the AI's {ship.name}!")
                    break

        else:
            self.game.ai_hidden_board[row][col] = "O"
            self.game.ai_board[row][col] = "O"
            self.ai_buttons[row][col].setText("O")
            self.ai_buttons[row][col].setStyleSheet("background-color: blue")
            self.game.player_score -= 1
       
        self.update_score()

        if all(cell != "X" for row in self.game.ai_board for cell in row):
            QMessageBox.information(self, "Victory", "You sank all AI ships!")
            sys.exit()

        self.ai_turn()


    def ai_turn(self):
        hit = self.game.ai.attack(self.game.player_board)
        if hit:  # A
            self.game.ai_score += 10
            print("AI scored a hit!")
            for ship in self.game.player.ships:
                if any((row, col) in ship.coordinates for row, col in self.game.ai.attacked_cells):  # تحقق إذا كانت الخلية جزءًا من السفينة
                    ship.hits += 1
                    if ship.is_sunk() and not hasattr(ship, 'sunk_announced'):  # إذا تم غرق السفينة
                        ship.sunk_announced = True
                        self.game.ai_score += 50
                        QMessageBox.information(self, "AI Sunk a Ship", f"The AI sunk your {ship.name}!")
                    break
        else:
            self.game.ai_score -= 1
            print("AI missed!")
        self.update_ship_status()
        self.update_score()

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
def update_score(self): #A
        self.player_score_label.setText(f"{self.game.player_score}")
        self.player_score_label.setStyleSheet("color: black; font-size: 16px; font-weight: bold;")

        self.ai_score_label.setText(f"{self.game.ai_score}")
        self.ai_score_label.setStyleSheet("color: red; font-size: 16px; font-weight: bold;")

def main():
    app = QApplication(sys.argv)
    game = BattleshipGame()
    start_window = StartWindow()
    start_window.game = game
    start_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    




