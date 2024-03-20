"""Test functionality for writing from config file"""

from pathlib import Path
import pandas as pd
import subscript.fmuobs._config as conf
from subscript.fmuobs.fmuobs import dump_results
import pytest

TEST_DATA = Path(__file__).parent / "testdata_fmuobs"
CONFIG_FILE_STEM = TEST_DATA / "fmuobs_config"
CONFIG_FILE_ODS = str(CONFIG_FILE_STEM) + ".ods"


@pytest.fixture(scope="session", name="summary_df")
def _fixture_summary_df():
    """Return drogon summary input as dataframe

    Returns:
        pd.DataFrame: the summary data as dataframe
    """
    summary = pd.read_csv(TEST_DATA / "drogon_summary_input.txt", sep=" ")

    return conf._ensure_caps_columns(summary)


@pytest.fixture(scope="session", name="rft_df")
def _fixture_rft_df():
    """Return drogon rft input as dataframe"""
    rft = pd.read_excel(TEST_DATA / "drogon_rft_input.ods")

    return conf._ensure_caps_columns(rft)


@pytest.fixture(scope="session", name="seismic_df")
def _fixture_seismic_df():
    """Return drogon seismic input as dataframe"""
    seismic = pd.read_csv(TEST_DATA / "drogon_seismic_input.csv")

    return conf._ensure_caps_columns(seismic)


def test_extract_summary(summary_df):
    summary = conf.extract_summary(summary_df)
    print(summary)


def test_extract_rft(rft_df):
    rft = conf.extract_rft(rft_df)
    print(rft)


def test_extract_general(seismic_df):
    seismic = conf.extract_general(seismic_df, "seismic")
    print(seismic_df)


def test_read_specific():
    rft = conf.read_tabular_file(
        "/private/dbs/git/subscript/tests/testdata_fmuobs/drogon_rft_input.ods"
    )
    print(rft.shape)


@pytest.mark.parametrize("ending", [".ods", ".xls", ".xlsx", ".csv", "_ms_sep.csv"])
def test_read_tabular_file(ending):
    """Test reading of config file"""
    correct_columns = ["OBSERVATION_TYPE", "CONTENT", "INPUT_FILE", "LABEL", "ACTIVE"]
    config = conf.read_tabular_file(str(TEST_DATA / "fmuobs_config") + ending)
    assert isinstance(
        config, pd.DataFrame
    ), f"should return pd.Dataframe but is {type(config)}"
    read_columns = config.columns.tolist()
    assert (
        read_columns == correct_columns
    ), f"Columns should be {correct_columns}, but are {read_columns}"
    assert config.shape == (
        3,
        5,
    ), f"Expecting shape (3, 5) but result was {config.shape}"


def test_parse_config_elements():
    """Test parsing of the individual elements in a config file"""
    obs_summary, observations = conf.read_config_file(CONFIG_FILE_ODS)
    print(observations)
    observations.to_csv(TEST_DATA / "dumped_observations.csv", index=False)
    obs_summary.to_csv(TEST_DATA / "dumped_summary.csv", index=False)
    ert_out = TEST_DATA / "ert_out.obs"
    dump_results(obs_summary, ertfile=ert_out)
    # conf.generate_rft_obs_files(
    # observations.loc[observations["CONTENT"] == "rft"], TEST_DATA
    # )


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
