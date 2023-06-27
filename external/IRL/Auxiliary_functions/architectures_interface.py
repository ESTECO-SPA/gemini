import subprocess
from typing import List, Tuple

import torch
from torch import Tensor
from torch.distributions.multivariate_normal import MultivariateNormal


class VariationalGenerator(torch.nn.Module):

    def __init__(self, input_size: int, hidden_layers: List[int], output_size: int):
        super().__init__()
        pass

    def forward(self, x: torch.Tensor) -> Tuple[Tensor, MultivariateNormal]:
        pass


class VariationalGeneratorEncoded(VariationalGenerator):
    def __init__(self, input_size: int, hidden_layers: List[int], output_size: int, executable_path, weight_path):
        super().__init__(input_size, hidden_layers, output_size)
        self.executable_path = executable_path
        self.weight_path = weight_path

    def forward(self, x: torch.Tensor) -> Tuple[Tensor, MultivariateNormal]:
        data = x.tolist()[0]
        executable_format = ",".join([str(x) for x in data])
        output = subprocess.run([self.executable_path, self.weight_path, executable_format], capture_output=True)
        result = [float(v) for v in output.stdout.decode().strip().split(",")]
        return torch.Tensor([result]), None
