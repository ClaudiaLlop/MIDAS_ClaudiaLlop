# Tic-Tac-Toe API

## Author
**Claudia Llop Moreno**

## Project Overview
This project is a RESTful API for a Tic-Tac-Toe game, built using Flask and SQLAlchemy. The API allows users to create matches and make moves in the game, handling game state and determining winners.

## Technologies Used
- **Flask**: A lightweight web framework for Python.
- **SQLAlchemy**: An ORM (Object Relational Mapping) tool for database management.
- **SQLite**: A simple file-based database used for storing game data.
- **Docker**: A platform for developing, shipping, and running applications in containers.

## Installation

### Prerequisites
- Docker installed on your machine
- Basic understanding of Flask and REST APIs

### Steps to Deploy and Run the Application

1. **Clone the Repository**
   ```bash
   git clone <https://github.com/ClaudiaLlop/MIDAS_ClaudiaLlop.git>
   cd <MIDAS_ClaudiaLlop>
   ```
2. **Build the Docker Image**

   In the root directory of the project (where the Dockerfile is located), run:
    ```bash
    docker build -t my-tictactoe-app .
    ```
3. **Run the Docker Container**

   Start the container and map the ports:
    ```bash
   docker run -d -p 5000:5000 my-tictactoe-app
   ```
4. **Access the API**

    The API will be accessible at http://localhost:5000. You can use tools like Postman or cURL to interact with the API.

## API Endpoints

### Create a Match

- Endpoint: ```/create```
- Method: ```POST```
- Description: Initializes a new match and returns the ```matchId```
- Response:
```json
{
  "matchId": <new_match_id>
}
```
  
### Make a Move

- Endpoint: ```/move```
- Method: ```POST```
- Description: Makes a move in the game and returns if it was successfull or an error.
- Payload Example:
```json
{
  "matchId": <match_id>,
  "playerId": "<X or O>",
  "square": {
    "x": <1-3>,
    "y": <1-3>
  }
}
```
- Response: Depends on the state of the game. Returns a message about the move's success or failure.

   **Possible responses:**

   - If the movement is successfull the response must return the following message and state of the board, e.g.:
   ```json
   Movement successfully registered
   X| |
   | |
   | |
   ```
   - If the position described in the movement is already occupied it will return:
   ```json
   {"error": "The space is already occupied."}
   ```
  - If it is not the turn of the playerId in the request:
   ```json
   {"error": "It is player <X or O> turn."}
   ```
  - If the ```matchId``` is invalid:
   ```json
   {"error": "MatchId not found."}
   ```
  - If the values of x and y are different from 1,2,3:
   ```json
   {"error": "x and y coordinates must be integers from 1 to 3."}
   ```
  - When a player wins the match:
   ```json
   Movement successfully registered
   X|O|O
   |X|
   | |X
   Player X is the winner!
   ```
  - If there is already a winner and a new movement is sent:
   ```json
   {"message": "Match finished. Player X is the winner."}
   ```
  - If the match is a draw:
  ```json
   Movement successfully registered
   X|O|X
   O|X|X
   O|X|O
   The match is a draw!
   ```
  And more.

### Check Status

- Endpoint: ```/status```
- Method: ```GET```
- Description: Gets status of the match.
- Params: ```matchId``` must be sent in the request. ```http://localhost:5000/status?matchId=<match_id>``` 
- Response Example:
```json
{
    "board": "X|X| \n |O| \n |O|X",
    "current_turn": "X",
    "winner": null
}
```

## Configuration

### Database Configuration

The application is configured to use an SQLite database. The database file will be created in the same directory as the application.

### Logging

Logging is implemented to track the application behavior and game state changes. The logging level is set to ```INFO```.

## Testing

The project includes a set of unit tests to verify the functionality of the API. To run the tests, you can use a test framework like ```pytest```. Ensure that your database is reset to its initial state before running the tests.
```bash
pytest tests/
```

## Conclusion

This API serves as a backend for a simple Tic-Tac-Toe game, allowing multiple matches to be created and played through HTTP requests. It demonstrates basic RESTful principles and is designed for easy testing and expansion.

