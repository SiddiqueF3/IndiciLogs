from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from database.db_service import DatabaseService
from config import Config
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database service
db_service = DatabaseService()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in (simple session check)
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login')
def login():
    """Login page"""
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint for user login"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password are required'}), 400
        
        # Authenticate user
        auth_result = db_service.authenticate_user(username, password)
        
        if auth_result['success']:
            # Store user info in session
            session['user_id'] = auth_result['user']['id']
            session['username'] = auth_result['user']['username']
            session['role'] = auth_result['user']['role']
            session['full_name'] = auth_result['user']['fullName']
            
            return jsonify(auth_result)
        else:
            return jsonify(auth_result), 401
            
    except Exception as e:
        app.logger.error(f"Error in login: {str(e)}")
        return jsonify({'success': False, 'message': 'Login failed. Please try again.'}), 500

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """Main page with the console error logs table"""
    return render_template('index.html')

@app.route('/api/logs')
@login_required
def get_logs():
    """API endpoint to fetch filtered console error logs"""
    try:
        # Get filter parameters from request
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        time_from = request.args.get('time_from')
        time_to = request.args.get('time_to')
        practice_id = request.args.get('practice_id')
        
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 25))
        
        # Get search parameter
        search = request.args.get('search', '')
        
        # Fetch data from database
        logs, total_count = db_service.get_console_error_logs(
            date_from=date_from,
            date_to=date_to,
            time_from=time_from,
            time_to=time_to,
            practice_id=practice_id,
            search=search,
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            'data': logs,
            'total': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_count + per_page - 1) // per_page
        })
        
    except Exception as e:
        import traceback
        error_details = {
            'error': str(e),
            'type': type(e).__name__,
            'traceback': traceback.format_exc()
        }
        app.logger.error(f"Error in get_logs: {error_details}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/practice-ids')
@login_required
def get_practice_ids():
    """API endpoint to fetch distinct practice IDs"""
    try:
        practice_ids = db_service.get_practice_ids()
        app.logger.info(f"Returning {len(practice_ids)} practice IDs to frontend")
        return jsonify(practice_ids)
    except Exception as e:
        import traceback
        app.logger.error(f"Error in get_practice_ids: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-connection')
def test_connection():
    """Test endpoint to check database connectivity"""
    try:
        if db_service.test_connection():
            return jsonify({'status': 'success', 'message': 'Database connection successful'})
        else:
            return jsonify({'status': 'error', 'message': 'Database connection failed'}), 500
    except Exception as e:
        import traceback
        app.logger.error(f"Error in test_connection: {traceback.format_exc()}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/logs-summary')
@login_required
def get_logs_summary():
    """API endpoint to fetch aggregated console error logs (Common Logs)"""
    try:
        # Get filter parameters from request
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        practice_id = request.args.get('practice_id')

        # Pagination
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 25))

        logs, total_count = db_service.get_console_error_logs_summary(
            date_from=date_from,
            date_to=date_to,
            practice_id=practice_id,
            page=page,
            per_page=per_page
        )

        return jsonify({
            'data': logs,
            'total': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_count + per_page - 1) // per_page
        })
    except Exception as e:
        import traceback
        app.logger.error(f"Error in get_logs_summary: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
