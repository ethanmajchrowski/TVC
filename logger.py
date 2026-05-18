import logging
import colorlog

logger = logging.getLogger("game")
logger.setLevel(logging.DEBUG)

# Colored formatter for terminal
color_formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s [%(levelname)s] %(message)s",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
)

stream_handler = colorlog.StreamHandler()
stream_handler.setFormatter(color_formatter)

# Plain file output
with open("game.log", "w") as f:
    f.close()

file_handler = logging.FileHandler("game.log")
file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
file_handler.setFormatter(file_formatter)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)