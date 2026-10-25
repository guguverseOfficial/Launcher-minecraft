import logging

def setup_logger():
    logging.basicConfig(
        filename='launcher.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger("GuguverseLauncher")