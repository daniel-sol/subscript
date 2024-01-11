import re
from pathlib import Path
import yaml
from subscript.fmuobs.fmuobs import autoparse_file, df2obsdict
from pandas import DataFrame
import pytest

from ._common_fmuobs import (
    _find_observation_file,
    _assert_compulsories_are_correct,
    _compare_to_results_in_file,
)

TEST_DATA = "testdata_fmuobs/"


@pytest.mark.integration
@pytest.mark.parametrize(
    "obs_file",
    ["drogon/drogon_wbhp_rft_wct_gor_tracer_4d_plt.obs", "snorre/all_obs_230310.txt"],
)
def test_from_autoparse_file_to_df2obsdict(obs_file):
    """Test dictionaries produced for drogon and snorre are as expected

    Args:
        obs_file (str): ert observation file
    """
    full_data_path = _find_observation_file(obs_file, "")
    file_type, dataframe = autoparse_file(full_data_path)
    assert file_type == "ert"
    assert isinstance(dataframe, DataFrame)
    result_dict = df2obsdict(dataframe, full_data_path.parent)
    assert isinstance(
        result_dict, dict
    ), f"Results from dfobsdict should be dictionary, but is {type(result_dict)}"
    assert isinstance(
        result_dict["general"], dict
    ), "key general from df2obsdict should be dictionary"
    for key, item in result_dict.items():
        if key == "general":
            continue
        assert isinstance(
            item, list
        ), f"{key} is expected to be list but is {type(item)}"
    # _compare_to_results_in_file(
    #     result_dict,
    #     Path(__file__).parent
    #     / TEST_DATA
    #     / re.sub(r"\..*", "", obs_file.split("/")[-1]),
    # )
