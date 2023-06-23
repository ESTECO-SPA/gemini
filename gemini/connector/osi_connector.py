from typing import List, Tuple

import numpy as np

from external import OSIReceiver
from gemini.common import VehicleState, Point2d


def osi_time_calculator(seconds, nanos):
    return seconds + nanos / 1E9


class GroundTruthInfo:

    def __init__(self, ground_truth) -> None:
        self.ground_truth = ground_truth

    def get_simulation_time(self) -> float:
        return osi_time_calculator(self.ground_truth.timestamp.seconds, self.ground_truth.timestamp.nanos)

    def get_vehicle_state(self, agent_id: int) -> VehicleState:
        agent_info = next(
            filter(lambda moving_object: moving_object.id.value == agent_id, self.ground_truth.moving_object))
        return self.__get_vehicle_state(agent_info)

    @staticmethod
    def __get_vehicle_state(agent_info) -> VehicleState:
        position = Point2d(agent_info.base.position.x, agent_info.base.position.y)
        velocity = Point2d(agent_info.base.velocity.x, agent_info.base.velocity.y)
        acceleration = Point2d(agent_info.base.acceleration.x, agent_info.base.acceleration.y)
        heading = agent_info.base.orientation.yaw
        return VehicleState(position, velocity, acceleration, heading, agent_info.id.value)

    def get_vehicle_states(self) -> List[VehicleState]:
        return [self.__get_vehicle_state(agent) for agent in self.ground_truth.moving_object]

    def get_simulation_state(self) -> Tuple[float, List[VehicleState]]:
        return self.get_simulation_time(), [self.__get_vehicle_state(agent) for agent in
                                            self.ground_truth.moving_object]


class TimedOSIReceiver:
    """
    Wrapper of OSIReceiver which is able to receive information with a fixed time step
    (see receive(self, time_step=None))
    """

    def __init__(self, osi_receiver: OSIReceiver) -> None:
        self.osi_receiver = osi_receiver
        self.current_timed_ground_truth = None
        self.open = True

    def receive(self, time_step=None) -> GroundTruthInfo:
        if time_step:
            return self.__receive_after(time_step)
        else:
            return self.__receive_now()

    def __receive_after(self, time_step: float) -> GroundTruthInfo:
        starting_timed_ground_truth = self.__get_starting_timed_ground_truth()
        self.current_timed_ground_truth = self.__get_next_timed_ground_truth(starting_timed_ground_truth,
                                                                             time_step)
        return GroundTruthInfo(self.current_timed_ground_truth.ground_truth)

    def __get_starting_timed_ground_truth(self) -> GroundTruthInfo:
        if not self.current_timed_ground_truth:
            starting_timed_ground_truth = self.__receive_now()
        else:
            starting_timed_ground_truth = self.current_timed_ground_truth
        return starting_timed_ground_truth

    def __get_next_timed_ground_truth(self, starting_timed_ground_truth: GroundTruthInfo, time_step: float):
        while True:
            next_timed_ground_truth = self.__receive_now()
            if next_timed_ground_truth.get_simulation_time() - starting_timed_ground_truth.get_simulation_time() >= time_step:
                break
        return next_timed_ground_truth

    def __receive_now(self) -> GroundTruthInfo:
        ground_truth = self.osi_receiver.receive()
        return GroundTruthInfo(ground_truth)

    def close(self) -> None:
        self.osi_receiver.close()
        self.current_timed_ground_truth = None
        self.open = False

    def is_open(self) -> bool:
        return self.open


class NearVehicles:
    def __init__(self, ground_truth_info: GroundTruthInfo) -> None:
        self.ground_truth_info = ground_truth_info

    def get_vehicles_near_to(self, target_vehicle: VehicleState, number_of_vehicles: int = 1) -> List:
        if self.ground_truth_info.get_vehicle_states():
            return self.__get_vehicle_near_to(target_vehicle, number_of_vehicles)
        else:
            raise ValueError("There are no other vehicles")

    def __get_vehicle_near_to(self, target_vehicle: VehicleState, number_of_requested_vehicles: int) -> List:
        other_vehicle_states = self.__get_other_vehicles(target_vehicle)
        vehicle_distances = [target_vehicle.position_distance(vehicle) for vehicle in other_vehicle_states]
        ordered_indexes = np.argsort(vehicle_distances)
        number_other_vehicles = len(other_vehicle_states)
        return [other_vehicle_states[index] for index in
                ordered_indexes[:min(number_other_vehicles, number_of_requested_vehicles)]]

    def __get_other_vehicles(self, target_vehicle):
        vehicle_states = self.ground_truth_info.get_vehicle_states()
        if target_vehicle in vehicle_states:
            vehicle_states.remove(target_vehicle)
        return vehicle_states
