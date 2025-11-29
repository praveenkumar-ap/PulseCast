"""
External signal adapters for third-party data sources.
"""

# Import adapters for side-effect registration
from . import delphi_epidata, cdc_fluview, weather_open_meteo

__all__ = ["delphi_epidata", "cdc_fluview", "weather_open_meteo"]
