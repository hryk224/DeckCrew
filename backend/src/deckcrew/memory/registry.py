"""Memory store factory and singleton.

Swap LocalMemoryStore for a persistent implementation (Zep, Supabase)
by updating create_memory_store() in M4-06.
"""

from deckcrew.memory.base import MemoryStore
from deckcrew.memory.local import LocalMemoryStore


def create_memory_store() -> MemoryStore:
    """Create the memory store.

    Currently returns an in-memory implementation.
    """
    return LocalMemoryStore()


# Singleton instance shared across the application.
memory_store: MemoryStore = create_memory_store()
