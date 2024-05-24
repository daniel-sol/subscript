import os
import logging
import re
from datetime import datetime
import pandas as pd
from pathlib import Path, PosixPath
from shutil import rmtree
from fmu.dataio import ExportData
from subscript.genertobs_unstable._utilities import check_and_fix_str
import pyarrow as pa


def add_time_stamp(string="", record_type="f", comment_mark="--"):
    """Add commented line with user and timestamp

    Args:
        string (str): the string to stamp
        record_type (str, optional): specifies if it is file or folder. Defaults to "f".

    Returns:
        _type_: _description_
    """
    ctime = datetime.now().strftime("%Y-%m-%d:%H:%M:%S")
    user = os.getlogin()
    if record_type == "f":
        type_str = "file"
    else:
        type_str = "folder"

    time_stamped = f"{comment_mark}This {type_str} is autogenerated by {user} running genertobs_unstable at {ctime}\n"
    time_stamped += f"{comment_mark} DO NOT EDIT THIS FILE MANUALLY!\n"

    time_stamped += string
    return time_stamped


def write_csv_with_comment(file_path, frame):
    """Write to csv file with timestamped header

    Args:
        file_path (str): path to file
        frame (pd.DataFrame): the dataframe to write
    """

    with open(file_path, "w", encoding="utf-8") as stream:
        stream.write(add_time_stamp(comment_mark="#"))
        frame.to_csv(stream, index=False, header=False, sep=" ")


def write_timeseries_ertobs(obs_dict: dict):
    """Make ertobs string to from dictionary

    Args:
        obs_dict (dict): the dictionary to extract from

    Returns:
        str: string to write into ertobs file
    """
    logger = logging.getLogger(__name__ + ".write_timeseries_ertobs")
    logger.debug("%s observations to write", obs_dict)
    obs_frames = []
    for element in obs_dict:
        logger.debug("Element to extract from %s", element)
        key = element["vector"]
        logger.debug(key)
        obs_frame = element["data"]
        obs_frame["class"] = "SUMMARY_OBSERVATION"
        obs_frame["key"] = f"KEY={key}" + ";};"
        order = ["class", "label", "value", "error", "date", "key"]
        obs_frame = obs_frame[order]
        obs_frame["value"] = "{VALUE=" + obs_frame["value"].astype(str) + ";"
        obs_frame["error"] = "ERROR=" + obs_frame["error"].astype(str) + ";"
        obs_frame["date"] = "DATE=" + obs_frame["date"].astype(str) + ";"
        obs_frames.append(obs_frame)
    obs_frames = pd.concat(obs_frames)
    obs_str = re.sub(r" +", " ", obs_frames.to_string(header=False, index=False)) + "\n"
    logger.debug("Returning %s", obs_str)
    return obs_str


def select_from_dict(keys: list, full_dict: dict):
    """Select some keys from a bigger dictionary

    Args:
        keys (list): the keys to select
        full_dict (dict): the dictionary to extract from

    Returns:
        dict: the subselection of dict
    """
    return {key: full_dict[key] for key in keys}


def create_rft_ertobs_str(well_name: str, restart: int, obs_file: PosixPath) -> str:
    """Create the rft ertobs string for specific well

    Args:
        well_name (str): well name
        restart (str): restart number
        obs_file (str): name file with corresponding well observations

    Returns:
        str: the string
    """
    return (
        f"GENERAL_OBSERVATION {well_name}_OBS "
        + "{"
        + f"DATA={well_name}_SIM ;"
        + f" RESTART = {restart}; "
        + f"OBS_FILE = {obs_file}"
        + ";};\n"
    )


def create_rft_gendata_str(well_name: str, restart: int) -> str:
    """Create the string to write as gendata call

    Args:
        well_name (str): well name
        restart (str): restart number

    Returns:
        str: the string
    """
    return (
        f"GEN_DATA {well_name}_SIM "
        + f"RESULT_FILE:RFT_{well_name}_%d "
        + f"REPORT_STEPS:{restart}\n"
    )


def write_genrft_str(
    parent: PosixPath, well_date_path: str, layer_zone_table: str
) -> str:
    """write the string to define the GENDATA_RFT call

    Args:
        parent (str): path where rfts are stored
        well_date_path (str): path where the well, date, and restart number are written
        layer_zone_table (str): path to where the zones and corresponding layers are stored

    Returns:
        str: the string
    """
    str_parent = str(parent)
    string = (
        f"DEFINE <RFT_INPUT> {parent}\n"
        + "FORWARD_MODEL MAKE_DIRECTORY(<DIRECTORY>=gendata_rft)\n"
        + "FORWARD_MODEL GENDATA_RFT(<PATH_TO_TRAJECTORY_FILES>=<RFT_INPUT>,"
        + f"<WELL_AND_TIME_FILE>=<RFT_INPUT>/{str(well_date_path).replace(str_parent, '')},"
        + f"<ZONEMAP>=<RFT_INPUT>/{str(layer_zone_table).replace(str_parent, '')},"
        + " <OUTPUTDIRECTORY>=gendata_rft)\n\n"
    )
    return string


def write_rft_ertobs(rft_dict: dict, parent_folder: PosixPath) -> str:
    """Write all rft files for rft dictionary, pluss info str

    Args:
        rft_dict (dict): the rft information
        parent_folder (str, optional): path to parent folder to write to. Defaults to "".

    Returns:
        str: ertobs strings for rfts
    """
    logger = logging.getLogger(__name__ + ".write_rft_ertobs")
    rft_folder = Path(parent_folder) / "rft"
    rft_folder.mkdir(exist_ok=True)
    logger.debug("%s observations to write", rft_dict)
    well_date_list = []
    rft_ertobs_str = ""
    gen_data = ""
    prefix = make_rft_prefix(rft_dict)

    logger.debug("prefix is %s", prefix)
    for element in rft_dict["observations"]:
        well_name = element["well_name"]
        logger.debug(well_name)
        date = element["date"]
        restart = element["restart"]
        obs_file = write_well_rft_files(rft_folder, prefix, element)
        well_date_list.append([well_name, date, restart])
        rft_ertobs_str += create_rft_ertobs_str(well_name, restart, obs_file)
        gen_data += create_rft_gendata_str(well_name, restart)

    well_date_frame = pd.DataFrame(
        well_date_list, columns=["well_name", "date", "restart"]
    )

    well_date_file = rft_folder / "well_date_restart.txt"
    write_csv_with_comment(well_date_file, well_date_frame)
    logger.debug("Written %s", str(well_date_file))
    gen_data_file = parent_folder / "gendata_include.ert"
    gen_data = (
        write_genrft_str(
            rft_folder, str(well_date_file), rft_dict["plugin_arguments"]["zonemap"]
        )
        + gen_data
    )

    gen_data_file.write_text(add_time_stamp(gen_data))
    logger.debug("Written %s", str(gen_data_file))

    return rft_ertobs_str


def make_rft_prefix(indict: dict) -> str:
    """Derive prefix for rft data from dict with metadata

    Args:
        indict (dict): the metadata to use

    Returns:
        str: the prefix derived
    """
    logger = logging.getLogger(__name__ + ".make_rft_prefix")
    try:
        metadata = indict["metadata"]
    except KeyError:
        logger.warning("No metadata for %s", indict["name"])
        metadata = {}
    columns = metadata.get("columns", {"value": {"unit": "bar"}})
    rft_format = columns["value"]["unit"]
    valid_sat_format = ["fraction", "saturation"]
    logger.debug("Rft format is : %s", rft_format)
    if rft_format in valid_sat_format:
        prefix = "saturation_"
    else:
        prefix = "pressure_"
    return prefix


def write_well_rft_files(
    parent_folder: PosixPath, prefix: str, element: dict
) -> PosixPath:
    """Write rft files for rft element for one well

    Args:
        parent_folder (str): parent to write all files to
        prefix (str): prefix defining if it is pressure or saturation
        element (dict): the info about the element

    Returns:
        str: ertobs string for well
    """
    logger = logging.getLogger(__name__ + ".write_well_rft_files")
    fixed_file_name = check_and_fix_str(element["well_name"])
    obs_file = parent_folder / f"{prefix}{fixed_file_name}.obs"
    position_file = parent_folder / f"{prefix}{fixed_file_name}.txt"
    logger.debug("Writing %s and %s", obs_file, position_file)
    obs_frame = element["data"][["value", "error"]]
    logger.debug("observations\n%s", obs_frame)
    write_csv_with_comment(obs_file, obs_frame)
    position_frame = element["data"][["x", "y", "md", "tvd", "zone"]]
    logger.debug("positions for\n%s", position_frame)
    write_csv_with_comment(position_file, position_frame)

    return obs_file


def write_dict_to_ertobs(obs_list: list, parent: PosixPath) -> str:
    """Write all observation data for ert

    Args:
        obs_list (list): the list of all observations
        parent (str, optional): location to write to. Defaults to "".

    Returns:
        str: parent folder for all written info
    """
    logger = logging.getLogger(__name__ + ".write_dict_to_ertobs")
    logger.debug("%s observations to write", len(obs_list))
    if parent.exists():
        logger.warning("%s exists, deleting and overwriting contents", str(parent))
        rmtree(parent)
    parent.mkdir()
    obs_str = add_time_stamp()
    readme_file = parent / "readme.txt"
    readme_file.write_text(add_time_stamp(record_type="d"))
    for obs in obs_list:
        logger.debug(obs)
        content = obs["content"]
        obs_str += f"--\n--{obs['name']}\n"
        if content == "timeseries":
            obs_str += write_timeseries_ertobs(obs["observations"])

        elif content == "rft":
            obs_str += write_rft_ertobs(obs, parent)
        else:
            logger.warning(
                "Currently not supporting other formats than timeseries and rft"
            )
    ertobs_file = parent / "ert_observations.obs"
    ertobs_file.write_text(obs_str)

    return obs_str


def export_with_dataio(data: list, config: dict, store_path: str):
    """Export observations from list of input dicts

    Args:
        data (list): the data stored as dict
        config (dict): config file needed for dataio
        store_path (str): path to where to store
    """
    logger = logging.getLogger(__name__ + ".export_with_dataio")
    logger.info("Will be exporting %i elements from dict %s", len(data), data)
    Path(store_path).mkdir(parents=True, exist_ok=True)
    cwd = Path().cwd()
    os.chdir(store_path)
    exporter = ExportData(config=config)
    logger.info("Results will be stored in %s", store_path)
    for data_element in data:
        logger.debug("Exporting element %s\n------", data_element["name"])
        content = data_element["content"]
        if content == "rft":
            prefix = make_rft_prefix(data_element)
        else:
            prefix = ""
        logger.debug("Obs are:\n %s", data_element["observations"])
        for observation in data_element["observations"]:
            logger.debug("-->Data are \n%s", observation["data"])
            try:
                name = observation["vector"].replace(":", "_")
            except KeyError:
                name = observation["well_name"]
            obs_data = pa.Table.from_pandas(observation["data"])
            logger.debug("Observations to export %s", obs_data)
            export_path = exporter.export(
                obs_data,
                name=prefix + check_and_fix_str(name),
                tagname=content,
                casepath=store_path,
                fmu_context="preprocessed",
                content=content,
                is_observation=True,
            )
            logger.info("Exporting to %s", export_path)
    parent = Path(export_path).parent
    logger.info("All exported to %s", parent)
    return parent


def generate_preprocessed_hook(export_path, output_folder):

    stem = "upload_observations"

    posixpath = Path(output_folder).resolve()
    workflow_name = posixpath / f"xhook_{stem}"
    call = f"WF_UPLOAD_SUMO_OBS <SCRATCH>/<USER>/<CASE_DIR> {str(export_path)} '--env' <SUMO_ENV>"
    workflow_name.write_text(add_time_stamp(call))

    workflow_content = f"LOAD_WORKFLOW   {workflow_name}  -- define and load workflow\n"
    workflow_content += f"HOOK_WORKFLOW {workflow_name.name}  PRE_SIMULATION"
    include_file = posixpath / f"xhook_{stem}.ert"
    include_file.write_text(add_time_stamp(workflow_content))
