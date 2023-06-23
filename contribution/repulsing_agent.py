from threading import Thread

from gemini.simulator.esmini import run_scenario
from external import UdpSender
from gemini.actors import UdpSenderXYH, SimulationLink, AgentConnector, Agent, \
    SimulationRecorder
from gemini.action_logic import RepulsingProximityLogic

new_thread = Thread(target=run_scenario, args=('controlled_two_cars_in_open_space.xosc',))
new_thread.start()

agent_connector = AgentConnector(agent_id=1, osi_channel=UdpSenderXYH(UdpSender(port=53901)))
agent_logic = RepulsingProximityLogic(radius=8.0, repulsing_factor=1.0)
recorder = SimulationRecorder()
repulsing_car_agent = SimulationLink(actors=(Agent(agent_logic, agent_connector), recorder))
repulsing_car_agent.live(time_step=0.01, max_time=10)
recorder.get_simulation_trajectory().plot_dynamics()
