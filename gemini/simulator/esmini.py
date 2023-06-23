import os
from ctypes import *

from dotenv import load_dotenv

from gemini import resources

load_dotenv()


class EsminiSimulator:

    def __init__(self, esmini_library) -> None:
        self.scenario_engine = esmini_library

    def scenario_engine_initialization(self, scenario_path, enable_controls=False):
        disable_ctrls = int(not enable_controls)
        self.scenario_engine.SE_Init(bytes(scenario_path, 'utf-8'), disable_ctrls, 1, 0, 0)

    def step(self, dt=None):
        if not dt:
            self.scenario_engine.SE_Step()
        else:
            self.scenario_engine.SE_StepDT(c_float(dt))

    def open_osi_socket(self, ip_address):
        return self.scenario_engine.SE_OpenOSISocket(ip_address)


class EsminiSimulatorFactory:

    @staticmethod
    def create():
        esmini_lib = CDLL(os.getenv('ESMINI_LIB_PATH'))
        return EsminiSimulator(esmini_lib)


def run_scenario(scenario_name):
    resources.change_dir_to_scenario_folder()
    scenario_path = resources.get_scenario_path(scenario_name)
    se = EsminiSimulatorFactory.create()
    se.scenario_engine_initialization(scenario_path, enable_controls=True)
    osi_socker_correct = se.open_osi_socket("127.0.0.1")
    print("osi correct", osi_socker_correct)
    while True:
        se.step()
