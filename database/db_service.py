from sqlalchemy import text
from database.connection import DatabaseConnection
from database.models import ConsoleErrorLog
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service layer for database operations"""
    
    def __init__(self):
        self.db_connection = DatabaseConnection()
    
    def get_console_error_logs(self, date_from=None, date_to=None, time_from=None, 
                             time_to=None, practice_id=None, search=None, 
                             page=1, per_page=25):
        """
        Fetch console error logs using stored procedure with filtering and pagination
        """
        try:
            session = self.db_connection.get_session()
            
            # Prepare parameters for stored procedure
            params = {
                'DateFrom': date_from,
                'DateTo': date_to,
                'TimeFrom': time_from,
                'TimeTo': time_to,
                'PracticeID': practice_id
            }
            
            # Supabase/Postgres function call without schema prefix
            sp_query = text("""
                SELECT * FROM sp_getconsoleerrorlogs(
                    :DateFrom,
                    :DateTo,
                    :TimeFrom,
                    :TimeTo,
                    :PracticeID,
                    :Page,
                    :PerPage
                )
            """)

            # Include pagination params
            params_with_pagination = {
                **params,
                'Page': page,
                'PerPage': per_page
            }

            result = session.execute(sp_query, params_with_pagination)
            rows = result.fetchall()
            
            # Convert to list of dictionaries
            logs = []
            for row in rows:
                log_dict = {
                    'id': row[0],
                    'practiceid': row[1],
                    'stacktraces': row[2],
                    'ErrorMassage': row[3],
                    'url': row[4],
                    'ErrorTime': self._format_time_string(row[5]),  # Keep as string for time values
                    'insertdat': self._format_datetime(row[6]),
                    'updatedat': self._format_datetime(row[7]),
                    'JiraStatus': row[8],
                    'Status': row[9],
                    'LLMSolution': row[10] if len(row) > 10 else None
                }
                logs.append(log_dict)
            
            # Read TotalCount from the last column if rows returned, else 0
            total_count = int(rows[0][-1]) if rows else 0
            
            # Apply search filter client-side if provided (affects count on this page only)
            if search:
                search_lower = search.lower()
                logs = [log for log in logs if any(
                    search_lower in str(value).lower() 
                    for value in log.values() 
                    if value is not None
                )]
                # When client-side searching is applied here, reflect the filtered count for this page
                total_count = len(logs)
            
            session.close()
            return logs, total_count
            
        except Exception as e:
            logger.error(f"Error fetching console error logs: {str(e)}")
            if 'session' in locals():
                session.close()
            raise
    
    def get_practice_ids(self):
        """
        Fetch distinct practice IDs using stored procedure
        """
        try:
            session = self.db_connection.get_session()

            # Query table directly for distinct practice IDs (Supabase tables without schema)
            result = session.execute(text(
                "SELECT DISTINCT practiceid FROM tblconsoleerrorlogs WHERE practiceid IS NOT NULL ORDER BY practiceid"
            ))
            rows = result.fetchall()

            practice_ids = [{'id': row[0]} for row in rows if row[0] is not None]

            logger.info(f"Loaded {len(practice_ids)} unique practice IDs")
            session.close()
            return practice_ids

        except Exception as e:
            logger.error(f"Error fetching practice IDs: {str(e)}")
            if 'session' in locals():
                session.close()
            raise
    
    def test_connection(self):
        """Test database connection"""
        return self.db_connection.test_connection()

    def authenticate_user(self, username, password):
        """
        Authenticate user using stored procedure
        """
        try:
            session = self.db_connection.get_session()

            sp_query = text("""
                SELECT * FROM sp_consoleloguser_login(
                    :username,
                    :password
                )
            """)

            result = session.execute(sp_query, {
                'username': username,
                'password': password
            })
            
            row = result.fetchone()
            session.close()

            if row and (row[0] == 1 or str(row[0]) == '1'):
                return {
                    'success': True,
                    'user': {
                        'id': row[1],      # UserId
                        'username': row[2], # Username
                        'role': row[3],     # Role
                        'fullName': row[4]  # FullName
                    }
                }
            else:
                return {
                    'success': False,
                    'message': 'Invalid username or password'
                }

        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            return {
                'success': False,
                'message': 'Authentication failed. Please try again.'
            }

    def get_console_error_logs_summary(self, date_from=None, date_to=None, practice_id=None, page=1, per_page=25):
        """
        Fetch aggregated/summary console error logs using stored procedure with pagination
        """
        try:
            session = self.db_connection.get_session()

            params = {
                'DateFrom': date_from,
                'DateTo': date_to,
                'PracticeID': practice_id,
                'Page': page,
                'PerPage': per_page
            }

            sp_query = text("""
                SELECT * FROM sp_getconsoleerrorlogssummary(
                    :DateFrom,
                    :DateTo,
                    :PracticeID,
                    :Page,
                    :PerPage
                )
            """)

            result = session.execute(sp_query, params)
            rows = result.fetchall()

            logs = []
            for row in rows:
                log_dict = {
                    'practiceids': row[0],
                    'stacktraces': row[1],
                    'ErrorMassage': row[2],
                    'LLMSolution': row[3],
                    'ErrorCount': row[4]
                }
                logs.append(log_dict)

            total_count = int(rows[0][-1]) if rows else 0

            session.close()
            return logs, total_count

        except Exception as e:
            logger.error(f"Error fetching console error logs summary: {str(e)}")
            if 'session' in locals():
                session.close()
            raise

    def _format_datetime(self, dt_value):
        """Helper method to safely format datetime objects"""
        if dt_value is None:
            return None

        # If it's already a string, return as is
        if isinstance(dt_value, str):
            return dt_value

        # If it's a datetime object, format it
        if hasattr(dt_value, 'isoformat'):
            return dt_value.isoformat()

        # If it's some other type, convert to string
        return str(dt_value)

    def _format_time_string(self, time_value):
        """Helper method to safely format time values as strings"""
        if time_value is None:
            return None

        # If it's already a string, return as is
        if isinstance(time_value, str):
            return time_value

        # If it's a time object, format it as string
        if hasattr(time_value, 'strftime'):
            try:
                return time_value.strftime('%I:%M %p')  # Format as "9:31 PM"
            except:
                return str(time_value)

        # If it's a datetime object, extract time part
        if hasattr(time_value, 'time'):
            try:
                return time_value.strftime('%I:%M %p')  # Format as "9:31 PM"
            except:
                return str(time_value)

        # If it's some other type, convert to string
        return str(time_value)
