#!/usr/bin/env python3
"""
Console Error Logs Web Application
Entry point for running the Flask application
"""

from app import app
from database.db_service import DatabaseService
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_database_connection():
    """Test database connection on startup"""
    try:
        db_service = DatabaseService()
        if db_service.test_connection():
            logger.info("Database connection test successful")
            return True
        else:
            logger.error("Database connection test failed")
            return False
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return False

if __name__ == '__main__':
    logger.info("Starting Console Error Logs Web Application")
    
    # Test database connection
    if test_database_connection():
        logger.info("Starting Flask development server...")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        logger.error("Cannot start application - database connection failed")
        print("\nPlease check your database configuration in the .env file")
        print("Copy .env.example to .env and update with your database settings")
