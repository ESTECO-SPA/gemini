import pickle

import numpy as np
import pandas as pd
import torch

from external import Variational_Generator
from gemini.dataset import PlotFiskhamnsmotet
from gemini.resources import get_path_data_file


## This file contains the original rollout of Santiago. I only copy/paste all the required functions in this file.
## A dictionary named visitor is proviede as argument of policy_rollout so to collect information

def policy_rollout(b_states, flat_o_states, G, visitor: dict):
    l_a_state = torch.empty(b_states.shape)  # container for non standarized learning agent states
    l_a_state[0] = torch.Tensor(b_states[0])

    # non standarized position and velocity used to compute values in next Timestamps_UNIX step
    current_pos = torch.Tensor(b_states[0][:2])
    current_vel = torch.Tensor(b_states[0][2:4])

    G.eval()
    with torch.no_grad():
        for i in range(len(b_states) - 1):
            current_state = torch.cat([torch.Tensor(flat_o_states[i].reshape(1, -1)),
                                       l_a_state[i].reshape(1, -1)], dim=1).float()
            visitor.setdefault('torch_state', []).append(current_state.numpy()[0])
            visitor.setdefault('time', []).append(0.05 * i)
            action, _ = G(current_state)
            visitor.setdefault('action', []).append(action.numpy())

            current_pos = current_pos + action  # since the action is actually the change in position
            current_acc = action - current_vel  # this is the change in change in position delta_delta_pos

            current_vel = action  # change in position

            b_s = torch.cat([current_pos, current_vel, current_acc], dim=1)  # concatenate learning a state space

            l_a_state[i + 1] = b_s  # next state

    return l_a_state


def find_nearest_obstacles(state, obstacles, n_agents=2):
    current_pos = np.array(state[0][:2])
    obstacles_pos = [obstacles[i * 6:i * 6 + 2] for i in range(int(len(obstacles) / 6))]
    distances = [np.linalg.norm(current_pos - op) for op in obstacles_pos]
    sorted = np.argsort(distances)
    nearest = [obstacles[i * 6:i * 6 + 6] for i in sorted[0:n_agents]]
    return np.array(nearest).flatten()


def par_roll(test_ids, sel_routes, obstacles, G, visitor):
    roll_outs = []
    te = []
    original = []  # modification wrt Santiagos code. it stores origianl trajectory
    for i in test_ids:
        ac = sel_routes[sel_routes.member == i]
        if (len(ac) > 3) & (len(ac) < 400):
            ac_states, _, flat_o_states = get_individual_states(ac, obstacles, n_agents=2)
            # [REF1] flat_o_states are the obstacles. These have been evaluated based on the original trajectory, i.e ac.
            roll_outs.append(policy_rollout(ac_states, flat_o_states, G, visitor))
            te.append(i)
            original.append(np.array([ac.X.to_numpy(), ac.Y.to_numpy()]))

    return roll_outs, te, original


def get_individual_states(b, obstacles, n_agents=2):
    state_space = obstacles[(obstacles.Timestamps_UNIX >= b.iloc[0].Timestamps_UNIX) & (
            obstacles.Timestamps_UNIX <= b.iloc[-1].Timestamps_UNIX)]
    obstacle_states = np.array(get_expert_state_space(b, state_space, n_agents)).T
    b_states = np.array(get_trajectory_states(b)).T
    b_actions = np.array(get_trajectory_actions(b)).T

    return b_states, b_actions, flatten(obstacle_states)


def get_expert_state_space(expert, state_space, n_agents=2):
    '''
    For a given expert obtain the complete state space with respect to a fixed number of interactions (n_agents)
    '''
    state_df = get_state_df(state_space)
    interaction_ids = get_interactions(expert, state_df, n_agents)

    state_dfs = []

    for inter in interaction_ids:
        state_dfs.append(state_df.loc[inter])

    n_time_steps = len(interaction_ids)

    x_coord = np.zeros((n_agents, n_time_steps))  # x coordinates
    y_coord = np.zeros((n_agents, n_time_steps))  # y coordinates
    dx = np.zeros((n_agents, n_time_steps))  # x component of velocity vector
    dy = np.zeros((n_agents, n_time_steps))  # y component of velocity vector
    ddx = np.zeros((n_agents, n_time_steps))  # "" for acceleration vector
    ddy = np.zeros((n_agents, n_time_steps))  # "" for acceleration vector

    for i, df in enumerate(state_dfs):

        for obs in range(min(len(df), n_agents)):
            x_coord[obs, i] = df.iloc[obs].X
            y_coord[obs, i] = df.iloc[obs].Y
            dx[obs, i] = df.iloc[obs].d_x
            dy[obs, i] = df.iloc[obs].d_y
            ddx[obs, i] = df.iloc[obs].dd_x
            ddy[obs, i] = df.iloc[obs].dd_y

    return x_coord, y_coord, dx, dy, ddx, ddy


def get_trajectory_states(actor):
    '''
    For a given pandas dataframe containing the actor information, extract it's trajectory states.
    The trajectory states in this case are the position, the velocity, and the acceleration
    '''

    # changing from series to numpy array
    a_np_X = actor.X.to_numpy()
    a_np_Y = actor.Y.to_numpy()

    delta_X = np.append(0, a_np_X[1:] - a_np_X[
                                        :-1])  # this can be also viewed as the component of the direction vector in x
    delta_Y = np.append(0, a_np_Y[1:] - a_np_Y[:-1])  # "==" in y

    delta_delta_X = np.append(0, delta_X[1:] - delta_X[:-1])
    delta_delta_Y = np.append(0, delta_Y[1:] - delta_Y[:-1])

    return a_np_X[1:-1], a_np_Y[1:-1], delta_X[1:-1], delta_Y[1:-1], delta_delta_X[1:-1], delta_delta_Y[1:-1]


def get_state_df(state_space):
    '''
    Gets new dataframe with aditional columns containing the state values
    '''

    state_df = pd.DataFrame(columns=list(state_space.columns) + ['d_x', 'd_y', 'dd_x', 'dd_y'])
    uni_ids = np.unique(state_space.member)
    for i in uni_ids:
        temp_o = state_space[state_space.member == i].iloc[1:-1, :]
        if len(temp_o) < 3:
            continue

        _, _, dx, dy, ddx, ddy = get_trajectory_states(state_space[state_space.member == i])
        temp_o = temp_o.assign(d_x=dx, d_y=dy, dd_x=ddx, dd_y=ddy)

        state_df = pd.concat([state_df, temp_o])

    return state_df


def get_interactions(actor, no_ex_state, n_obs=2, x_threshold=200, y_threshold=200):
    '''
    This function obtains the ids of the vehicles with whom the actor interacts in a fixed time and space window.
    '''

    interaction_ids = []  # recovers the id columns of obstacles with which the expert "interacts" in each timestep
    for row in range(1, len(actor) - 1, 1):
        x_now = actor.iloc[row].X
        y_now = actor.iloc[row].Y
        t_now = actor.iloc[row].Timestamps_UNIX
        t_next = actor.iloc[row + 1].Timestamps_UNIX
        x_interval = pd.Interval(x_now - x_threshold, x_now + x_threshold, closed='neither')
        y_interval = pd.Interval(y_now - y_threshold, y_now + y_threshold, closed='neither')

        # Revisar creacion de intervalo de observacion
        result = (x_interval.left <= no_ex_state.X) & (no_ex_state.X <= x_interval.right) & \
                 (y_interval.left <= no_ex_state.Y) & (no_ex_state.Y <= y_interval.right) & \
                 (t_now <= no_ex_state.Timestamps_UNIX) & (no_ex_state.Timestamps_UNIX < t_next)

        # Get L2 distance from actor to obstacles inside space window at respectime time step
        value = (x_now - no_ex_state[result].X) ** 2 + (y_now - no_ex_state[result].Y) ** 2
        d = np.sqrt(value.astype('float64'))
        # Get ids for n_obs closest obstacles inside the space window
        ids = np.argsort(d)[:n_obs].index

        interaction_ids.append(ids)

    return interaction_ids


def get_trajectory_actions(actor):
    '''
    For a given pandas dataframe containing the actor information, extract it's trajectory actions.
    The trajectory action in this case is the velocity vector
    '''

    a_np_X = actor.X.to_numpy()
    a_np_Y = actor.Y.to_numpy()

    delta_X = np.append(a_np_X[1:] - a_np_X[:-1], 0)  # this can be viewed as the component of the direction vector in x
    delta_Y = np.append(a_np_Y[1:] - a_np_Y[:-1], 0)  # "==" in y

    return delta_X[1:-1], delta_Y[1:-1]


def flatten(states):
    # Flatten and rearanging obstacle states
    flatobs = []
    for elem in states:
        flatobs.extend(elem[:, :6])
    flatobs = np.array(flatobs)
    return flatobs.reshape(-1, 12)


tracks = pd.read_csv(get_path_data_file('corrected_tracks.csv'))
with open(get_path_data_file('uc2.pickle'), 'rb') as handle:
    uc2 = pickle.load(handle)

actor_ids = np.fromiter(uc2.keys(), dtype=int)
obstacle_ids = []
for v in uc2.values():
    obstacle_ids.extend(v[0])

obstacles = tracks[tracks.member.isin(obstacle_ids)]
# Generator Parameters: make sure hidden layer vector is the same as in notebook 7
input_size = 18
hidden_layers = [18, 18, 16, 16, 14, 14, 12, 12, 12]
output_size = 5
# Load Generator
data = dict()
G = Variational_Generator(input_size, hidden_layers, output_size)

roll_lists = []
target_id = 5
rollout, test_ids, original_trajectories = par_roll(np.array([target_id]), tracks, obstacles, G, data)
roll_lists.append(rollout)
x = [r[0].item() for r in rollout[0]]
y = [r[1].item() for r in rollout[0]]

x_original = original_trajectories[0][0, :]
y_original = original_trajectories[0][1, :]

plot = PlotFiskhamnsmotet()
plot.add("target", x_original, y_original)
plot.add("predicted", x, y)
plot.plot()

df = tracks[tracks['member'] == target_id][:-2]
df['Timestamps_UNIX'] = df['Timestamps_UNIX'] - df['Timestamps_UNIX'].iloc[0]

# All the collected information is stored in the DATA folder
with open(get_path_data_file("rollout_original.pickle"), "wb") as file:
    state = np.zeros(len(data['time']))
    ids = np.zeros((len(data['time']), 2))
    pickle.dump([data['time'], state, data['torch_state'], data['action'], ids], file)
