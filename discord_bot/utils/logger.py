import logging
import os

def setup_logging():
    """
    Setup logging configuration.
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format)

    # Write logs to a file
    # log_directory = "log/"
    # if not os.path.exists(log_directory):
    #     os.makedirs(log_directory)
    # log_file = os.path.join(log_directory, 'app.log')
    # file_handler = logging.FileHandler(log_file)
    # file_handler.setFormatter(logging.Formatter(log_format))
    # logging.getLogger().addHandler(file_handler)

    return logging.getLogger()
