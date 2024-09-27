from app import db


class Match(db.Model):
    """This class represents a game of Tic-Tac-Toe, storing the game state and determining the winner."""
    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)
    board = db.Column(db.String(9), nullable=False, default=' ' * 9)
    current_turn = db.Column(db.String(1), nullable=False, default='X')
    winner = db.Column(db.String(1), nullable=True)

    def check_winner(self):
        winning_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
        for combo in winning_combinations:
            if self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]] != ' ':
                return self.board[combo[0]]
        return None
