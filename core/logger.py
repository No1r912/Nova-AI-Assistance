import logging

from core.config import DATA_DIR, DEBUG


LOG_DIRECTORY = DATA_DIR / "logs"
LOG_FILE = LOG_DIRECTORY / "nova.log"


LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)


logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)



def info(message):

    logging.info(message)



def error(message):

    logging.error(message)



def warning(message):

    logging.warning(message)
