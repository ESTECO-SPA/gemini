
from .IRL.Auxiliary_functions.architectures_interface import (
    VariationalGenerator,
    VariationalGeneratorEncoded,
)


from .udp_driver.udp_osi_common import (
    OSIReceiver,
    UdpSender,
    input_modes,
)

__all__ = [
    "VariationalGeneratorEncoded",
    "VariationalGenerator",
    "OSIReceiver",
    "UdpSender",
    "input_modes",
]
