# logger_config.py
import logging

# Configure logging
logging.basicConfig(
    filename='/home/ubuntu/dexter/wakemeup-server/logs/wakemeup_logs.log',  # Log file
    level=logging.INFO,  # Logging level
    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',  # Include the module name
    filemode='a'  # Append mode
)

# Create a logger object that can be imported and used in other files
logger = logging.getLogger(__name__)
