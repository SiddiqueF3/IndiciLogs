from sqlalchemy import create_engine, text
import os
from sqlalchemy.orm import sessionmaker
from config import Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Database connection manager"""
    
    def __init__(self):
        self.config = Config()
        self.engine = None
        self.SessionLocal = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize database connection"""
        try:
            # If DATABASE_URL is provided (e.g., Supabase Postgres), prefer it
            database_url = os.environ.get('DATABASE_URL') or self.config.DATABASE_URL

            logger.info("Connecting using DATABASE_URL (preferred)")

            self.engine = create_engine(
                database_url,
                echo=False,
                pool_pre_ping=True,
                pool_recycle=3600,
                connect_args={
                    "sslmode": "require"
                }
            )

            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            logger.info("Database connection established successfully")

            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            return

        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            raise

    def _get_connection_strings(self):
        """Get multiple connection string formats to try"""
        server = self.config.DB_SERVER
        database = self.config.DB_DATABASE
        username = self.config.DB_USERNAME
        password = self.config.DB_PASSWORD
        driver = self.config.DB_DRIVER

        # URL encode the password to handle special characters
        import urllib.parse
        encoded_password = urllib.parse.quote_plus(password)
        encoded_username = urllib.parse.quote_plus(username)

        connection_strings = []

        if username and password:
            # Format 1: Standard with encoded credentials
            connection_strings.append(
                f"mssql+pyodbc://{encoded_username}:{encoded_password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"
            )

            # Format 2: With port
            connection_strings.append(
                f"mssql+pyodbc://{encoded_username}:{encoded_password}@{server},1433/{database}?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"
            )

            # Format 3: Raw pyodbc connection string
            raw_conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;Connection Timeout=30;"
            connection_strings.append(f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(raw_conn_str)}")

        return connection_strings
    
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()
    
    def test_connection(self):
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False
