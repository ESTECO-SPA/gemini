import numpy as np
import pandas as pd
import torch

from external import VariationalGenerator
from gemini.dataset import TrajectoryDatabase, roll_out, PlotFiskhamnsmotet, to_sampling_time_state
from gemini.resources import get_path_data_file

if __name__ == '__main__':
    target_id = 5
    tracks = pd.read_csv(get_path_data_file('corrected_tracks.csv'))
    db = TrajectoryDatabase(tracks)
    trajectory_states = db.get_generator(target_id, 2)
    input_size = 18
    hidden_layers = [18, 18, 16, 16, 14, 14, 12, 12, 12]
    output_size = 5
    G = VariationalGenerator(input_size, hidden_layers, output_size)
    sampling_state = [to_sampling_time_state(state, 0.05) for state in trajectory_states]
    rollout = roll_out(G, sampling_state)
    predicted_trajectory = np.array(rollout)

    target, obstacles = db.get_trajectories(target_id)

    plot = PlotFiskhamnsmotet()
    plot.add("target", list(target.X), list(target.Y))
    plot.add("predicted", predicted_trajectory[:, 0], predicted_trajectory[:, 1])
    for obstacle in obstacles:
        plot.add("obstacle", list(obstacle.X), list(obstacle.Y))
    plot.plot()
