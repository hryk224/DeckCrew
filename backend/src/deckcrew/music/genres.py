"""Genre groups and resolution logic.

Users select a genre_group (e.g. "house_party"). The system resolves
which specific genre to use based on energy, time_of_night, section,
and venue vibe. Mood and instruments are derived from the genre.

10 groups defined. Not all need to be exposed in UI at once —
the set shown to users can be filtered at the presentation layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from deckcrew.state.models import Section
from deckcrew.venue.models import EventVibe, TimeOfNight


@dataclass
class GenreEntry:
    """A single genre within a group."""

    name: str
    lyria_prompt: str
    default_instruments: list[str]
    default_mood: str  # single value for now; may expand to list later
    energy_affinity: float  # 0.0-1.0: preferred energy level
    bpm_range: tuple[int, int] = (100, 140)


@dataclass
class GenreGroup:
    """A selectable genre group containing related genres."""

    id: str
    label: str
    genres: list[GenreEntry] = field(default_factory=list)


# --- Group definitions ---

HOUSE_PARTY = GenreGroup(
    id="house_party",
    label="House Party",
    genres=[
        GenreEntry("deep_house", "Deep House", ["Synth Pads", "Precision Bass"], "Groovy", 0.5, (118, 128)),
        GenreEntry("tech_house", "Tech House", ["Funk Drums", "808 Hip Hop Beat"], "Driving", 0.7, (124, 132)),
        GenreEntry("disco", "Disco Funk", ["Funk Drums", "Precision Bass"], "Funky", 0.6, (110, 126)),
    ],
)

TECHNO_NIGHT = GenreGroup(
    id="techno_night",
    label="Techno Night",
    genres=[
        GenreEntry("techno", "Techno", ["808 Hip Hop Beat", "Moog Oscillations"], "Dark", 0.7, (128, 145)),
        GenreEntry("minimal_techno", "Minimal Techno", ["Moog Oscillations", "Synth Pads"], "Hypnotic", 0.5, (120, 135)),
        GenreEntry("melodic_techno", "Melodic Techno", ["Synth Pads", "Moog Oscillations"], "Emotional", 0.6, (122, 138)),
    ],
)

EDM_FESTIVAL = GenreGroup(
    id="edm_festival",
    label="EDM Festival",
    genres=[
        GenreEntry("edm", "EDM", ["Synth Pads", "Funk Drums"], "Upbeat", 0.8, (126, 150)),
        GenreEntry("progressive", "Trance", ["Synth Pads", "Moog Oscillations"], "Euphoric", 0.7, (128, 140)),
        GenreEntry("future_house", "Synthpop", ["Synth Pads", "Precision Bass"], "Bright", 0.6, (124, 132)),
    ],
)

BASS_MUSIC = GenreGroup(
    id="bass_music",
    label="Bass Music",
    genres=[
        GenreEntry("dubstep", "Dubstep", ["808 Hip Hop Beat", "Precision Bass"], "Aggressive", 0.8, (140, 150)),
        GenreEntry("drum_and_bass", "Drum & Bass", ["Funk Drums", "Precision Bass"], "Intense", 0.9, (160, 180)),
        GenreEntry("trap", "Trap Beat", ["808 Hip Hop Beat", "Precision Bass"], "Hard", 0.7, (130, 150)),
        GenreEntry("bass_house", "Breakbeat", ["Funk Drums", "808 Hip Hop Beat"], "Heavy", 0.7, (124, 132)),
    ],
)

HIPHOP_RNB = GenreGroup(
    id="hiphop_rnb",
    label="Hip Hop / R&B",
    genres=[
        GenreEntry("hip_hop", "Lo-Fi Hip Hop", ["808 Hip Hop Beat", "Rhodes Piano"], "Chill", 0.4, (80, 100)),
        GenreEntry("trap_hiphop", "Trap Beat", ["808 Hip Hop Beat", "Precision Bass"], "Hard", 0.7, (130, 150)),
        GenreEntry("rnb", "R&B", ["Rhodes Piano", "Precision Bass"], "Smooth", 0.4, (80, 110)),
        GenreEntry("afrobeats", "Afrobeat", ["Funk Drums", "Precision Bass"], "Groovy", 0.6, (100, 120)),
    ],
)

LATIN_GLOBAL = GenreGroup(
    id="latin_global",
    label="Latin / Global",
    genres=[
        GenreEntry("reggaeton", "Reggaeton", ["808 Hip Hop Beat", "Precision Bass"], "Danceable", 0.7, (90, 105)),
        GenreEntry("salsa", "Salsa", ["Conga Drums", "Trumpet"], "Lively", 0.6, (160, 190)),
        GenreEntry("cumbia", "Cumbia", ["Maracas", "Accordion"], "Festive", 0.5, (80, 110)),
        GenreEntry("afrobeat", "Afrobeat", ["Funk Drums", "Precision Bass"], "Groovy", 0.6, (100, 130)),
    ],
)

DISCO_FUNK = GenreGroup(
    id="disco_funk",
    label="Disco / Funk",
    genres=[
        GenreEntry("disco_funk", "Disco Funk", ["Funk Drums", "Precision Bass"], "Funky", 0.6, (110, 130)),
        GenreEntry("boogie", "Disco Funk", ["Funk Drums", "Rhodes Piano"], "Groovy", 0.5, (105, 125)),
        GenreEntry("soul", "Neo-Soul", ["Rhodes Piano", "Warm Acoustic Guitar"], "Soulful", 0.4, (90, 110)),
    ],
)

ROCK_INDIE = GenreGroup(
    id="rock_indie",
    label="Rock / Indie",
    genres=[
        GenreEntry("rock", "Classic Rock", ["Guitar", "Funk Drums"], "Energetic", 0.7, (110, 140)),
        GenreEntry("indie_rock", "Indie Pop", ["Guitar", "Synth Pads"], "Bright", 0.5, (100, 130)),
        GenreEntry("alternative", "Psychedelic Rock", ["Guitar", "Synth Pads"], "Dreamy", 0.5, (90, 130)),
    ],
)

CHILL_LOUNGE = GenreGroup(
    id="chill_lounge",
    label="Chill / Lounge",
    genres=[
        GenreEntry("chillout", "Chillout", ["Synth Pads", "Warm Acoustic Guitar"], "Relaxed", 0.2, (80, 110)),
        GenreEntry("lo_fi_hip_hop", "Lo-Fi Hip Hop", ["Rhodes Piano", "Warm Acoustic Guitar"], "Chill", 0.3, (70, 95)),
        GenreEntry("trip_hop", "Trip Hop", ["Synth Pads", "Precision Bass"], "Moody", 0.3, (80, 110)),
        GenreEntry("neo_soul", "Neo-Soul", ["Rhodes Piano", "Precision Bass"], "Smooth", 0.3, (85, 105)),
    ],
)

OPEN_FORMAT = GenreGroup(
    id="open_format",
    label="Open Format",
    genres=[],  # No fixed genres; borrows from all groups dynamically
)

# All groups in display order
ALL_GROUPS: list[GenreGroup] = [
    HOUSE_PARTY, TECHNO_NIGHT, EDM_FESTIVAL, BASS_MUSIC,
    HIPHOP_RNB, LATIN_GLOBAL, DISCO_FUNK, ROCK_INDIE,
    CHILL_LOUNGE, OPEN_FORMAT,
]

GROUPS_BY_ID: dict[str, GenreGroup] = {g.id: g for g in ALL_GROUPS}

# Flat list of all genres (for open_format resolution)
_ALL_GENRES: list[GenreEntry] = [
    genre for group in ALL_GROUPS for genre in group.genres
]


def resolve_genre(
    group: GenreGroup,
    energy: float,
    time_of_night: TimeOfNight,
    section: Section,
    event_vibe: EventVibe = "underground",
) -> GenreEntry:
    """Select the best genre from a group based on current context.

    For open_format (empty genres), searches all groups.
    Selection is based on energy affinity, adjusted by time, section,
    and event vibe.

    Event vibe influence:
    - underground: slight downward shift (prefer deeper variants)
    - mainstream: slight upward shift (prefer catchier/brighter variants)
    - experimental: no shift (let energy decide)
    """
    candidates = group.genres if group.genres else _ALL_GENRES
    if not candidates:
        # Absolute fallback
        return HOUSE_PARTY.genres[0]

    # Adjust target energy based on context
    target = energy
    if time_of_night == "early":
        target -= 0.1
    elif time_of_night == "late":
        target -= 0.15
    if section in ("intro", "release"):
        target -= 0.1
    elif section == "peak":
        target += 0.1

    # Event vibe: underground prefers deeper, mainstream prefers catchier
    if event_vibe == "underground":
        target -= 0.05
    elif event_vibe == "mainstream":
        target += 0.05

    target = max(0.0, min(1.0, target))

    # Pick genre closest to target energy
    return min(candidates, key=lambda g: abs(g.energy_affinity - target))
