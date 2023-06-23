import multiprocessing
import time

from external import UdpSender
from gemini.action_logic import ActionLogic
from gemini.actors import SimulationLink, Agent, AgentConnector, UdpSenderXYH, SimulationRecorder
from gemini.common import VehicleState, Point2d, VehicleTrajectory
from gemini.resources import get_scenario_path
from gemini.scenario import ScenarioModelGenerator, ScenarioModelObject
from gemini.simulator.esmini import run_scenario


# New Logic that simply
class ConstantVelocityLogic(ActionLogic):

    def __init__(self, velocity: Point2d) -> None:
        self.velocity = velocity

    def act(self, ground_truth_info, agent_id: int) -> VehicleState:
        agent_vehicle = ground_truth_info.get_vehicle_state(agent_id)  # query for actual vehicle state
        # time.sleep(0.1)
        return VehicleState(agent_vehicle.position,
                            self.velocity)  # keep position and change actual velocity  to constant velocity


trajectory = VehicleTrajectory([0], [VehicleState(velocity=Point2d(1, 1))])

agent = Agent(action_logic=ConstantVelocityLogic(Point2d(1, 1)),
              agent_connector=AgentConnector(
                  agent_id=0,
                  osi_channel=UdpSenderXYH(UdpSender(port=53901))))

scenario_model_generator = ScenarioModelGenerator(ScenarioModelObject(0, "line_trajectory", trajectory, 53901))
scenario = scenario_model_generator.build_scenario()
scenario.write_xml(get_scenario_path('try.xosc'))

proc = multiprocessing.Process(target=run_scenario, args=('try.xosc',))
proc.start()

recorder = SimulationRecorder()

simulation = SimulationLink(actors=(agent, recorder))
simulation.live(time_step=0.03, max_time=5)
proc.terminate()
recorder.get_simulation_trajectory().plot_dynamics()
