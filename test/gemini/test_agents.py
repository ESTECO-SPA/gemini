import struct
from unittest import TestCase
from unittest.mock import Mock

from external import input_modes
from gemini.actors import UdpSenderXYH
from gemini.common import VehicleState, Point2d


class TestUdpSenderChannel(TestCase):
    def test_send_position_state(self):
        udp_sender = Mock()
        udp_sender.send = Mock()
        udp_sender_channel = UdpSenderXYH(udp_sender)
        vehicle_state = VehicleState(Point2d(1, 2), Point2d(3, 4), Point2d(5, 6), 3.1)
        expected_message = struct.pack(
            'iiiidddddB',
            1,  # version
            input_modes['stateXYH'],
            0,  # object ID
            0,  # frame nr
            1,  # x
            2,  # y
            3.1,  # h
            5,  # speed
            0.0,
            1
        )

        udp_sender_channel.send_position_state(0, vehicle_state)

        udp_sender.send.assert_called_once_with(expected_message)
