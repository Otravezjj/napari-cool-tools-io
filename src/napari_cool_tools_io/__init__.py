try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from ._sample_data import make_sample_data

__all__ = ("make_sample_data",)

import napari
import torch

viewer = napari.current_viewer()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
