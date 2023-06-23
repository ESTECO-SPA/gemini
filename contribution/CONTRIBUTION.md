# Contribution

Please take a look at the following sections to understand the architecture and the process flow.
The idea is simple:

- Actors can perceive the GroundTruthInfo of the simulation
- Agents are Actors that can change vehicle dynamics (through UDP message)
- Agent's behavior depends on a specific Logic (you can implement your own logic)
- SimulationLink class defines time_step used by the Actors to perceive the GroundTruthInfo of the simulation,
  see `gemini.actors.SimulationLink.live`.

### 0. Packages / folder

- **external**: contains file/code provided at the beginning of the project. These file have been not modified except
  for
  `external/udp_driver/udp_osi_common.py` where a copy of GroundTruth has been returned (
  see `external/udp_driver/udp_osi_common.py:189`)
- **gemini**: source code folder
- **test**: test folder
- **contribution**: doc folder
    - **contribution/model**: rollout_*.py have been created to understand differences between the original
      nearest_neighbor routine and the one implemented in Gemini.
- **.env file**: file which defines environmental variables used to read/store file, knows where `libesminiLib.so` is
  located, etc.

### 1. Elements

#### Actors, Agents, Logic

- Each entity interacting with the ESMINI simulator implements the Actor interface (`gemini.actors.Actor`) which takes
  as input a `gemini.connector.osi_connector.GroundTruthInfo` object (a wrapper around `osi3.osi_groundtruth_pb2`)
- There are two kind of Actors:  `gemini.actors.SimulationRecorder` used to retrieve information from the ground truth
  and `gemini.actors.Agent` which interacts with the simulator through `gemini.actors.AgentConnector` (which use
  `gemini.actors.UdpSenderXYH` a wrapper around `external.udp_driver.udp_osi_common.UdpSender` )
- The `gemini.actors.Agent` decide to "do things" based on its own logic `gemini.action_logic.ActionLogic`.
  There are 5 logics. You should take a look to two of them: `gemini.action_logic.VariationalGeneratorLogic` and
  `gemini.action_logic.FollowTrajectoryLogic`
    - `gemini.action_logic.VariationalGeneratorLogic`  is the logic of the IRL model. You can see that it identify the
      two nearest vehicles in a distance range of 200mt and passes this information to the IRL model which is a
      `external.IRL.Auxiliary_functions.architectures.Generic_Network` (see the field `gemini/action_logic.py:58`).
    - `gemini.action_logic.FollowTrajectoryLogic`  is a logic which inject the original dataset trajectories
      into simulation. It uses the callable `gemini.common.VehicleTrajectory` that takes as input a time and return the
      `gemini.common.VehicleState` at that specific time. This is a result of an interpolation,  
      see `gemini.common.VehicleTrajectory.__find_state`

**Remark:** the rollout routine of the original model implementation(see `external/IRL/8. Rollouts.ipynb`
and `contribution/model/rollout_original.py:62` #REF1 comment)
consider as input the two nearest vehicles to the original trajectory and not the actual trajectory. On the contrary,
the gemini implementation refers to the actual position of the
ego vehicle to evaluate the two nearest vehicles. Pay attention that I am referring to the rollout procedure, I do not
know what happens in the training phase of the IRL models.
You can refer to the code (folder: `external/IRL`) to access this information.

### 2. Process Flow

Let me describe all the steps that allow injecting the original trajectories + IRL pre-trained model into the
simulation.
Please refer to `contribution/compare_performance/inject_IRL.py`

- Step 1: load the original IRL pretrained model. It is
  a `external.IRL.Auxiliary_functions.architectures.Variational_Generator`
- Step 2: load an episode (interaction between a target vehicle and obstacles vehicles)
- Step 3: create an open scenario file that is compatible with the aforementioned episode
- Step 4: run a simulation of the previous episode (with OSI/UDP open channel)
- Step 5: generate the actors that will interact with the simulation.
- Step 6: start the communication with the simulator (for a maximum time defined by max_time argument)
- Step 7: stop the simulation
- Step 8: store the simulated trajectories on a file (or plot the dynamics, etc.. )

### 3. How do actors take a decision?

Take a look to `gemini.actors.SimulationLink.live` The idea is that approximately each time_step unit of time the
SimulationLink perceives the ground_truth_info of the simulation. It gives this information to each actor
which decided to act.

- If the actor is an agent with `gemini.action_logic.FollowTrajectoryLogic` logic it interpolates
  the state based on the current simulation time (`gemini/action_logic.py:50`) and drives the simulation by sending this
  information to the simulator `gemini/actors.py:62`
- If the actor is an agent with `gemini.action_logic.VariationalGeneratorLogic` it will delegate decision to
  the pre-trained IRL model.

## Required Improvements

### 1. IRL model state/action

Now the IRL model considers the other vehicle dynamics and gives back the delta step movement to take for the next 0.05
seconds. As described previously, we do not have access to this precise time step but I can wait approximately that time
step
(It will be higher e.g 0.06/0.07. See `gemini.connector.osi_connector.TimedOSIReceiver.receive`)
Please create an IRL which gives as output action the next vehicle speed directly.
In this way, I am not forced to compute it (see `gemini.common.VehicleState.move_velocity_acceleration`).

The IRL considers as "speed" of another vehicle as the delta position between two consecutive timesteps of 0.05 sec.
The same occurs for acceleration. I do not have direct access to this information since the system asks for vehicle
dynamics
directly to the simulator. Please allow the IRL model to take as state the standard speed and acceleration of other
vehicles.
Now I need to infer it here: `gemini.action_logic.VariationalGeneratorLogic.__to_torch_state`)

### 2. New UDP input mode

Now the dead reckoning modality has been implemented. It is ok because I can send position and speed of
a vehicle in a given time step and this vehicle will keep that speed for the next time frame.
This feature is needed by the IRL model so that it can query the simulator and ask for other vehicle dynamics.
The problem arises when I pass the next vehicle information. These are the steps:

- I ask the simulator to give me information on vehicle dynamics (position and velocity)
- a logic decides to change velocity and take k sec for doing that. At the same time, the vehicle keeps moving.
- I change the velocity and send back this information to the simulator but with the old position.
- The vehicle is teleported back of some meter, if I ask the simulator to give me back the vehicle information I see
  really
  high acceleration and wrong speed (see `contribution.deadreckoning.ConstantVelocityLogic` that sends back always the
  same
  velocity but takes time to do that ). This kind of behavior is problematic for the IRL model which can perceive a
  surrounding vehicle has a really high acceleration!
  Please add a driver input mode where I can only change the velocity of the vehicle,
  and I am not forced to change also the position.

## Known Issues

### Speed of simulated agent

Consider `contribution/deadreckoning.py:21` (use it without time.sleep(0.01)).
In this example, I implemented a logic that should keep a constant velocity of 1.42 m/s.

Each time_step (see `contribution/deadreckoning.py:43`), I send a UDP message saying to the vehicle to keep the actual
position and a fixed speed of 1.42 m/s (I am using deadreckoning input mode).
If time_step is below 0.02 sec really strange acceleration occurs. Maybe sending too many UDP messages is a bad idea?

### Zig-zag movement / faster car

If you execute `contribution/compare_performance/inject_IRL.py` to see how the IRL model behaves you will notice two
differences w.r.t the original trajectory (run `contribution/compare_performance/inject_dataset.py`)

1. the IRL model generates a faster car if compared with the original one
2. there is a strange zig-zag movement

Both differences are due to the `gemini.action_logic.VariationalGeneratorLogic.act` method which have been properly
commented, please take a look to it.

More specifically, **issue number 1** is due to the adaptation needed to evaluate the new dynamics of the agent. This
adaptation ise required because the original IRL works with a fixed timestep of 0.05s and
because the velocity is just the difference in position related to that time step. See Required Improvement number 1.

**Issue number 2** is caused by the perceived acceleration of the obstacles, this acceleration indeed seems to be really
high. If you switch off the acceleration, considering each obstacles moving at constant speed you will notice that the
zig-zag dynamics disappears.  
