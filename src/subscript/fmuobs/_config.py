"""Code related to fmobs config stuff"""

import logging
from typing import Union
from pathlib import Path, PosixPath
import pandas as pd
import numpy as np


def _read_csv(tabular_file_path: Union[str, PosixPath], sep: str) -> pd.DataFrame:
    logger = logging.getLogger(__name__ + "._read_table")
    logger.debug("Performing the actual attempt to read %s as csv", tabular_file_path)
    return pd.read_csv(tabular_file_path, sep=sep)


def _ensure_low_cap_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    dataframe.columns = [col.lower() for col in dataframe.columns]
    return dataframe


def read_tabular_file(
    tabular_file_path: Union[str, PosixPath], sep=","
) -> pd.DataFrame:
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
        dataframe = _read_csv(tabular_file_path, sep)
    except UnicodeDecodeError:
        dataframe = pd.read_excel(tabular_file_path)
    nr_cols = dataframe.shape[1]
    logger.debug("Nr of columns are %s", nr_cols)
    if nr_cols == 1:
        logger.debug("Wrong number of columns, trying with other separators")
        for separator in [";", " "]:
            logger.debug("Trying with |%s| as separator", separator)
            dataframe = _read_csv(tabular_file_path, separator)
            if dataframe.shape[1] > 1:
                break
    if dataframe.shape == 1:
        raise IOError("File is not parsed correctly, check if there is something wrong")

    return dataframe


def extract_rft_obs(in_frame: pd.DataFrame) -> dict:
    pass


def extract_general(in_frame: pd.DataFrame) -> dict:
    pass


def extract_summary(in_frame: pd.DataFrame, key_identifier="vector") -> dict:
    """Extract summary to pd.Dataframe format for fmu obs

    Args:
        in_frame (pd.DataFrame): the dataframe to extract from
        key_identifier (str, optional): name of column to be used to make lables. Defaults to "VECTOR".

    Returns:
        dict: the results as a dictionary
    """
    logger = logging.getLogger(__name__ + ".extract_summary")
    logger.debug("Columns in dataframe %s", in_frame.columns.tolist())
    all_summary_obs = []
    for key in in_frame[key_identifier].unique():
        logger.debug("Making obs frame for %s", key)
        key_frame = in_frame.loc[in_frame[key_identifier] == key]
        report_frame = key_frame.copy()
        logger.debug("shape of data for %s %s", key, report_frame.shape)
        if key_frame.shape[0] == 1:
            logger.debug("Just one row")
            obs_lable = key_frame["date"].values.tolist().pop().replace("-", "_")
            logger.debug(obs_lable)

        else:
            logger.debug("Multiple rows")
            logger.debug(key_frame[key_identifier].shape)
            obs_lable = range(key_frame.shape[0])
            logger.debug(range(key_frame.shape[0]))
        logger.debug("Adding label(s) %s", obs_lable)
        report_frame["lable"] = obs_lable
        all_summary_obs.append(report_frame)

    logger.debug("Concatenating %s summary series", len(all_summary_obs))
    logger.debug("Last object has columns %s", all_summary_obs[-1].columns)
    all_summary_obs = pd.concat(all_summary_obs)
    all_summary_obs["lable"] = (
        all_summary_obs[key_identifier].str.replace(":", "_")
        + "_"
        + all_summary_obs["lable"].astype(str)
    )
    logger.debug("Returning results %s", all_summary_obs)
    return all_summary_obs


def read_config_file(
    config_file_name: Union[str, PosixPath], parent_folder: Union[str, PosixPath] = None
) -> pd.DataFrame:
    """Parse config file

    Args:
        config_file_name (str): path to config file

    Returns:
        pd.DataFrame: the config file as dataframe
    """
    logger = logging.getLogger(__name__ + ".read_config_file")
    config = read_tabular_file(config_file_name)
    logger.debug("Shape of config file: %s", config.shape)
    if parent_folder is None:
        parent_folder = Path(config_file_name).parent
    else:
        parent_folder = Path(parent_folder)

    obs_data = {}
    obs_summary = []
    for rnr, row in config.iterrows():
        file_contents = read_tabular_file(parent_folder / row["input_file"])
        if row["active"] != "yes":
            logger.info("row %s is deactivated", rnr)
            continue
        file_contents = _ensure_low_cap_columns(file_contents)
        logger.debug(file_contents)
        obs_type = row["observation_type"]
        content = row["content"]
        obs_type = row["observation_type"]
        if obs_type not in obs_data:
            obs_data[obs_type] = {}
        if content not in obs_data[obs_type]:
            obs_data[obs_type][content] = []
        obs_data[obs_type][content].append(file_contents)

    logger.debug(obs_data)
    return config
