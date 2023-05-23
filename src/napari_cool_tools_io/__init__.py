try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from ._sample_data import make_sample_data

__all__ = ("make_sample_data",)

import napari
import torch
from napari.utils.notifications import show_info

viewer = napari.current_viewer()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def memory_stats():
    show_info(f"Gpu memory allocated: {torch.cuda.memory_allocated()/1024**2}")
    show_info(f"Gpu memory reserved: {torch.cuda.memory_reserved()/1024**2}")
