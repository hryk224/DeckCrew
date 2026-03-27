"""Predefined venue configurations.

Three presets covering distinct event scenarios.
UNDERGROUND_CLUB is the default for new sessions.
"""

from deckcrew.venue.models import VenueContext

UNDERGROUND_CLUB = VenueContext(
    room_size="club",
    crowd_density=0.7,
    time_of_night="peak_hours",
    event_vibe="underground",
)

FESTIVAL_MAIN = VenueContext(
    room_size="festival",
    crowd_density=0.9,
    time_of_night="peak_hours",
    event_vibe="mainstream",
)

INTIMATE_LOUNGE = VenueContext(
    room_size="intimate",
    crowd_density=0.4,
    time_of_night="late",
    event_vibe="experimental",
)

DEFAULT_VENUE = UNDERGROUND_CLUB
