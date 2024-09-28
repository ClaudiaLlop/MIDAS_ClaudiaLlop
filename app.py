import logging
from app import create_app, db

app = create_app()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    with app.app_context():
        db.create_all()
        logger.info("Tables created (if they didn't exist).")
    logger.info("Service started")
    app.run(host='0.0.0.0', port=5000, debug=True)
