import logging
import os

def setup_logging():
    """
    Setup logging configuration.
    """
    # Get the root logger
    logger = logging.getLogger()
    
    # Set the logger level
    log_level = logging.INFO
    logger.setLevel(log_level)
   
    # Ensure there is no duplicated handlers
    if not logger.handlers:
        # configure the handler and formatter at the root logger level
        ch = logging.StreamHandler() # Create console handler and
        ch.setLevel(log_level) # set level to info
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') # Create formatter
        ch.setFormatter(formatter) # Add formatter to ch
        logger.addHandler(ch) # Add ch to logger

    # Write logs to a file
    # log_directory = "log/"
    # if not os.path.exists(log_directory):
    #     os.makedirs(log_directory)
    # log_file = os.path.join(log_directory, 'app.log')
    # file_handler = logging.FileHandler(log_file)
    # file_handler.setFormatter(logging.Formatter(log_format))
    # logging.getLogger().addHandler(file_handler)

    return logging.getLogger()