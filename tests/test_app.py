import unittest
import json
from app import create_app, db


class TestMatchEndpoints(unittest.TestCase):

    def setUp(self):
        """Set up test client and database for each test."""
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Drop the database after each test."""
        with self.app.app_context():
            db.drop_all()

    def test_create_match(self):
        """Test the /create endpoint."""
        response = self.client.post('/create')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('matchId', data)
        self.assertIsInstance(data['matchId'], int)

    def test_status_endpoint(self):
        """Test the /status endpoint."""
        response = self.client.post('/create')
        match_id = json.loads(response.data)['matchId']

        response = self.client.get(f'/status?matchId={match_id}')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('board', data)
        self.assertIn('current_turn', data)
        self.assertEqual(data['current_turn'], 'X')
        self.assertIsNone(data['winner'])

    def test_make_move(self):
        """Test the /move endpoint with valid data."""
        # Create a match
        response = self.client.post('/create')
        match_id = json.loads(response.data)['matchId']

        # Player X makes a valid move
        response = self.client.post('/move', json={
            'matchId': match_id,
            'playerId': 'X',
            'square': {'x': 1, 'y': 1}
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Movement successfully registered', response.data.decode())

    def test_make_move_invalid_coordinates(self):
        """Test the /move endpoint with invalid coordinates."""
        response = self.client.post('/create')
        match_id = json.loads(response.data)['matchId']

        # Player X tries to make a move with invalid coordinates
        response = self.client.post('/move', json={
            'matchId': match_id,
            'playerId': 'X',
            'square': {'x': 4, 'y': 1}
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('x and y coordinates must be integers from 1 to 3.', response.data.decode())

    def test_make_move_to_occupied_space(self):
        """Test moving to an already occupied space."""
        response = self.client.post('/create')
        match_id = json.loads(response.data)['matchId']

        # Player X makes a move
        self.client.post('/move', json={
            'matchId': match_id,
            'playerId': 'X',
            'square': {'x': 1, 'y': 1}
        })

        # Player O tries to make a move in the same space
        response = self.client.post('/move', json={
            'matchId': match_id,
            'playerId': 'O',
            'square': {'x': 1, 'y': 1}
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('The space is already occupied.', response.data.decode())

    def test_make_move_with_wrong_turn(self):
        """Test moving when it's not the player's turn."""
        response = self.client.post('/create')
        match_id = json.loads(response.data)['matchId']

        # Player X makes a move
        self.client.post('/move', json={
            'matchId': match_id,
            'playerId': 'X',
            'square': {'x': 1, 'y': 1}
        })

        # Player X tries to move again
        response = self.client.post('/move', json={
            'matchId': match_id,
            'playerId': 'X',
            'square': {'x': 2, 'y': 1}
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('It is player O turn.', response.data.decode())

    def test_draw(self):
        """Test a draw situation in the match."""
        response = self.client.post('/create')
        match_id = json.loads(response.data)['matchId']

        # Fill the board without winner
        moves = [
            ('X', 1, 1), ('O', 1, 2), ('X', 2, 2), ('O', 1, 3),
            ('X', 2, 3), ('O', 2, 1), ('X', 3, 1), ('O', 3, 3), ('X', 3, 2)
        ]

        for player, x, y in moves:
            self.client.post('/move', json={
                'matchId': match_id,
                'playerId': player,
                'square': {'x': x, 'y': y}
            })

        # Verify draw
        response = self.client.post('/move', json={
            'matchId': match_id,
            'playerId': 'X',
            'square': {'x': 1, 'y': 1}
        })

        self.assertIn('Match finished. It is a draw.', response.data.decode())

    def test_create_multiple_matches(self):
        """Test creating multiple matches to ensure matchId increments correctly."""
        response1 = self.client.post('/create')
        match_id_1 = json.loads(response1.data)['matchId']

        response2 = self.client.post('/create')
        match_id_2 = json.loads(response2.data)['matchId']

        self.assertGreater(match_id_2, match_id_1)

    def test_move_after_winner(self):
        """Test no further moves are allowed after the game is won."""
        response = self.client.post('/create')
        match_id = json.loads(response.data)['matchId']

        # X is the winner
        moves = [
            ('X', 1, 1), ('O', 1, 2),
            ('X', 2, 1), ('O', 1, 3),
            ('X', 3, 1)
        ]

        for player, x, y in moves:
            self.client.post('/move', json={
                'matchId': match_id,
                'playerId': player,
                'square': {'x': x, 'y': y}
            })

        # Try to move after X winning
        response = self.client.post('/move', json={
            'matchId': match_id,
            'playerId': 'O',
            'square': {'x': 2, 'y': 2}
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn('Player X is the winner', response.data.decode())

    def test_move_with_invalid_match_id(self):
        """Test making a move with a non-existent matchId."""
        response = self.client.post('/move', json={
            'matchId': 9999,
            'playerId': 'X',
            'square': {'x': 1, 'y': 1}
        })

        self.assertEqual(response.status_code, 404)
        self.assertIn('MatchId not found.', response.data.decode())


if __name__ == '__main__':
    unittest.main()
