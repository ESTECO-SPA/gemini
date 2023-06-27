import multiprocessing
import pickle

import pandas as pd

from external import VariationalGenerator
from gemini.action_logic import VariationalGeneratorLogic
from gemini.actors import SimulationLink, SimulationRecorder
from gemini.dataset import TrajectoryDatabase
from gemini.resources import get_path_data_file, get_scenario_path
from gemini.scenario import ScenarioModelGenerator
from gemini.simulator.esmini import run_scenario

# HOW TO INJECT IRL MODEL INTO SIMULATION
# TBN: please configure the env variables in the .env file as reported in the README.md file.
# The gemini.resources functions use these env variables.

# 1) LOAD THE IRL MODEL
input_size = 18
hidden_layers = [18, 18, 16, 16, 14, 14, 12, 12, 12]
output_size = 5  # 5 (actions in the form of mu_x, mu_y, sigma_x, sigma_y, and ρ (correlation factor)
generator = VariationalGenerator(input_size, hidden_layers, output_size)

# 2) LOAD THE ORIGINAL DATASET
tracks = pd.read_csv(get_path_data_file('corrected_tracks.csv'))
db = TrajectoryDatabase(tracks)
target, obstacles = db.get_scenario_objects(trajectory_id=5)

# 3) WRITE THE OPEN SCENARIO FILE BASED ON THE TARGET AND OBSTACLES TRAJECTORIES
scenario_model_generator = ScenarioModelGenerator(target, obstacles)
scenario = scenario_model_generator.build_scenario()  # build the parking_lot open scenario
scenario.write_xml(get_scenario_path('try.xosc'))

# 4) START THE SIMULATION OF THE OPEN SCENARIO FILE CREATED AT STEP 3
proc = multiprocessing.Process(target=run_scenario, args=('try.xosc',))
proc.start()

# 5) DEFINE THE ACTORS THAT WILL INTERACT WITH THE SIMULATION
# SimulationRecorder is an actor that save the vehicle states during the simulation
recorder = SimulationRecorder()
# The following actors are composed by:
# - the IRL actor created at step 1 (object: generator)
# - all the vehicle obstacles extracted by the original dataset
data = dict()
logic = VariationalGeneratorLogic(generator, 0.05, data)
agents = scenario_model_generator.get_agent_with_model(model_logic=logic)

# 6) START THE COMMUNICATION WITH THE SIMULATOR TROUGH OSIReceiver and UdpSender.
simulation = SimulationLink(actors=agents + [recorder])
simulation.live(time_step=0.05, max_time=scenario_model_generator.get_time())

# 7) TERMINATE SIMULATION
proc.terminate()

# 8) STORE THE TRAJECTORY
# SimulationRecorder is used to retrieve the vehicle dynamics
trajectory = recorder.get_simulation_trajectory()

# DATA ANALYSIS
# trajectory.plot_dynamics()
# trajectory.plot_position()

# 7) STORE THE TRAJECTORY
# SimulationRecorder is used to retrieve the vehicle dynamics

# used in analysis.ipynb
with open(get_path_data_file("irl_trajectory.pickle"), "wb") as file:
    trajectory.store_dict(file)

# used in performance_analysis.py
with open(get_path_data_file("irl_trajectory_object.pickle"), "wb") as file:
    pickle.dump(trajectory, file)

# storage of data (visitor)
# used in analysis.ipynb
with open(get_path_data_file("irl_perception_data.pickle"), "wb") as file:
    pickle.dump([data['time'], data['state'], data['torch_state'], data['action'], data['id']], file)
