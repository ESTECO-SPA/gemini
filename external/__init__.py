from .IRL.Auxiliary_functions.architectures_interface import (
    # Generic_Network,
    Variational_Generator,
)

from .udp_driver.udp_osi_common import (
    OSIReceiver,
    UdpSender,
    input_modes,
)

__all__ = [
    # "Generic_Network",
    "Variational_Generator",
    "OSIReceiver",
    "UdpSender",
    "input_modes",
]
