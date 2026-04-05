import logging
import os

def setup_logger(name, log_file, level=logging.INFO):
    """Sets up a logger that writes to a file."""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

# Global logger for the tool
logger = setup_logger('xsstriker', 'xsstriker/reports/xsstriker.log')

def log_error(msg):
    logger.error(msg)

def log_info(msg):
    logger.info(msg)
