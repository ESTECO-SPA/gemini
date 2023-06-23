from threading import Thread

from gemini.simulator.esmini import run_scenario
from external import UdpSender
from gemini.actors import AgentConnector, Agent, SimulationLink, SimulationRecorder, UdpSenderXYH
from gemini.action_logic import InertialMovementLogic
from gemini.common import TimedVehicleState, VehicleState, Point2d

new_thread = Thread(target=run_scenario, args=('inertial.xosc',))
new_thread.start()

real_agent = Agent(
    action_logic=InertialMovementLogic(
        TimedVehicleState(0, VehicleState(Point2d(0, 0), Point2d(10, 0), Point2d(0, 3)))),
    agent_connector=AgentConnector(agent_id=1, osi_channel=UdpSenderXYH(UdpSender(port=53901))))
obstacle_agent = Agent(
    action_logic=InertialMovementLogic(TimedVehicleState(0, VehicleState(Point2d(0, 0), Point2d(2, 2), Point2d(3, 3)))),
    agent_connector=AgentConnector(agent_id=0, osi_channel=UdpSenderXYH(UdpSender(port=53902))))

recorder = SimulationRecorder()
repulsing_car_agent = SimulationLink(actors=(real_agent, obstacle_agent, recorder))
repulsing_car_agent.live(max_time=10)
recorder.get_simulation_trajectory().plot_dynamics()
