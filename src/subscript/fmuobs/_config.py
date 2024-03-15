"""Code related to fmobs config stuff"""

import logging
import pandas as pd


def read_tabular_file(tabular_file_path: str, sep=",") -> pd.DataFrame:
    """Read csv or excel file into pandas dataframe

    Args:
        tabular_file_path (str): path to file
        sep (str, optional): seperator for csv files. Defaults to ",".

    Returns:
        pd.DataFrame: the dataframe read from file
    """
    logger = logging.getLogger(__name__ + ".read_tabular_file")
    logger.info("Reading file %s", tabular_file_path)
    dataframe = pd.DataFrame()
    try:
        dataframe = pd.read_csv(tabular_file_path, sep=sep)
    except UnicodeDecodeError:
        dataframe = pd.read_excel(tabular_file_path)
    nr_cols = dataframe.shape[1]
    logger.debug("Nr of columns are %s", nr_cols)
    if nr_cols == 1:
        logger.debug("Wrong number of columns, trying with separator other separators")
        for separator in [";", " "]:
            logger.debug("Trying with |%s| as separator", separator)
            dataframe = read_tabular_file(tabular_file_path, sep=separator)
            if dataframe.shape[1] > 1:
                break
        if dataframe.shape == 1:
            raise IOError(
                "File is not parsed correctly, check if there is something wrong"
            )

    return dataframe


def read_config_file(config_file_name: str) -> pd.DataFrame:
    """Parse config file

    Args:
        config_file_name (str): path to config file

    Returns:
        pd.DataFrame: the config file as dataframe
    """
    logger = logging.getLogger(__name__ + ".read_config_file")
    config = read_tabular_file(config_file_name)
    logger.debug("Shape of config file: %s", config.shape)
    return config
