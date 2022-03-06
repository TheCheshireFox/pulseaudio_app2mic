import logging
import datetime

from pathlib import Path
import pathlib

logging.addLevelName(logging.INFO, 'INFO')
logging.addLevelName(logging.WARNING, 'WARN')
logging.addLevelName(logging.ERROR, 'ERR ')
logging.addLevelName(logging.CRITICAL, 'CRIT')

def create_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(__name__)

    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s|%(name)s|%(levelname)s: %(message)s')

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)

    path = pathlib.Path.home() / Path('.local/pulseaudio_app2mic/logs')
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    sh = logging.FileHandler(path / f'{__name__}-{datetime.datetime.now().date}.log', 'w+')
    sh.setLevel(logging.INFO)
    sh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(sh)

    return logger