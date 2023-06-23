from unittest import TestCase
from unittest.mock import Mock, MagicMock

from gemini.common import VehicleState, Point2d
from gemini.connector.osi_connector import TimedOSIReceiver, NearVehicles, GroundTruthInfo, \
    osi_time_calculator


class TestGroundTruthInfo(TestCase):
    def test_get_simulation_time(self):
        ground_truth_info = GroundTruthInfo(generate_mocked_ground_truth_with_time(1, 1_000_000))

        osi_time = ground_truth_info.get_simulation_time()

        self.assertEqual(osi_time_calculator(1, 1_000_000), osi_time)


class TestTimedOSIReceiver(TestCase):
    def test_receive(self):
        receiver = Mock()
        receiver.side_effect = [
            generate_mocked_ground_truth_with_time(1, 2000000),
            generate_mocked_ground_truth_with_time(2, 8000000),
            generate_mocked_ground_truth_with_time(3, 2000000)
        ]
        mocked_osi_receive = Mock()
        mocked_osi_receive.receive = receiver
        timed_osi_receiver = TimedOSIReceiver(mocked_osi_receive)

        actual_ground_truth = timed_osi_receiver.receive(1.001)

        expected_time = osi_time_calculator(2, 8000000)
        self.assertEqual(expected_time, actual_ground_truth.get_simulation_time())

    def test_receive_skip_one_element(self):
        receiver = Mock()
        receiver.side_effect = [
            generate_mocked_ground_truth_with_time(1, 2000000),
            generate_mocked_ground_truth_with_time(2, 8000000),
            generate_mocked_ground_truth_with_time(4, 6000000)
        ]
        mocked_osi_receive = Mock()
        mocked_osi_receive.receive = receiver
        timed_osi_receiver = TimedOSIReceiver(mocked_osi_receive)

        actual_ground_truth = timed_osi_receiver.receive(1.007)

        expected_time = osi_time_calculator(4, 6000000)
        self.assertEqual(expected_time, actual_ground_truth.get_simulation_time())


def generate_mocked_ground_truth_with_time(seconds, nanos):
    mocked_ground_truth = Mock()
    mocked_ground_truth.timestamp.seconds = seconds
    mocked_ground_truth.timestamp.nanos = nanos
    return mocked_ground_truth


class TestNearVehicle(TestCase):

    def test_get_vehicle_near_to_without_vehicles(self):
        ground_truth = generate_mocked_ground_truth_with_vehicle([])
        near_vehicle = NearVehicles(ground_truth)
        target_vehicle = VehicleState(position=Point2d(2, 2), velocity=Point2d(1, 1), heading=1.0)

        with self.assertRaises(ValueError):
            near_vehicle.get_vehicles_near_to(target_vehicle)

    def test_get_vehicle_near_to_with_only_one_vehicles(self):
        expected_near_vehicle = VehicleState(position=Point2d(1, 1), velocity=Point2d(1, 1), heading=1.0)
        vehicles = [expected_near_vehicle]
        ground_truth = generate_mocked_ground_truth_with_vehicle(vehicles)
        near_vehicle = NearVehicles(ground_truth)
        target_vehicle = VehicleState(position=Point2d(2, 2), velocity=Point2d(1, 1), heading=1.0)

        actual_near_vehicles = near_vehicle.get_vehicles_near_to(target_vehicle)

        self.assertEqual(expected_near_vehicle, actual_near_vehicles[0])

    def test_get_vehicle_near_to_with_many_vehicles(self):
        expected_near_vehicle = VehicleState(position=Point2d(1, 1), velocity=Point2d(1, 1), heading=1.0)
        vehicles = [VehicleState(position=Point2d(2, 1), velocity=Point2d(1, 1), heading=1.0),
                    expected_near_vehicle]
        ground_truth = generate_mocked_ground_truth_with_vehicle(vehicles)
        near_vehicle = NearVehicles(ground_truth)
        target_vehicle = VehicleState(position=Point2d(0.5, 0.5), velocity=Point2d(1, 1), heading=1.0)

        actual_near_vehicles = near_vehicle.get_vehicles_near_to(target_vehicle)

        self.assertEqual(expected_near_vehicle, actual_near_vehicles[0])

    def test_get_two_near_vehicle_to_with_many_vehicles(self):
        expected_near_vehicles = [VehicleState(position=Point2d(1, 1), velocity=Point2d(1, 1), heading=1.0),
                                  VehicleState(position=Point2d(2, 1), velocity=Point2d(1, 1), heading=1.0)]
        vehicles = [VehicleState(position=Point2d(2, 1), velocity=Point2d(1, 1), heading=1.0),
                    VehicleState(position=Point2d(1, 1), velocity=Point2d(1, 1), heading=1.0),
                    VehicleState(position=Point2d(10, 10), velocity=Point2d(1, 1), heading=1.0)]
        ground_truth = generate_mocked_ground_truth_with_vehicle(vehicles)
        near_vehicle = NearVehicles(ground_truth)
        target_vehicle = VehicleState(position=Point2d(0.5, 0.5), velocity=Point2d(1, 1), heading=1.0)

        actual_near_vehicles = near_vehicle.get_vehicles_near_to(target_vehicle, 2)

        self.assertEqual(expected_near_vehicles, actual_near_vehicles)


def generate_mocked_ground_truth_with_vehicle(vehicles: list):
    mocked_ground_truth = Mock()
    mocked_ground_truth.get_vehicle_states = MagicMock(
        return_value=vehicles)
    return mocked_ground_truth
