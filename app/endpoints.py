import logging
import json
from flask import Blueprint, request
from .match import db, Match

routes = Blueprint('routes', __name__)


def check_data(data: dict):
    """
    Checks structure of data dict.

    Args:
        data (dict)

    Returns:
        error if the data is invalid
    """

    if not isinstance(data, dict):
        return json.dumps({'error': "Data must be a dict."}), 400

    required_keys = {"matchId", "playerId", "square"}
    if not required_keys.issubset(data.keys()):
        return json.dumps({'error': "Data dict must contain keys {matchId, playerId, square}"}), 400

    if not isinstance(data["square"], dict):
        return json.dumps({'error': "'square' key must be a dict."}), 400
    if not {"x", "y"} <= set(data["square"].keys()):
        return json.dumps({'error': "'square' dict must contain keys {x, y}"}), 400


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
    logger = logging.getLogger(__name__)

    try:
        max_match = db.session.query(db.func.max(Match.id)).scalar()

        if max_match is None:
            match_id = 0
        else:
            match_id = max_match + 1

        new_match = Match(id=match_id)

        logger.info(f"Creating match with ID: {match_id}")

        db.session.add(new_match)
        db.session.commit()

        logger.info(f"Match created successfully with ID: {match_id}")
        return json.dumps({'matchId': new_match.id}), 200

    except Exception as e:
        logger.error(f"Error creating match: {e}")
        return json.dumps({'error': 'Internal server error'}), 500


@routes.route('/move', methods=['POST'])
def make_move():
    """
    Endpoint for match movement.

    Returns:
        string
    """
    data = request.get_json()
    check_data(data)
    match_id = data.get('matchId')
    player = data.get('playerId')
    x = data['square']['x']
    y = data['square']['y']

    if player not in ("X", "O"):
        return json.dumps({'error': "Player must be 'X' or 'O'"}), 400

    if not isinstance(x, int) or not isinstance(y, int) or (x not in [1, 2, 3]) or (y not in [1, 2, 3]):
        return json.dumps({'error': "x and y coordinates must be integers from 1 to 3."}), 400

    # Calculate index on 3x3 board
    index = (x - 1) * 3 + (y - 1)

    # Check match existence
    match = Match.query.get(match_id)

    if not match:
        return json.dumps({'error': 'MatchId not found.'}), 404

    # Check if there is already a winner or draw
    if match.winner:
        return json.dumps({'message': f'Match finished. Player {match.winner} is the winner.'}), 400
    if all(char != ' ' for char in match.board) and not match.winner:
        return json.dumps({'message': f'Match finished. It is a draw.'}), 400

    # Validate movement
    if match.current_turn != player:
        return json.dumps({'error': f'It is player {match.current_turn} turn.'}), 400
    if match.board[index] != ' ':
        return json.dumps({'error': 'The space is already occupied.'}), 400

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


@routes.route('/status', methods=['GET'])
def get_status():
    match_id = request.args.get('matchId')
    match = Match.query.get(match_id)

    if not match:
        return json.dumps({'error': 'MatchId not found'}), 404

    board_drawing = draw_board(match.board)

    return json.dumps({
        'board': board_drawing,
        'current_turn': match.current_turn,
        'winner': match.winner
    }), 200


@routes.route('/')
def home():
    return "Welcome to the Tic-Tac-Toe API!"

