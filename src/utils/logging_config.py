import logging
import os
import sys
import traceback
from logging.handlers import RotatingFileHandler
from flask import request, session

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Configure logger
logger = logging.getLogger('storyquest')
logger.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_format)

# File handler for general logs
file_handler = RotatingFileHandler(
    os.path.join(logs_dir, 'storyquest.log'),
    maxBytes=10485760,  # 10MB
    backupCount=10
)
file_handler.setLevel(logging.INFO)
file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_format)

# File handler specifically for authentication logs with detailed information
auth_file_handler = RotatingFileHandler(
    os.path.join(logs_dir, 'auth.log'),
    maxBytes=10485760,  # 10MB
    backupCount=10
)
auth_file_handler.setLevel(logging.DEBUG)
auth_format = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')
auth_file_handler.setFormatter(auth_format)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.addHandler(auth_file_handler)

# Create authentication logger that inherits from main logger
auth_logger = logging.getLogger('storyquest.auth')
auth_logger.setLevel(logging.DEBUG)

def log_authentication_attempt(success, username, error=None):
    """
    Log authentication attempts with detailed context information
    
    Args:
        success (bool): Whether authentication was successful
        username (str): Username that attempted to authenticate
        error (Exception, optional): Exception if one occurred
    """
    # Get request information for context
    ip = request.remote_addr if request else "No request context"
    user_agent = request.user_agent.string if request and request.user_agent else "No user agent"
    endpoint = request.endpoint if request else "No endpoint"
    method = request.method if request else "No method"
    
    # Build log message with context
    msg = f"Authentication {'SUCCESS' if success else 'FAILURE'} - "
    msg += f"User: {username} - IP: {ip} - Endpoint: {endpoint} - Method: {method}"
    
    # Add session info if available
    if session:
        try:
            if 'user_id' in session:
                msg += f" - Session user_id: {session.get('user_id')}"
        except Exception as e:
            msg += f" - Session access error: {str(e)}"
    
    # Log at appropriate level with context
    if success:
        auth_logger.info(msg)
    else:
        if error:
            msg += f" - Error: {str(error)}"
            error_traceback = traceback.format_exc()
            auth_logger.error(f"{msg}\nTraceback: {error_traceback}")
        else:
            auth_logger.warning(msg)
    
    return msg

def log_session_state():
    """Log the current session state for debugging"""
    try:
        session_data = {k: v for k, v in session.items()} if session else {}
        auth_logger.debug(f"Current session state: {session_data}")
        return session_data
    except Exception as e:
        error_traceback = traceback.format_exc()
        auth_logger.error(f"Error accessing session: {str(e)}\nTraceback: {error_traceback}")
        return {"error": str(e)}
