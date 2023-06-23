import math
from typing import List, Tuple

import matplotlib.transforms as mtransforms
import numpy as np
import torch
from PIL import Image
from matplotlib import pyplot as plt

from gemini.common import VehicleState, Point2d, VehicleTrajectory
from gemini.resources import get_path_data_file
from gemini.scenario import ScenarioModelObject


class TrajectoryDatabase:

    def __init__(self, trajectories) -> None:
        self.trajectories = trajectories

    def __get_interactions(self, trajectory_id: int):
        target_trajectory = self.trajectories[self.trajectories['member'] == trajectory_id]
        target_time_interval = target_trajectory.iloc[0]['Timestamps_UNIX'], target_trajectory.iloc[-1][
            'Timestamps_UNIX']
        interacting_trajectories = self.trajectories[
            (self.trajectories['Timestamps_UNIX'] >= target_time_interval[0]) &
            (self.trajectories['Timestamps_UNIX'] <= target_time_interval[1]) &
            (self.trajectories['member'] != trajectory_id)
            ]
        interacting_trajectories.loc[:, 'Timestamps_UNIX'] = interacting_trajectories['Timestamps_UNIX'].apply(
            lambda x: round(x - target_time_interval[0], 2))
        target_trajectory.loc[:, 'Timestamps_UNIX'] = target_trajectory['Timestamps_UNIX'].apply(
            lambda x: round(x - target_time_interval[0], 2))
        interacting_trajectories = [interacting_trajectories[interacting_trajectories['member'] == i] for i in
                                    interacting_trajectories['member'].unique()]
        self.__add_dynamics(target_trajectory)
        interacting_trajectories = [trajectory for trajectory in interacting_trajectories if (len(trajectory)) > 2]
        for interacting_trajectory in interacting_trajectories:
            self.__add_dynamics(interacting_trajectory)
        return target_trajectory, interacting_trajectories

    def get_trajectories(self, trajectory_id):
        return self.__get_interactions(trajectory_id)

    def get_vehicle_trajectory(self, trajectory_id) -> Tuple[VehicleTrajectory, List[VehicleTrajectory]]:
        target, interactions = self.__get_interactions(trajectory_id)
        return self.__to_vehicle_trajectory(target), [self.__to_vehicle_trajectory(interaction) for interaction in
                                                      interactions]

    def get_scenario_objects(self, trajectory_id: int) -> Tuple[ScenarioModelObject, List[ScenarioModelObject]]:
        target_trajectory, obstacles_trajectories = self.get_vehicle_trajectory(trajectory_id)
        target_object = ScenarioModelObject(0, "ego", target_trajectory, 53901)
        obstacles_objects = [
            ScenarioModelObject(agent_id + 1, f"obstacle{agent_id}", obstacle_trajectory, agent_id + 53902) for
            obstacle_trajectory, agent_id in
            zip(obstacles_trajectories, range(len(obstacles_trajectories)))]
        return target_object, obstacles_objects

    @staticmethod
    def __to_vehicle_trajectory(df):
        times = list(df['Timestamps_UNIX'])
        trajectory = list(df.apply(lambda row: VehicleState(Point2d(row['X'], row['Y']), Point2d(row['dX'], row['dY']),
                                                            Point2d(row['ddX'], row['ddY']),
                                                            heading=math.atan2(row['dY'], row['dX'])), axis=1))
        return VehicleTrajectory(times, trajectory)

    def get_generator(self, trajectory_id: int, number_near_vehicles: int):
        target_trajectory, interacting_trajectories = self.__get_interactions(trajectory_id)
        for i in range(len(target_trajectory)):
            time = target_trajectory.iloc[i]['Timestamps_UNIX']
            target_state = self.__get__state(target_trajectory, time)
            interactions_state = [self.__get__state(interaction, time) for interaction in interacting_trajectories]
            obstacles_states = self.__get__obstacles_states(number_near_vehicles, target_state, interactions_state)
            yield self.__flatten(obstacles_states) + target_state

    @staticmethod
    def __flatten(array):
        return [item for sublist in array for item in sublist]

    @staticmethod
    def __get__state(df, time):
        if time in df['Timestamps_UNIX'].values:
            state = df[df['Timestamps_UNIX'] == time]
            return [state['X'].values[0], state['Y'].values[0], state['dX'].values[0], state['dY'].values[0],
                    state['ddX'].values[0], state['ddY'].values[0]]
        else:
            return [0, 0, 0, 0, 0, 0]

    @staticmethod
    def __distance(x, y):
        return (x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2

    @staticmethod
    def __get__obstacles_states(number_near_vehicles, target_state, interactions_state):
        distances = [TrajectoryDatabase.__distance(target_state, interaction_state) for interaction_state in
                     interactions_state]
        distances_sorted_indexes = np.argsort(distances)
        ordered_interactions_state = [interactions_state[i] for i in distances_sorted_indexes]
        return ordered_interactions_state[:number_near_vehicles]

    @staticmethod
    def __add_column(df, name):
        dt = df["Timestamps_UNIX"].to_numpy()[1:] - df["Timestamps_UNIX"].to_numpy()[:-1]
        dt = np.append(dt, dt[-1])
        column = df[name].to_numpy()
        d_name = np.append(column[1:] - column[:-1], 0)
        dd_name = np.append(d_name[1:] - d_name[:-1], 0)
        df.loc[:, 'd' + name] = d_name / dt
        df.loc[:, 'dd' + name] = dd_name / dt

    @staticmethod
    def __add_dynamics(df):
        TrajectoryDatabase.__add_column(df, 'X')
        TrajectoryDatabase.__add_column(df, 'Y')
        df.drop(df.tail(2).index, inplace=True)


def evaluate_dynamics(x, dx, dt):
    return x + dx * dt


def to_sampling_time_state(state, sampling_time):
    sampling_time_state = []
    states = np.array_split(state, len(state) / 6)
    for state in states:
        sampling_time_state.append(state[0])
        sampling_time_state.append(state[1])
        sampling_time_state.append(state[2] * sampling_time)
        sampling_time_state.append(state[3] * sampling_time)
        sampling_time_state.append(state[4] * sampling_time)
        sampling_time_state.append(state[5] * sampling_time)
    return sampling_time_state


def roll_out(network, trajectories):
    network.eval()
    current_state = trajectories[0][-6:-4]
    rollout = [current_state]
    for state in trajectories:
        with torch.no_grad():
            action, _ = network(torch.Tensor(state).reshape(1, -1))
            delta_position = action.tolist()[0]
            current_state = rollout[-1]
            rollout.append([current_state[0] + delta_position[0], current_state[1] + delta_position[1]])
    return rollout


def rotation(x, y):
    X = np.array(x)
    Y = np.array(y)
    angle = -np.pi / 3  # angle in radians
    scale = 2.2
    newx = scale * ((X - np.mean(X)) * np.cos(angle) - (Y - np.mean(Y)) * np.sin(angle)) - (
            np.mean(X) - 77)
    newy = scale * ((X - np.mean(X)) * np.sin(angle) + (Y - np.mean(Y)) * np.cos(angle)) - (
            np.mean(Y) - 403)
    return newx, newy


class PlotFiskhamnsmotet:

    def __init__(self) -> None:
        self.elements = list()

    def add(self, name, x, y):
        self.elements.append((name, x, y))

    def plot(self):
        image = Image.open(get_path_data_file("groundImage.png")).convert("L")
        arr = np.asarray(image)
        left_limit = 300
        right_limit = -50
        tr = mtransforms.Affine2D().rotate_deg(30)
        fig = plt.figure(figsize=(12, 6), constrained_layout=True)
        ax = fig.add_subplot(111)
        plt.imshow(arr, cmap='gray', vmin=0, vmax=255, transform=tr + ax.transData)
        for element in self.elements:
            name, x, y = element
            obstacle_x, obstacle_y = rotation(x, y)
            plt.plot(obstacle_x, obstacle_y, label=name)
        # plt.axvline(x=right_limit, c='r')
        # plt.axvline(x=left_limit, c='orange')
        plt.axis([-200, 350, 500, 300])
        plt.legend()
        plt.show()
