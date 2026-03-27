"""In-memory implementation of MemoryStore.

Data is lost on process restart. Suitable for local development
and M4 initial implementation. Will be replaced by a persistent
backend (Zep Cloud / Supabase) when needed (M4-06).

Memory scope: local process context (single user, no auth).
"""

from deckcrew.memory.models import InterventionRecord, MemoryState, PreferenceProfile
from deckcrew.memory.profile import update_profile


class LocalMemoryStore:
    """In-memory memory store."""

    def __init__(self) -> None:
        self._state = MemoryState()

    async def load(self) -> MemoryState:
        return self._state

    async def save(self, state: MemoryState) -> None:
        self._state = state

    async def add_intervention(self, record: InterventionRecord) -> None:
        self._state.interventions.append(record)
        self._state.profile = update_profile(self._state.profile, record)

    async def get_profile(self) -> PreferenceProfile:
        return self._state.profile

    async def clear(self) -> None:
        self._state = MemoryState()
