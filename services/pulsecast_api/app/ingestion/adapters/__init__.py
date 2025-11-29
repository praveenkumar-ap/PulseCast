"""
Adapter namespace.
"""

# Import submodules to trigger registration side-effects
from . import external, batch

__all__ = ["external", "batch"]
