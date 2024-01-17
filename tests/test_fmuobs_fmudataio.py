"""Tests export with fmu-dataio"""
import os
import yaml
import shutil
from pathlib import Path
from subscript.fmuobs.fmuobs import export_w_meta

TEST_DATA = Path(__file__).parent / "testdata_fmuobs/drogon"


def test_export_w_meta(tmp_path):
    """Test function export_w_meta

    Args:
        tmp_path (PosixPath): place to store results of test
    """
    test_ens_path = TEST_DATA / "ertrun1"
    test_config_path = TEST_DATA / "proj/fmuconfig/output/global_variables.yml"

    obs_path = TEST_DATA / "../ert-doc.yml"
    with open(obs_path, "r", encoding="utf-8") as stream:
        observations = yaml.safe_load(stream)
    print(observations)

    case_path = tmp_path / test_ens_path.name
    expected_ex_path = str(
        case_path / "share/results/dictionaries/observations--all.json"
    )
    conf_path = tmp_path / test_config_path.name
    shutil.copytree(test_ens_path, case_path)
    shutil.copy(test_config_path, conf_path)

    os.chdir(tmp_path)
    assert len(observations) > 0
    ex_path = export_w_meta(observations, conf_path, case_path)
    assert ex_path == expected_ex_path
    posix_path = Path(ex_path)
    meta_path = posix_path.parent / f".{posix_path.name}.yml"
    assert meta_path.exists(), f"No metadata with path {meta_path}"
