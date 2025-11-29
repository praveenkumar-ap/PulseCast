"""Indicator source adapters namespace."""

# Import side-effect registrations
from . import delphi_epidata, cdc_fluview, open_meteo

__all__ = ["delphi_epidata", "cdc_fluview", "open_meteo"]
