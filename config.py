import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # SQL Server Database Configuration (legacy)
    DB_SERVER = os.environ.get('DB_SERVER') or 'dbserver-local'
    DB_DATABASE = os.environ.get('DB_DATABASE') or 'PMS_NZ_Local_NZTFS'
    DB_USERNAME = os.environ.get('DB_USERNAME') or 'pms_nz'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'pms@@nz'
    DB_DRIVER = os.environ.get('DB_DRIVER') or 'ODBC Driver 17 for SQL Server'

    @property
    def DATABASE_URL(self):
        """Construct database connection string.

        Priority:
        1) If env DATABASE_URL is set (e.g. Supabase Postgres), return it verbatim
        2) Otherwise, construct the SQL Server URL (legacy)
        """
        env_url = os.environ.get('DATABASE_URL')
        if env_url:
            return env_url

        driver = self.DB_DRIVER.replace(' ', '+')

        if self.DB_USERNAME and self.DB_PASSWORD:
            # SQL Server Authentication with additional connection parameters
            return (f"mssql+pyodbc://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_SERVER}/{self.DB_DATABASE}"
                   f"?driver={driver}&timeout=30&TrustServerCertificate=yes")
        else:
            # Windows Authentication
            return (f"mssql+pyodbc://@{self.DB_SERVER}/{self.DB_DATABASE}"
                   f"?driver={driver}&trusted_connection=yes&timeout=30&TrustServerCertificate=yes")



        
