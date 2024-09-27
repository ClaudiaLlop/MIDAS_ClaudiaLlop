import random
import logging
import json
from flask import Blueprint, request
from .match import db, Match

routes = Blueprint('routes', __name__)


def draw_board(board):
    """
    Creates friendly visualization of the board

    Args:
        board: List containing the elements of each position of the board

    Returns:
        string
    """
    board_lines = [board[i:i + 3] for i in range(0, len(board), 3)]
    return "\n".join(["|".join(row) for row in board_lines])


@routes.route('/create', methods=['POST'])
def create_match():
    """
    Endpoint for match initialization.

    Returns:
        dict containing the matchId created
    """
    match_id = random.randint(0, 100000)
    new_match = Match(id=match_id)

    logger = logging.getLogger(__name__)
    logger.info(f"Match created successfully with ID: {match_id}")

    db.session.add(new_match)
    db.session.commit()
    return json.dumps({'matchId': new_match.id}), 200


@routes.route('/move', methods=['POST'])
def make_move():
    """
    Endpoint for match movement.

    Returns:
        string
    """
    data = request.get_json()
    match_id = data.get('matchId')
    player = data.get('playerId')
    x = data['square']['x']
    y = data['square']['y']

    if not isinstance(x, int) or not isinstance(y, int) or  (x not in [1, 2, 3]) or (y not in [1, 2, 3]):
        return json.dumps({'error': "x and y coordinates must be integers from 1 to 3."}), 400

    # Calculate index on 3x3 board
    index = (x - 1) * 3 + (y - 1)

    # Check match existence
    match = Match.query.get(match_id)

    if not match:
        return json.dumps({'error': 'MatchId not found.'}), 404

    # Check if there is already a winner
    if match.winner:
        if match.winner == "draw":
            return json.dumps({'message': f'Match finished. It is a draw.'}), 400
        else:
            return json.dumps({'message': f'Match finished. Player {match.winner} is the winner.'}), 400

    # Validate movement
    if match.board[index] != ' ':
        return json.dumps({'error': 'The space is already occupied.'}), 400
    if match.current_turn != player:
        return json.dumps({'error': f'It is player {match.current_turn} turn.'}), 400

    # Register movement
    board_list = list(match.board)
    board_list[index] = player
    match.board = ''.join(board_list)

    # Check winner
    winner = match.check_winner()
    if winner:
        match.winner = winner

    # Change turn if there is no winner yet
    match.current_turn = 'O' if player == 'X' else 'X'

    db.session.commit()

    # Draw board and prepare response
    board_drawing = draw_board(match.board)
    response_message = "Movement successfully registered\n{}".format(board_drawing)

    if match.winner:
        response_message += f"\nPlayer {match.winner} is the winner!"

    if all(square != ' ' for square in match.board):
        response_message += "\nThe match is a draw!"

    return response_message, 200


@routes.route('/')
def home():
    return "Welcome to the Tic-Tac-Toe API!"

