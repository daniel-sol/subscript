"""Test functionality for writing from config file"""

from pathlib import Path
import pandas as pd
from subscript.fmuobs._config import read_config_file
import pytest

CONFIG_FILE_STEM = str(Path(__file__).parent / "testdata_fmuobs/fmuobs_config")


@pytest.mark.parametrize("ending", [".ods", ".xls", ".xlsx", ".csv", "_ms_sep.csv"])
def test_reading_config(ending):
    """Test reading of config file"""
    correct_columns = ["observation_type", "content", "input_file", "active"]
    config = read_config_file(CONFIG_FILE_STEM + ending)
    assert isinstance(config, pd.DataFrame)
    assert config.columns.tolist() == correct_columns
    assert config.shape == (3, 4)


def test_parse_config_elements():
    """Test parsing of the individual elements in a config file"""


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
