# import must be written here

# Ship Class

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
