@echo off
echo ========================================
echo Console Error Logs Web Application Setup
echo ========================================

echo.
echo 1. Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo.
echo 2. Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo 3. Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo 4. Setting up environment configuration...
if not exist .env (
    copy .env.example .env
    echo Created .env file from template
    echo IMPORTANT: Please edit .env file with your database settings!
) else (
    echo .env file already exists
)

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file with your database settings
echo 2. Run the SQL scripts in sql/stored_procedures.sql
echo 3. Start the application with: python run.py
echo.
pause
