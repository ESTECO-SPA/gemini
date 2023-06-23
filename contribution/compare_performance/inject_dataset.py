import multiprocessing
import pickle

import pandas as pd

from gemini.actors import SimulationLink, SimulationRecorder
from gemini.dataset import TrajectoryDatabase
from gemini.resources import get_path_data_file, get_scenario_path
from gemini.scenario import ScenarioModelGenerator
from gemini.simulator.esmini import run_scenario

# HOW TO INJECT DATASET TRAJECTORIES INTO SIMULATION
# TBN: please configure the env variables in the .env file as reported in the README.md file.
# The gemini.resources functions use these env variables.

# 1) LOAD THE ORIGINAL DATASET
tracks = pd.read_csv(get_path_data_file('corrected_tracks.csv'))
db = TrajectoryDatabase(tracks)
target, interactions = db.get_scenario_objects(trajectory_id=5)

# 2) WRITE THE OPEN SCENARIO FILE BASED ON THE TARGET AND OBSTACLES TRAJECTORIES
scenario_model_generator = ScenarioModelGenerator(target, interactions)
scenario = scenario_model_generator.build_scenario()
scenario.write_xml(get_scenario_path('try.xosc'))

# 3) START THE SIMULATION OF THE OPEN SCENARIO FILE CREATED AT STEP 3
proc = multiprocessing.Process(target=run_scenario, args=('try.xosc',))
proc.start()

# 4) DEFINE THE ACTORS THAT WILL INTERACT WITH THE SIMULATION
# SimulationRecorder is an actor that save the vehicle states during the simulation
recorder = SimulationRecorder()
# The following actors are mimic the original dataset
actors = scenario_model_generator.get_agents()

# 5) START THE COMMUNICATION WITH THE SIMULATOR TROUGH OSIReceiver and UdpSender.
simulation = SimulationLink(actors=actors + [recorder])
simulation.live(time_step=0.05, max_time=scenario_model_generator.get_time())

# 6) TERMINATE SIMULATION
proc.terminate()

# 7) STORE THE TRAJECTORY
# recorder is used to retrieve the vehicle dynamics
# used in analysis.ipynb
trajectory = recorder.get_simulation_trajectory()
with open(get_path_data_file("dataset_trajectory.pickle"), "wb") as file:
    trajectory.store_dict(file)

# used in performance_analysis.py
with open(get_path_data_file("dataset_trajectory_object.pickle"), "wb") as file:
    pickle.dump(trajectory, file)

