from typing import Callable

import matplotlib.pyplot as plt
import numpy as np

from gemini.simulation import SimulationTrajectory


class PerformanceAnalysis:

    def __init__(self, real_trajectory: SimulationTrajectory, model_trajectory: SimulationTrajectory, n_point: int = 100) -> None:
        self.real_trajectory = real_trajectory
        self.model_trajectory = model_trajectory
        self.n_point = n_point

    def plot(self, agent_id: int, chart_type: str = "time-distance") -> None:
        if chart_type == 'time-distance':
            self.plot_time_distance(agent_id)
        elif chart_type == 'distance-distance':
            self.plot_distance_distance(agent_id)
        else:
            ValueError(f"{chart_type} not allowed (choose time-distance or distance-distance)")

    def compute_performance(self, agent_id: int, operator: Callable):
        distances, _ = self.__evaluate_distances(agent_id)
        return f" distances = [position: {operator(distances[:, 0])}, " \
               f"velocity: {operator(distances[:, 1])}, acceleration: {operator(distances[:, 2])} ]"

    def __evaluate_distances(self, agent_id: int):
        real_trajectory = self.real_trajectory.get_trajectory(agent_id)
        time_interval = real_trajectory.get_time_interval()
        model_trajectory = self.model_trajectory.get_trajectory(agent_id)
        times = np.linspace(time_interval[0], time_interval[1], self.n_point)
        real_values = [real_trajectory(t) for t in times]
        model_values = [model_trajectory(t) for t in times]
        distances = np.array([real.distance(model) for real, model in zip(real_values, model_values)])
        return distances, times

    def plot_time_distance(self, agent_id: int):
        distances, times = self.__evaluate_distances(agent_id)
        fig, axs = plt.subplots(2, 1)
        axs[0].plot(times, distances[:, 0])
        axs[0].set_title("distance displacement")
        axs[1].plot(times, distances[:, 1])
        axs[1].set_title("velocity displacement")
        plt.show()

    def plot_distance_distance(self, agent_id: int):
        real_trajectory = self.real_trajectory.get_trajectory(agent_id)
        time_interval = real_trajectory.get_time_interval()
        model_trajectory = self.model_trajectory.get_trajectory(agent_id)
        times = np.linspace(time_interval[0], time_interval[1], 100)
        real_values = [real_trajectory(t).speed() for t in times]
        model_values = [model_trajectory(t).speed() for t in times]
        plt.plot(real_values, real_values, "r")
        plt.scatter(real_values[2:], model_values[2:])
        plt.xlabel("real speed")
        plt.ylabel("predicted speed")
        plt.show()
