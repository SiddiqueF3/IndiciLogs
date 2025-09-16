# Console Error Logs Web Application

A Flask-based web application for viewing and filtering console error logs from a SQL Server database.

## Features

- **Responsive Data Table**: Paginated, searchable, and sortable display of console error logs
- **Advanced Filtering**: Filter by date range, time range, and practice ID
- **Real-time Search**: Search across all fields with live updates
- **Stack Trace Viewer**: Click to view full stack traces in a modal
- **Bootstrap 5 UI**: Clean, modern, and mobile-responsive interface

## Prerequisites

- Python 3.8 or higher
- SQL Server with the LOG.tblconsoleErrorLogs table
- ODBC Driver 17 for SQL Server (or compatible driver)

## Installation

1. **Clone or download the project**
   ```bash
   cd ConsoleLogWeb
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure database connection**
   ```bash
   copy .env.example .env
   ```
   
   Edit `.env` file with your database settings:
   ```
   DB_SERVER=your_sql_server_name
   DB_DATABASE=your_database_name
   DB_USERNAME=your_username
   DB_PASSWORD=your_password
   DB_DRIVER=ODBC Driver 17 for SQL Server
   SECRET_KEY=your-secret-key-here
   ```

5. **Create stored procedures**
   
   Run the SQL script in `sql/stored_procedures.sql` on your SQL Server database to create the required stored procedures:
   - `LOG.sp_GetConsoleErrorLogs`
   - `LOG.sp_GetPracticeIDs`

## Running the Application

1. **Start the application**
   ```bash
   python run.py
   ```

2. **Access the web interface**
   
   Open your browser and navigate to: `http://localhost:5000`

## Database Schema

The application expects a table with the following structure:

```sql
LOG.tblconsoleErrorLogs (
    id INT PRIMARY KEY,
    practiceid INT,
    stacktraces TEXT,
    ErrorMassage TEXT,
    url VARCHAR(500),
    ErrorTime DATETIME,
    insertdat DATETIME,
    updatedat DATETIME,
    JiraStatus VARCHAR(50),
    Status VARCHAR(50)
)
```

## API Endpoints

- `GET /` - Main application page
- `GET /api/logs` - Fetch filtered console error logs
  - Query parameters: `date_from`, `date_to`, `time_from`, `time_to`, `practice_id`, `search`, `page`, `per_page`
  - Backed by `LOG.sp_GetConsoleErrorLogs` which performs server-side pagination and returns a `TotalCount` column used to compute overall totals.
- `GET /api/practice-ids` - Fetch distinct practice IDs

## Usage

1. **Filtering Data**
   - Use date pickers to filter by date range
   - Use time pickers to filter by time range
   - Select a practice ID from the dropdown
   - Use the search box for text-based filtering

2. **Viewing Data**
   - Click on truncated stack traces to view full details
   - Use table sorting by clicking column headers
   - Navigate through pages using the pagination controls

## Troubleshooting

1. **Database Connection Issues**
   - Verify your `.env` file settings
   - Ensure SQL Server is accessible
   - Check ODBC driver installation

2. **Stored Procedure Errors**
   - Ensure stored procedures are created in the LOG schema
   - Verify user permissions for executing stored procedures

3. **Application Errors**
   - Check the console output for detailed error messages
   - Verify all dependencies are installed correctly

## Development

To run in development mode with debug enabled:
```bash
python app.py
```

## Production Deployment

For production deployment, consider:
- Using a WSGI server like Gunicorn
- Setting up proper logging
- Using environment-specific configuration
- Implementing proper security measures
