#!/usr/bin/env python3
"""
Database Connection Test Script
Use this script to troubleshoot database connectivity issues
"""

import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

def test_pyodbc_connection():
    """Test direct pyodbc connection"""
    print("=" * 50)
    print("Testing Direct pyodbc Connection")
    print("=" * 50)

    server = os.environ.get('DB_SERVER', 'dbserver-local')
    database = os.environ.get('DB_DATABASE', 'PMS_NZ_Local_NZTFS')
    username = os.environ.get('DB_USERNAME', 'pms_nz')
    password = os.environ.get('DB_PASSWORD', 'pms@@nz')
    driver = os.environ.get('DB_DRIVER', 'ODBC Driver 17 for SQL Server')

    print(f"Server: {server}")
    print(f"Database: {database}")
    print(f"Username: {username}")
    print(f"Driver: {driver}")
    print()

    # Test different server name formats
    server_formats = [
        server,                           # dbserver-local
        f"{server}\\SQLEXPRESS",         # dbserver-local\SQLEXPRESS
        f"{server},1433",                # dbserver-local,1433
        "localhost",                     # localhost
        "localhost\\SQLEXPRESS",         # localhost\SQLEXPRESS
        "127.0.0.1",                    # IP address
        ".",                            # Local default instance
        ".\\SQLEXPRESS"                 # Local named instance
    ]

    for server_name in server_formats:
        print(f"Trying server: {server_name}")

        # Test different connection string formats
        connection_strings = [
            # Format 1: Standard connection
            f"DRIVER={{{driver}}};SERVER={server_name};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;Connection Timeout=30;",

            # Format 2: Without TrustServerCertificate
            f"DRIVER={{{driver}}};SERVER={server_name};DATABASE={database};UID={username};PWD={password};Connection Timeout=30;",

            # Format 3: With Encrypt=no
            f"DRIVER={{{driver}}};SERVER={server_name};DATABASE={database};UID={username};PWD={password};Encrypt=no;Connection Timeout=30;",
        ]

        for i, conn_str in enumerate(connection_strings, 1):
            try:
                print(f"  Format {i}: ", end="")
                conn = pyodbc.connect(conn_str, timeout=10)
                cursor = conn.cursor()
                cursor.execute("SELECT 1 as test")
                result = cursor.fetchone()
                print(f"✅ SUCCESS!")
                print(f"Working connection string: {conn_str}")
                conn.close()
                return conn_str
            except Exception as e:
                print(f"❌ {str(e)[:100]}...")
        print()

    return None

def test_sqlalchemy_connection():
    """Test SQLAlchemy connection"""
    print("=" * 50)
    print("Testing SQLAlchemy Connection")
    print("=" * 50)
    
    try:
        from config import Config
        from sqlalchemy import create_engine, text
        
        config = Config()
        print(f"SQLAlchemy URL: {config.DATABASE_URL}")
        print()
        
        engine = create_engine(config.DATABASE_URL, echo=True)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            print("✅ SQLAlchemy connection successful!")
            return True
            
    except Exception as e:
        print(f"❌ SQLAlchemy connection failed: {str(e)}")
        return False

def list_available_drivers():
    """List available ODBC drivers"""
    print("=" * 50)
    print("Available ODBC Drivers")
    print("=" * 50)
    
    drivers = pyodbc.drivers()
    for driver in drivers:
        if 'SQL Server' in driver:
            print(f"✅ {driver}")
        else:
            print(f"   {driver}")

def main():
    print("Console Error Logs - Database Connection Tester")
    print("=" * 60)
    print()
    
    # List available drivers
    list_available_drivers()
    print()
    
    # Test direct pyodbc connection
    working_conn_str = test_pyodbc_connection()
    print()
    
    # Test SQLAlchemy connection
    test_sqlalchemy_connection()
    print()
    
    if working_conn_str:
        print("🎉 Connection successful!")
        print("You can now run the web application with: python run.py")
    else:
        print("❌ All connection attempts failed.")
        print("\nTroubleshooting tips:")
        print("1. Verify SQL Server is running")
        print("2. Check if SQL Server allows remote connections")
        print("3. Verify firewall settings (port 1433)")
        print("4. Try connecting with SQL Server Management Studio first")
        print("5. Check if the server name is correct (try with instance name like SERVER\\SQLEXPRESS)")

if __name__ == "__main__":
    main()
