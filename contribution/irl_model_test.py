import multiprocessing

import pandas as pd

from external import Variational_Generator
from gemini.actors import SimulationLink, SimulationRecorder
from gemini.dataset import TrajectoryDatabase
from gemini.resources import get_path_data_file, get_scenario_path
from gemini.scenario import ScenarioModelGenerator
from gemini.simulator.esmini import run_scenario

input_size = 18
hidden_layers = [18, 18, 16, 16, 14, 14, 12, 12, 12]
output_size = 5  # 5 (actions in the form of mu_x, mu_y, sigma_x, sigma_y, and ρ (correlation factor)
generator = Variational_Generator(input_size, hidden_layers, output_size)

tracks = pd.read_csv(get_path_data_file('corrected_tracks.csv'))
db = TrajectoryDatabase(tracks)
target, interactions = db.get_scenario_objects(6)

scenario_model_generator = ScenarioModelGenerator(target, [interactions[2]])
scenario = scenario_model_generator.build_scenario()
scenario.write_xml(get_scenario_path('try.xosc'))
proc = multiprocessing.Process(target=run_scenario, args=('try.xosc',))
proc.start()
recorder = SimulationRecorder()
# actors = scenario_model_generator.get_actors_with_model(model_logic=VariationalGeneratorLogic(generator, 0.05))
actors = scenario_model_generator.get_agents()
simulation = SimulationLink(actors=actors + [recorder])
simulation.live(time_step=0.05, max_time=scenario_model_generator.get_time())
recorder.get_simulation_trajectory().plot_dynamics()
proc.terminate()
