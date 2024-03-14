"""Code related to fmobs config stuff"""

import pandas as pd
import logging


def read_config_file(config_file_path: str) -> pd.DataFrame:
    logger = logging.getLogger(__name__ + ".read_config_file")
    config = pd.DataFrame()
    try:
        config = pd.read_csv(config_file_path)
    except UnicodeDecodeError:
        config = pd.read_excel(config_file_path)

    return config
