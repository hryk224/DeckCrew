"""Abstract interface for memory storage.

Implementations:
- LocalMemoryStore: in-memory, lost on restart (M4-01)
- Future: Zep Cloud or Supabase-backed store (M4-06)
"""

from typing import Protocol

from deckcrew.memory.models import InterventionRecord, MemoryState, PreferenceProfile


class MemoryStore(Protocol):
    """Interface for memory persistence.

    Conductor and API layers depend only on this protocol.
    """

    async def load(self) -> MemoryState:
        """Load the current memory state."""
        ...

    async def save(self, state: MemoryState) -> None:
        """Persist the full memory state."""
        ...

    async def add_intervention(self, record: InterventionRecord) -> None:
        """Append an intervention and update profile."""
        ...

    async def get_profile(self) -> PreferenceProfile:
        """Return the current preference profile."""
        ...

    async def clear(self) -> None:
        """Reset memory to empty state."""
        ...
