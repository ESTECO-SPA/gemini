from threading import Thread

from gemini.actors import SimulationLink
from gemini.common import VehicleState, Point2d, VehicleTrajectory
from gemini.resources import get_scenario_path
from gemini.scenario import ScenarioModelGenerator, ScenarioModelObject
from gemini.simulator.esmini import run_scenario


def generate_trajectory():
    return VehicleTrajectory([0, 5, 10],
                             [VehicleState(velocity=Point2d(10, 10)),
                              VehicleState(position=Point2d(50, 50), velocity=Point2d(-10, 20)),
                              VehicleState(position=Point2d(0, 150), velocity=Point2d(0, 0))])


trajectory = generate_trajectory()
scenario_model_generator = ScenarioModelGenerator(ScenarioModelObject(0, "line_trajectory", trajectory, 53901))
scenario = scenario_model_generator.build_scenario()
scenario.write_xml(get_scenario_path('try.xosc'))

new_thread = Thread(target=run_scenario, args=('try.xosc',))
new_thread.start()

actors = scenario_model_generator.get_agents()

simulation = SimulationLink(actors=actors)
simulation.live()
