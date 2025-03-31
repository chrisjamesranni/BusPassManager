import logging
from app import app

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Run the application
if __name__ == "__main__":
    logger.debug("Starting application on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
