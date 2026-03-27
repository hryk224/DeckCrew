import asyncio

from deckcrew.api.events import SSEEvent


class EventBus:
    """Simple pub/sub event bus using asyncio.Queue.

    Subscribers receive SSEEvent instances via individual queues.
    Designed for single-process, in-memory use.
    """

    def __init__(self) -> None:
        self._subscribers: list[asyncio.Queue[SSEEvent]] = []

    def subscribe(self) -> asyncio.Queue[SSEEvent]:
        """Create and return a new subscriber queue."""
        queue: asyncio.Queue[SSEEvent] = asyncio.Queue()
        self._subscribers.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[SSEEvent]) -> None:
        """Remove a subscriber queue. Safe to call if already removed."""
        try:
            self._subscribers.remove(queue)
        except ValueError:
            pass

    async def publish(self, event: SSEEvent) -> None:
        """Send an event to all active subscribers.

        Silently drops events for full queues to avoid blocking.
        """
        dead: list[asyncio.Queue[SSEEvent]] = []
        for queue in self._subscribers:
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                dead.append(queue)
        # Clean up unresponsive subscribers
        for queue in dead:
            self.unsubscribe(queue)


# Singleton instance shared across the application.
event_bus = EventBus()
