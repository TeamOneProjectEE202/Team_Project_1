# import must be written here

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
