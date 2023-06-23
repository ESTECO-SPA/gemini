import os

from dotenv import load_dotenv

load_dotenv()


def get_path_data_file(file_name: str):
    return os.getenv('DATA_PATH') + os.sep + file_name


def change_dir_to_scenario_folder():
    os.chdir(get_resources("xosc"))


def get_scenario_path(scenario_file_name: str):
    return get_resources("xosc", scenario_file_name)


def get_resources(*path_from_resource: str):
    return os.getenv('ESMINI_RESOURCES_FOLDER') + os.sep + str(os.sep).join(path_from_resource)
