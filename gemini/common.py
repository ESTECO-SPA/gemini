import math
from queue import Queue
from typing import List


class Point2d:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"[{self.x}, {self.y}]"

    def __sub__(self, other):
        return Point2d(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Point2d(self.x + other.x, self.y + other.y)

    def __rmul__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return Point2d(other * self.x, other * self.y)
        else:
            return NotImplemented

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def distance(self, other):
        diff = self - other
        return diff.norm()

    def norm(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)

    def unit_vector(self):
        return 1.0 / self.norm() * self


class Point3d:

    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self) -> str:
        return f"[{self.x}, {self.y}, {self.z}]"

    def __sub__(self, other):
        return Point3d(self.x - other.x, self.y - other.y, self.z - other.z)

    def __add__(self, other):
        return Point3d(self.x + other.x, self.y + other.y, self.z + other.z)

    def __rmul__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return Point3d(other * self.x, other * self.y, other * self.z)
        else:
            return NotImplemented

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z


class DelayedQueue:

    def __init__(self, delay: int) -> None:
        self.delayed_queue = Queue()
        self.delay = delay

    def put(self, item):
        self.delayed_queue.put(item)

    def get(self):
        if self.delayed_queue.qsize() < self.delay:
            return None
        return self.delayed_queue.get()

    def is_ready(self):
        return self.delayed_queue.qsize() > self.delay


class Interval:
    def interpolate(self, alpha: float):
        pass


class BoundedInterval(Interval):

    def __init__(self, loweb_bound, upper_bound) -> None:
        super().__init__()
        self.loweb_bound = loweb_bound
        self.upper_bound = upper_bound

    def interpolate(self, alpha: float):
        return self.loweb_bound + alpha * (self.upper_bound - self.loweb_bound)


class SingularInterval(Interval):

    def __init__(self, point) -> None:
        super().__init__()
        self.point = point

    def interpolate(self, alpha: float):
        return self.point


class VehicleState:
    def __init__(self, position: Point2d = Point2d(0, 0), velocity: Point2d = Point2d(0, 0), acceleration=Point2d(0, 0),
                 heading: float = 0, vehicle_id: int = -1) -> None:
        self.position = position
        self.velocity = velocity
        self.acceleration = acceleration
        self.heading = heading
        self.vehicle_id = vehicle_id

    def __repr__(self) -> str:
        return f"[id = {self.vehicle_id}, p = {self.position}, v = {self.velocity}, a = {self.acceleration}, h = {self.heading}"

    def __sub__(self, other):
        return VehicleState(self.position - other.position, self.velocity - other.velocity,
                            self.acceleration - other.acceleration,
                            heading=self.heading - other.heading)

    def __add__(self, other):
        return VehicleState(self.position + other.position, self.velocity + other.velocity,
                            self.acceleration + other.acceleration,
                            heading=self.heading + other.heading)

    def __rmul__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return VehicleState(other * self.position, other * self.velocity, other * self.acceleration,
                                heading=other * self.heading)

    def __eq__(self, other):
        return (self.velocity, self.position, self.acceleration, self.heading) == (
            other.velocity, other.position, self.acceleration, other.heading)

    def get_id(self):
        return self.vehicle_id

    def speed(self):
        return self.velocity.norm()

    def position_distance(self, other):
        return self.position.distance(other.position)

    def distance(self, other):
        return self.position.distance(other.position), self.velocity.distance(
            other.velocity), self.acceleration.distance(other.acceleration)

    def move(self, dt: float):
        spatial_increments = dt * self.velocity
        self.position = self.position + spatial_increments
        self.velocity = self.velocity + dt * self.acceleration
        self.heading = math.atan2(spatial_increments.y, spatial_increments.x)

    def move_velocity_acceleration(self, delta_position: Point2d,
                                   dt: float):  # update only velocity and acceleration based on dt (no position update!)
        print(delta_position)
        new_velocity = 1 / dt * delta_position
        self.acceleration = 1 / dt * (new_velocity - self.velocity)
        self.velocity = new_velocity
        state = VehicleState(self.position, self.velocity, self.acceleration,
                             math.atan2(delta_position.y, delta_position.x))
        # print(state)
        return state

    def to_list(self):
        return [self.position.x, self.position.y, self.velocity.x, self.velocity.y, self.acceleration.x,
                self.acceleration.y]


class TimedVehicleState:

    def __init__(self, time: float, state: VehicleState) -> None:
        self.state = state
        self.time = time

    def move(self, new_time: float):
        dt = new_time - self.time
        self.time = new_time
        self.state.move(dt)

    def get_state(self):
        return self.state


class VehicleTrajectory:

    def __init__(self, times: List[float], vehicle_states: List[VehicleState]) -> None:
        self.vehicle_states = vehicle_states
        self.times = times

    def __call__(self, time: float):
        return self.__find_state(time)

    def get_time_interval(self):
        return self.times[0], self.times[-1]

    def __find_state(self, time) -> VehicleState:
        i = 0
        if time <= self.times[0]:  # vehicle is not moving
            vehicle_state = self.vehicle_states[0]
            return VehicleState(vehicle_state.position, vehicle_id=vehicle_state.vehicle_id)
        elif time >= self.times[-1]:  # vehicle is not moving
            vehicle_state = self.vehicle_states[-1]
            return VehicleState(vehicle_state.position, heading=vehicle_state.heading,
                                vehicle_id=vehicle_state.vehicle_id)
        else:
            while time > self.times[i]:
                i = i + 1
            # between two time steps I consider constant velocity.
            lower_bound_time = self.times[i - 1]
            lower_bound_state = self.vehicle_states[i - 1]
            velocity = lower_bound_state.velocity
            position = lower_bound_state.position + (time - lower_bound_time) * velocity
            acceleration = lower_bound_state.acceleration
            state = VehicleState(position, velocity, acceleration, math.atan2(velocity.y, velocity.x),
                                 lower_bound_state.vehicle_id)
            return state
