"""Code related to fmobs config stuff"""

import logging
import pandas as pd


def read_config_file(config_file_path: str, sep=",") -> pd.DataFrame:
    """Read csv or excel file into pandas dataframe

    Args:
        config_file_path (str): path to file
        sep (str, optional): seperator for csv files. Defaults to ",".

    Returns:
        pd.DataFrame: the dataframe read from file
    """
    logger = logging.getLogger(__name__ + ".read_config_file")
    config = pd.DataFrame()
    try:
        config = pd.read_csv(config_file_path, sep=sep)
    except UnicodeDecodeError:
        config = pd.read_excel(config_file_path)
    nr_cols = config.shape[1]
    logger.debug("Nr of columns are %s", nr_cols)
    if nr_cols == 1:
        logger.debug("Wrong number of columns, trying with seperator ;")
        config = read_config_file(config_file_path, sep=";")

    return config
