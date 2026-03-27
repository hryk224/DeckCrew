"""Audience persona definitions.

Each persona represents a distinct listener segment with different
musical preferences and reaction tendencies.
"""

from typing import Literal

from pydantic import BaseModel, Field

PersonaName = Literal["clubber", "chiller", "explorer"]


class AudiencePersona(BaseModel):
    """Attributes defining a virtual audience segment."""

    name: PersonaName
    label: str
    preferred_energy: float = Field(ge=0.0, le=1.0)
    preferred_bpm: int = Field(ge=60, le=200)
    change_sensitivity: float = Field(ge=0.0, le=1.0)


CLUBBER = AudiencePersona(
    name="clubber",
    label="Clubber",
    preferred_energy=0.8,
    preferred_bpm=130,
    change_sensitivity=0.3,
)

CHILLER = AudiencePersona(
    name="chiller",
    label="Chiller",
    preferred_energy=0.35,
    preferred_bpm=100,
    change_sensitivity=0.2,
)

EXPLORER = AudiencePersona(
    name="explorer",
    label="Explorer",
    preferred_energy=0.5,
    preferred_bpm=120,
    change_sensitivity=0.8,
)

DEFAULT_PERSONAS: list[AudiencePersona] = [CLUBBER, CHILLER, EXPLORER]
