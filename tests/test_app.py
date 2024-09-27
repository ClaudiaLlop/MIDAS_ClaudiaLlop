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


if __name__ == '__main__':
    unittest.main()
