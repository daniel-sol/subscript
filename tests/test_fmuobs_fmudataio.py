"""Tests export with fmu-dataio"""
import os
import yaml
import shutil
from pathlib import Path
from subscript.fmuobs.fmuobs import export_w_meta, main
from subscript.fmuobs.fmuobs import get_parser
import pytest

TEST_DATA = Path(__file__).parent / "testdata_fmuobs/drogon"
TEST_DATA_ENS_PATH = TEST_DATA / "ertrun1"
TEST_DATA_FMU_CONFIG_PATH = TEST_DATA / "proj/"
RELATIVE_PATH_TO_CONFIG = "fmuconfig/output/global_variables.yml"


def _setup_ert_run_setting(root_path, file_ending="json", export_folder="dictionaries"):
    """Replicate fmu like structure for test

    Args:
        root_path (PosixPath): the root for making structure

    Returns:
        tuple: the neccessary paths for the test, project_path, case_path, and path to expected results
    """
    case_path = root_path / TEST_DATA_ENS_PATH.name
    expected_ex_path = str(
        case_path / f"share/results/{export_folder}/observations--all.{file_ending}"
    )
    project_path = root_path / "proj/"  # /thisproject/" TEST_DATA_FMU_CONFIG_PATH.name
    shutil.copytree(TEST_DATA_ENS_PATH, case_path)
    shutil.copytree(TEST_DATA_FMU_CONFIG_PATH, project_path)
    return project_path, case_path, expected_ex_path


def _assert_files_correctly_produced(produced_path, should_be_path):
    assert produced_path == should_be_path
    posix_path = Path(produced_path)
    meta_path = posix_path.parent / f".{posix_path.name}.yml"
    assert meta_path.exists(), f"No metadata with path {meta_path}"


def test_export_w_meta(tmp_path):
    """Test function export_w_meta

    Args:
        tmp_path (PosixPath): place to store results of test
    """

    obs_path = TEST_DATA / "../ert-doc.yml"
    with open(obs_path, "r", encoding="utf-8") as stream:
        observations = yaml.safe_load(stream)
    print(observations)

    project_path, case_path, expected_ex_path = _setup_ert_run_setting(tmp_path)
    os.chdir(tmp_path)
    assert len(observations) > 0
    ex_path = export_w_meta(
        observations, project_path / RELATIVE_PATH_TO_CONFIG, case_path
    )
    _assert_files_correctly_produced(ex_path, expected_ex_path)


# def test_parsing_of_args():
#     parser = get_parser()
#     args = parser.parse_args()
#     print(vars(args))
#     print(args.ert_case_path)
#     print(args.fmu_config_file)


@pytest.mark.parametrize(
    "export_control, file_ending, export_folder",
    [("--yml", "json", "dictionaries"), ("--csv", "csv", "tables")],
)
def test_command_line(tmp_path, mocker, export_control, file_ending, export_folder):
    """Test export with metadata with command line tool

    Args:
        tmp_path (PosixPath): where to run test
        mocker (pytest.fixture): fixture for mocking command line run
    """
    project_path, case_path, expected_path = _setup_ert_run_setting(
        tmp_path, file_ending, export_folder
    )

    ert_config_path = project_path / "ert/model"
    ert_config_path.mkdir(parents=True)

    os.chdir(ert_config_path)
    mocker.patch(
        "sys.argv",
        [
            "fmuobs",
            str(TEST_DATA / "../ert-doc.obs"),
            "--ert_case_path",
            str(case_path),
            export_control,
            "observations",
        ],
    )
    main()
    exports = list(case_path.glob("share/results/**/*.*"))
    assert len(exports) == 4, f"there where {len(exports)} produced, not 4"
    ex_paths = str(
        [file_path for file_path in exports if not file_path.name.startswith(".")]
    )
    for ex_path in ex_paths:
        _assert_files_correctly_produced(ex_path, expected_path)
