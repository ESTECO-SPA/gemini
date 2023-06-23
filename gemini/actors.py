import struct
from typing import Tuple

from external import OSIReceiver, UdpSender, input_modes
from gemini.action_logic import ActionLogic
from gemini.common import VehicleState
from gemini.connector.osi_connector import TimedOSIReceiver, GroundTruthInfo
from gemini.simulation import SimulationTrajectory


class UdpSenderXYH:

    def __init__(self, udp_sender: UdpSender) -> None:
        self.udp_sender = udp_sender

    def send_position_state(self, vehicle_id: int, vehicle_state: VehicleState) -> None:
        self.udp_sender.send(
            struct.pack(
                'iiiidddddB',
                1,  # version
                input_modes['stateXYH'],
                vehicle_id,  # object ID
                0,  # frame nr
                vehicle_state.position.x,  # x
                vehicle_state.position.y,  # y
                vehicle_state.heading,  # h
                vehicle_state.speed(),  # speed
                0.0,  # steering angle
                1,  # dead reckoning
            )
        )


class AgentConnector:

    def __init__(self, agent_id: int, osi_channel: UdpSenderXYH) -> None:
        self.agent_id = agent_id
        self.osi_sender = osi_channel

    def send_position_state(self, vehicle_state: VehicleState):
        self.osi_sender.send_position_state(self.agent_id, vehicle_state)

    def get_agent_id(self):
        return self.agent_id


class Actor:
    def act(self, ground_truth_info: GroundTruthInfo) -> None:
        pass


class Agent(Actor):
    def __init__(self, action_logic: ActionLogic, agent_connector: AgentConnector) -> None:
        self.action_logic = action_logic
        self.agent_connector = agent_connector

    def act(self, ground_truth_info: GroundTruthInfo) -> None:
        new_vehicle_state = self.action_logic.act(ground_truth_info, self.agent_connector.get_agent_id())
        print("SIMULATION TIME: ", ground_truth_info.get_simulation_time())
        print("SEND STATE:", new_vehicle_state)
        if new_vehicle_state:
            self.agent_connector.send_position_state(new_vehicle_state)


class SimulationRecorder(Actor):
    """
    It is an Actor which record the simulation trajectory of each agent
    """

    def __init__(self) -> None:
        self.simulation_trajectory = SimulationTrajectory()

    def act(self, ground_truth_info: GroundTruthInfo) -> None:
        simulation_state = ground_truth_info.get_simulation_state()
        self.simulation_trajectory.add_state(simulation_state)

    def get_simulation_trajectory(self) -> SimulationTrajectory:
        return self.simulation_trajectory


class SimulationLink:
    """
    Create an object which is in charge of manage communication with ESMINI simulator
    """

    def __init__(self, actors: Tuple[Actor, ...]) -> None:
        self.actors = actors
        self.timed_osi_receiver = TimedOSIReceiver(OSIReceiver())

    def live(self, time_step: float = None, max_time: float = float('Inf')) -> None:
        """
        :param time_step: time_step used to get information from the OSIReceiver
        :param max_time: maximum time allowed for simulation
        :return: None
        """
        time = - float('Inf')
        while self.timed_osi_receiver.is_open() and time < max_time:
            ground_truth_info = self.timed_osi_receiver.receive(time_step)
            time = ground_truth_info.get_simulation_time()
            for actor in self.actors:
                actor.act(ground_truth_info)
