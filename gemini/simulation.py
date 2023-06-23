import pickle
from typing import List, Tuple

import matplotlib.pyplot as plt

from gemini.common import VehicleTrajectory, VehicleState


class SimulationTrajectory:

    def __init__(self) -> None:
        self.storage = dict()
        self.time = []

    def add_state(self, time_and_vehicle_states: Tuple[float, List[VehicleState]]) -> None:
        time, vehicle_states = time_and_vehicle_states
        self.time.append(time)
        for vehicle_state in vehicle_states:
            vehicle_state_id = vehicle_state.get_id()
            if vehicle_state_id in self.storage:
                self.storage[vehicle_state_id].append(vehicle_state)
            else:
                self.storage[vehicle_state_id] = [vehicle_state]

    def store(self, file_path: str) -> None:
        with open(file_path, 'wb') as file:
            pickle.dump(self, file)

    def store_dict(self, file) -> None:
        storage_dict = {'time': self.time}
        for key, value in self.storage.items():
            storage_dict[key] = [v.to_list() for v in value]
        pickle.dump(storage_dict, file)

    def get_trajectory(self, agent_id) -> VehicleTrajectory:
        return VehicleTrajectory(self.time, self.storage[agent_id])

    def plot_position(self) -> None:
        from gemini.dataset import PlotFiskhamnsmotet
        plot = PlotFiskhamnsmotet()
        for agent_id, agent_states in self.storage.items():
            x = [agent_state.position.x for agent_state in agent_states]
            y = [agent_state.position.y for agent_state in agent_states]
            plot.add(f"agent id: {agent_id}", x, y)
        plot.plot()

    def plot_dynamics(self) -> None:
        fig, axs = plt.subplots(6, 1, sharex='all')
        for agent_id, agent_states in self.storage.items():
            x = [agent_state.position.x for agent_state in agent_states]
            y = [agent_state.position.y for agent_state in agent_states]
            dx = [agent_state.velocity.x for agent_state in agent_states]
            dy = [agent_state.velocity.y for agent_state in agent_states]
            ddx = [agent_state.acceleration.x for agent_state in agent_states]
            ddy = [agent_state.acceleration.y for agent_state in agent_states]
            self.__plot(self.time, x, agent_id, 'Position X', axs[0])
            self.__plot(self.time, y, agent_id, 'Position Y', axs[1])
            self.__plot(self.time, dx, agent_id, 'Velocity X', axs[2])
            self.__plot(self.time, dy, agent_id, 'Velocity Y', axs[3])
            self.__plot(self.time, ddx, agent_id, 'Acceleration X', axs[4])
            self.__plot(self.time, ddy, agent_id, 'Acceleration Y', axs[5])
        plt.legend()
        plt.show()

    @staticmethod
    def __plot(t, v, agent_id, chart_title, ax) -> None:
        ax.plot(t, v, label=f"agent id: {agent_id}")
        ax.set_title(chart_title)

    def get_vehicle_trajectories(self) -> List[VehicleTrajectory]:
        return [VehicleTrajectory(self.time, self.storage[agent_id]) for agent_id in self.storage.keys()]
