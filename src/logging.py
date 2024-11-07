import logging.config
import os
from typing import Optional

import yaml

LOG_CONFIG = 'src/logger-config.yml'
    
def get_logger(logger_config: Optional[str]):
    if logger_config is None:
        raise ValueError
    
    elif not os.path.exists(logger_config):
        raise FileNotFoundError
    
    else:
        with open(logger_config, 'r') as cfg:
            logging.config.dictConfig(yaml.load(cfg, yaml.SafeLoader))
            logger = logging.getLogger('chatbot')
            logger.info('[OK] loaded logger')
        
    return logger

logger = get_logger(LOG_CONFIG)