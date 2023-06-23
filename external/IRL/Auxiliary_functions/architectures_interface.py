from typing import List, Tuple

import torch
from torch import Tensor
from torch.distributions.multivariate_normal import MultivariateNormal


class Variational_Generator(torch.nn.Module):

    def __init__(self, input_size: int, hidden_layers: List[int], output_size: int):
        super().__init__()
        pass

    def forward(self, x) -> Tuple[Tensor, MultivariateNormal]:
        pass
