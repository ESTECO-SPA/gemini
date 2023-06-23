import tempfile
from os import path
from unittest import TestCase

from gemini.common import VehicleState
from gemini.simulation import SimulationTrajectory


class TestSimulationTrajectory(TestCase):

    def test_store_create_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = path.join(temp_dir, 'record.pickle')
            trajectory = SimulationTrajectory()

            trajectory.store(file_path)

            self.assertTrue(path.isfile(file_path))

    def test_add_single_state(self):
        trajectory = SimulationTrajectory()
        vehicle_state = VehicleState(vehicle_id=1)

        trajectory.add_state((0.23, [vehicle_state]))

        self.assertEqual([0.23], trajectory.time)
        self.assertEqual([vehicle_state], trajectory.storage[1])

    def test_add_many_state(self):
        trajectory = SimulationTrajectory()
        first_vehicle = VehicleState(vehicle_id=1)
        second_vehicle = VehicleState(vehicle_id=4)
        third_vehicle = VehicleState(vehicle_id=1)

        trajectory.add_state((0.23, [first_vehicle]))
        trajectory.add_state((0.24, [second_vehicle]))
        trajectory.add_state((0.29, [third_vehicle]))

        self.assertEqual([0.23, 0.24, 0.29], trajectory.time)
        self.assertEqual([first_vehicle, third_vehicle], trajectory.storage[1])
        self.assertEqual([second_vehicle], trajectory.storage[4])

    def test_get_vehicle_trajectories_with_empty_storage(self):
        trajectory = SimulationTrajectory()

        actual_trajectories = trajectory.get_vehicle_trajectories()

        self.assertTrue(not actual_trajectories)

    def test_get_vehicle_trajectories_with_one_storage_trajectory(self):
        trajectory = SimulationTrajectory()
        first_vehicle = VehicleState(vehicle_id=1)
        second_vehicle = VehicleState(vehicle_id=1)
        third_vehicle = VehicleState(vehicle_id=1)
        trajectory.add_state((0.23, [first_vehicle]))
        trajectory.add_state((0.24, [second_vehicle]))
        trajectory.add_state((0.29, [third_vehicle]))

        actual_trajectories = trajectory.get_vehicle_trajectories()

        self.assertEqual([0.23, 0.24, 0.29], actual_trajectories[0].times)
        self.assertEqual([first_vehicle, second_vehicle, third_vehicle], actual_trajectories[0].vehicle_states)
        self.assertEqual(1, len(actual_trajectories))

    def test_get_vehicle_trajectories_with_many_storage_trajectory(self):
        trajectory = SimulationTrajectory()
        first_vehicle = VehicleState(vehicle_id=1)
        second_vehicle = VehicleState(vehicle_id=2)
        third_vehicle = VehicleState(vehicle_id=1)
        fourth_vehicle = VehicleState(vehicle_id=2)
        trajectory.add_state((0.23, [first_vehicle, second_vehicle]))
        trajectory.add_state((0.24, [third_vehicle, fourth_vehicle]))

        actual_trajectories = trajectory.get_vehicle_trajectories()

        self.assertEqual([0.23, 0.24, ], actual_trajectories[0].times)
        self.assertEqual([first_vehicle, second_vehicle], actual_trajectories[0].vehicle_states)
        self.assertEqual([0.23, 0.24], actual_trajectories[1].times)
        self.assertEqual([third_vehicle, fourth_vehicle], actual_trajectories[1].vehicle_states)
        self.assertEqual(2, len(actual_trajectories))
