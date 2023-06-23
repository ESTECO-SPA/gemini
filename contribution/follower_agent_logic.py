from threading import Thread

from external import UdpSender
from gemini.action_logic import FollowerAgentLogic
from gemini.actors import UdpSenderXYH, Agent, AgentConnector, SimulationLink, SimulationRecorder
from gemini.simulator.esmini import run_scenario

new_thread = Thread(target=run_scenario, args=('controlled_two_cars_in_open_space.xosc',))
new_thread.start()

follower_agent_channel = UdpSenderXYH(UdpSender(port=53901))
target_agent_channel = UdpSenderXYH(UdpSender(port=53900))

follower_agent_connector = AgentConnector(agent_id=0, osi_channel=follower_agent_channel)
followed_agent_connector = AgentConnector(agent_id=1, osi_channel=target_agent_channel)
follower_agent = Agent(action_logic=FollowerAgentLogic(waiting_update=250),
                       agent_connector=follower_agent_connector)

recorder = SimulationRecorder()

simulation = SimulationLink(actors=(follower_agent, recorder))
simulation.live(time_step=0.001, max_time=20)
recorder.get_simulation_trajectory().plot_dynamics()
