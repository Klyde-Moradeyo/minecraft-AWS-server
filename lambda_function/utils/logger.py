import logging
import os

def setup_logging():
    """
    Setup logging configuration.
    """
    # Get the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # or whichever level you desire

    # Ensure there is no duplicated handlers
    if not logger.handlers:
        # Create console handler and set level to info
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Add formatter to ch
        ch.setFormatter(formatter)

        # Add ch to logger
        logger.addHandler(ch)

    # Write logs to a file
    # log_directory = "log/"
    # if not os.path.exists(log_directory):
    #     os.makedirs(log_directory)
    # log_file = os.path.join(log_directory, 'app.log')
    # file_handler = logging.FileHandler(log_file)
    # file_handler.setFormatter(logging.Formatter(log_format))
    # logging.getLogger().addHandler(file_handler)

    return logging.getLogger()
