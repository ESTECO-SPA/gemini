import math
from unittest import TestCase

from gemini.common import DelayedQueue, VehicleState, Point2d, VehicleTrajectory, \
    BoundedInterval, SingularInterval, Point3d


class TestPoint2d(TestCase):

    def test_sub(self):
        left_point = Point2d(1, 2)
        right_point = Point2d(2, 4)

        actual_diff = left_point - right_point

        expected_diff = Point2d(-1, -2)
        self.assertEqual(expected_diff, actual_diff)

    def test_add(self):
        left_point = Point2d(1, 2)
        right_point = Point2d(2, 4)

        actual_sum = left_point + right_point

        expected_sum = Point2d(3, 6)
        self.assertEqual(expected_sum, actual_sum)

    def test_rmul_int(self):
        point = Point2d(1, 2)

        actual_rmul = 3 * point

        expected_rmul = Point2d(3, 6)
        self.assertEqual(expected_rmul, actual_rmul)

    def test_rmul_float(self):
        point = Point2d(1, 2)

        actual_rmul = 3.0 * point

        expected_rmul = Point2d(3.0, 6.0)
        self.assertEqual(expected_rmul, actual_rmul)

    def test_two_points_are_equal(self):
        left_point = Point2d(1, 2)
        right_point = Point2d(1, 2)

        self.assertTrue(left_point == right_point)

    def test_two_points_are_not_equal(self):
        left_point = Point2d(1, 2)
        right_point = Point2d(2, 2)

        self.assertFalse(left_point == right_point)

    def test_distance(self):
        left_point = Point2d(1, 2)
        right_point = Point2d(4, 6)

        actual_left_distance = left_point.distance(right_point)
        actual_right_distance = right_point.distance(left_point)

        self.assertEqual(actual_left_distance, actual_right_distance)
        self.assertEqual(5.0, actual_left_distance)

    def test_norm(self):
        point = Point2d(3, 4)

        actual_norm = point.norm()

        self.assertEqual(5.0, actual_norm)

    def test_unit_vector(self):
        point = Point2d(3.0, 4.0)

        actual_unit_vector = point.unit_vector()

        almost_equal(self.assertAlmostEqual, Point2d(3.0 / 5.0, 4.0 / 5.0), actual_unit_vector)


def almost_equal(condition, left: Point2d, right: Point2d):
    return condition(left.x, right.x, delta=1E-15) and condition(left.y, right.y, delta=1E-15)


class TestPoint3d(TestCase):

    def test_sub(self):
        left_point = Point3d(1, 2, 4)
        right_point = Point3d(2, 4, 7)

        actual_diff = left_point - right_point

        expected_diff = Point3d(-1, -2, -3)
        self.assertEqual(expected_diff, actual_diff)

    def test_add(self):
        left_point = Point3d(1, 2, 2)
        right_point = Point3d(2, 4, 3)

        actual_sum = left_point + right_point

        expected_sum = Point3d(3, 6, 5)
        self.assertEqual(expected_sum, actual_sum)

    def test_rmul_int(self):
        point = Point3d(1, 2, 7)

        actual_rmul = 3 * point

        expected_rmul = Point3d(3, 6, 21)
        self.assertEqual(expected_rmul, actual_rmul)

    def test_rmul_float(self):
        point = Point3d(1, 2, -1)

        actual_rmul = 3.0 * point

        expected_rmul = Point3d(3.0, 6.0, -3.0)
        self.assertEqual(expected_rmul, actual_rmul)

    def test_two_points_are_equal(self):
        left_point = Point3d(1, 2, 2)
        right_point = Point3d(1, 2, 2)

        self.assertTrue(left_point == right_point)

    def test_two_points_are_not_equal(self):
        left_point = Point3d(1, 2, 5)
        right_point = Point3d(2, 2, 5)

        self.assertFalse(left_point == right_point)


class TestDelayedQueue(TestCase):

    def test_is_ready_is_false_with_zero_delay_and_zero_elements(self):
        queue = DelayedQueue(0)

        self.assertFalse(queue.is_ready())

    def test_is_ready_is_false_with_positive_delay(self):
        queue = DelayedQueue(1)
        queue.put("a")

        actual_ready = queue.is_ready()

        self.assertFalse(actual_ready)

    def test_is_ready_is_true_with_positive_delay(self):
        queue = DelayedQueue(1)
        queue.put("a")
        queue.put("a")

        actual_ready = queue.is_ready()

        self.assertTrue(actual_ready)


class TestBoundedInterval(TestCase):

    def test_interpolate_with_alpha_zero(self):
        interval = BoundedInterval(1, 10)

        interpolated_point = interval.interpolate(0)

        self.assertEqual(1, interpolated_point)

    def test_interpolate_with_alpha_one(self):
        interval = BoundedInterval(1, 10)

        interpolated_point = interval.interpolate(1)

        self.assertEqual(10, interpolated_point)


class TestSingularInterval(TestCase):

    def test_interpolate_with_any_alpha(self):
        interval = SingularInterval(78)

        interpolated_point = interval.interpolate(123)

        self.assertEqual(78, interpolated_point)


class TestVehicleState(TestCase):

    def test_speed(self):
        vehicle_state = VehicleState(position=Point2d(1, 1), velocity=Point2d(1, 1), heading=1.0)

        actual_heading_speed = vehicle_state.speed()

        self.assertEqual(math.sqrt(2), actual_heading_speed)

    def test_distance(self):
        left_vehicle_state = VehicleState(position=Point2d(1, 1), velocity=Point2d(1, 1), heading=1.0)
        right_vehicle_state = VehicleState(position=Point2d(4, 5), velocity=Point2d(1, 1), heading=1.0)

        actual_distance = left_vehicle_state.position_distance(right_vehicle_state)

        self.assertEqual(5.0, actual_distance)

    def test_move_change_correctly_position(self):
        dt = 0.1
        acceleration = Point2d(0.1, 0.1)
        velocity = Point2d(1, 1)
        position = Point2d(1, 1)
        vehicle_state = VehicleState(position=position, velocity=velocity, acceleration=acceleration,
                                     heading=1.0)
        vehicle_state.move(dt)

        expected_velocity = velocity + dt * acceleration
        expected_position = position + dt * velocity
        self.assertEqual(expected_position, vehicle_state.position)
        self.assertEqual(expected_velocity, vehicle_state.velocity)
        self.assertEqual(acceleration, vehicle_state.acceleration)


class TestVehicleTrajectory(TestCase):

    def test_trajectory_between_two_states(self):
        times = [0.0, 1.0]
        vehicle_states = [VehicleState(position=Point2d(1, 1), velocity=Point2d(1, 1), heading=1.0),
                          VehicleState(position=Point2d(2, 2), velocity=Point2d(2, 2), heading=2.0)]
        vehicle_trajectory = VehicleTrajectory(times, vehicle_states)

        actual_state = vehicle_trajectory(0.5)

        self.assertEqual(VehicleState(position=Point2d(1.5, 1.5), velocity=Point2d(1, 1), heading=0.7853981633974483),
                         actual_state)

    def test_trajectory_stops_after_the_end_time(self):
        times = [0.0, 1.0]
        vehicle_states = [VehicleState(position=Point2d(1, 1), velocity=Point2d(1, 1), heading=1.0),
                          VehicleState(position=Point2d(2, 2), velocity=Point2d(2, 2), heading=2.0)]
        vehicle_trajectory = VehicleTrajectory(times, vehicle_states)

        actual_state = vehicle_trajectory(1.5)

        self.assertEqual(VehicleState(position=Point2d(2, 2), velocity=Point2d(0, 0), heading=2.0),
                         actual_state)

    def test_trajectory_stops_before_the_start_time(self):
        times = [1.0, 2.0]
        vehicle_states = [VehicleState(position=Point2d(1, 1), velocity=Point2d(1, 1), heading=1.0),
                          VehicleState(position=Point2d(2, 2), velocity=Point2d(2, 2), heading=2.0)]
        vehicle_trajectory = VehicleTrajectory(times, vehicle_states)

        actual_state = vehicle_trajectory(0.5)

        self.assertEqual(VehicleState(position=Point2d(1, 1), velocity=Point2d(0, 0), heading=0.0),
                         actual_state)
