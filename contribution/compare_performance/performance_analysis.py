import pickle

import numpy as np

from gemini.performance_analysis import PerformanceAnalysis
from gemini.resources import get_path_data_file

# 1) LOAD THE MODELED TRAJECTORIES
with open(get_path_data_file("irl_trajectory_object.pickle"), "rb") as file:
    irl_trajectory = pickle.load(file)

# 2) LOAD THE ORIGINAL TRAJECTORIES
with open(get_path_data_file("dataset_trajectory_object.pickle"), "rb") as file:
    dataset_trajectory = pickle.load(file)

# 3) INSTANTIATE THE PerformanceAnalysis OBJECT WHICH IS IN CHARGE OF EVALUATE / SHOW DIFFERENCES BETWEEN MODELED
# AND REAL TRAJECTORIES
performance_analysis = PerformanceAnalysis(dataset_trajectory, irl_trajectory, n_point=100)

# 3) COMPUTE THE DISTANCE BETWEEN THE MODELED AND ORIGINAL TRAJECTORY
# HOW THE DISTANCE IS EVALUATED?
# - a number of <n_point> equally spaced time step are created
# - for each of these time steps the position, velocity and acceleration of both trajectory are evaluated
# - for each time steps the Euclidean distance between the modeled and original trajectories (for position, velocity and
#   acceleration ) is evaluated. At this stage there are 3 distances vectors (one for position, one for velocity, ...)
# - the <operator> function is applied on each distance vector
agent_id = 0
performance = performance_analysis.compute_performance(agent_id=agent_id, operator=np.mean)
print("PERFORMANCE")
print(f"performance={performance}")

# 4) PLOT CHARTS
performance_analysis.plot(agent_id, "time-distance")
# performance_analysis.plot(0, "distance-distance")
