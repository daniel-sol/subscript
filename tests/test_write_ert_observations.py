"""Test functionality for writing from config file"""

from pathlib import Path
import pandas as pd
import subscript.fmuobs._config as conf
import pytest

TEST_DATA = Path(__file__).parent / "testdata_fmuobs"
CONFIG_FILE_STEM = TEST_DATA / "/fmuobs_config"
CONFIG_FILE_ODS = str(CONFIG_FILE_STEM) + ".ods"


@pytest.fixture(scope="session", name="summary_df")
def _fixture_summary_df():
    """Return drogon summary input as dataframe

    Returns:
        _type_: _description_
    """
    summary = pd.read_csv(TEST_DATA / "drogon_summary_input.txt", sep=" ")

    return conf._ensure_low_cap_columns(summary)


def test_extract_summary(summary_df):
    summary = conf.extract_summary(summary_df)
    print(summary)


@pytest.mark.parametrize("ending", [".ods", ".xls", ".xlsx", ".csv", "_ms_sep.csv"])
def test_reading_config(ending):
    """Test reading of config file"""
    correct_columns = ["observation_type", "content", "input_file", "active"]
    config = conf.read_tabular_file(str(CONFIG_FILE_STEM) + ending)
    assert isinstance(
        config, pd.DataFrame
    ), f"should return pd.Dataframe but is {type(config)}"
    read_columns = config.columns.tolist()
    assert (
        read_columns == correct_columns
    ), f"Columns should be {read_columns}, but are {correct_columns}"
    assert config.shape == (
        3,
        4,
    ), f"Expecting shape (3,4) but result was {config.shape}"


def test_parse_config_elements():
    """Test parsing of the individual elements in a config file"""
    conf.read_config_file(CONFIG_FILE_ODS)


def test_write_controls_from_config():
    """Test writing of controls file from config file"""
    pass


def test_dump_w_fmu_dataio():
    """Test writing files to disk with fmu_dataio"""
    pass


def write_summary_observations_from_config():
    """Test writing of summary observations from config file"""

    pass


def write_rft_observations_from_config():
    """Test writing of rft files from config file"""

    pass


def write_general_observations_from_config():
    """Test writing of general observations from config"""
    pass


def test_write_observations_from_config():
    """Test writing of all observations from config, might not be a test"""
    pass


def test_write_controls_from_config():
    """Test writing of controls file from config file"""
    pass


def test_write_observations_from_controls():
    """Test writing of observations file from control file, might not be a test"""
    pass
