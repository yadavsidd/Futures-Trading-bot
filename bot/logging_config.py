import logging
import sys

def setup_logging():
    logger = logging.getLogger("trading_bot")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')

        # Console handler (INFO level)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler (DEBUG level, append mode)
        file_handler = logging.FileHandler("trading_bot.log", mode="a")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
