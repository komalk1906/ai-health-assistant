"""
schemas/medicine.py
--------------------
Schema for the /api/medicines/{medicine_name} endpoint.
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict


class MedicineOut(BaseModel):
    id: int
    name: str
    common_uses: Optional[str] = None
    precautions: Optional[str] = None
    side_effects: Optional[str] = None
    warnings: Optional[str] = None
    seek_professional_advice: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
