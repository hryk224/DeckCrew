"""Auto turn loop for autonomous DJ set progression.

Runs minor turns at regular intervals, with periodic major turns.
Genre changes trigger a pending major on the next turn.
Manual Next Turn resets the timer and runs an immediate major.

All turn execution is serialized via an asyncio Lock to prevent
concurrent turn execution between auto and manual triggers.
"""

import asyncio
import logging
import time

from deckcrew.agent.registry import create_agents, create_audiences, create_critic
from deckcrew.api.event_bus import EventBus
from deckcrew.memory.registry import memory_store
from deckcrew.music.base import MusicBackend
from deckcrew.orchestrator.conductor import Conductor
from deckcrew.orchestrator.config import DEFAULT_DIALOGUE_MODE, MAX_DELIBERATION_ROUNDS
from deckcrew.state.models import ChangeKind
from deckcrew.state.store import session_store

logger = logging.getLogger(__name__)

# Tuning constants
MINOR_INTERVAL_SEC = 150  # 2.5 minutes
MAJOR_EVERY_N_MINORS = 3  # auto major every 3 minors


class AutoTurnLoop:
    """Backend-managed auto turn loop.

    Start/stop lifecycle is tied to session Play/Stop.
    """

    def __init__(self) -> None:
        self._task: asyncio.Task[None] | None = None
        self._lock = asyncio.Lock()
        self._wake = asyncio.Event()
        self._minor_count = 0
        self._deadline = 0.0
        self._bus: EventBus | None = None
        self._music: MusicBackend | None = None

    @property
    def is_running(self) -> bool:
        return self._task is not None and not self._task.done()

    def start(self, bus: EventBus, music: MusicBackend) -> None:
        """Start the auto loop. Must be called after session is running."""
        if self.is_running:
            return
        self._bus = bus
        self._music = music
        self._minor_count = 0
        self._deadline = time.monotonic() + MINOR_INTERVAL_SEC
        self._wake.clear()
        self._task = asyncio.create_task(self._run())
        logger.info("[auto-loop] Started (interval=%ds, major every %d minors)",
                    MINOR_INTERVAL_SEC, MAJOR_EVERY_N_MINORS)

    async def stop(self) -> None:
        """Stop the auto loop."""
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except (asyncio.CancelledError, Exception):
                pass
            self._task = None
            logger.info("[auto-loop] Stopped")

    def reset_timer(self) -> None:
        """Reset the auto loop deadline (called after manual turn)."""
        self._minor_count = 0
        self._deadline = time.monotonic() + MINOR_INTERVAL_SEC
        self._wake.set()  # Break current sleep to recalculate

    async def run_manual_turn(self, kind: ChangeKind = "major",
                               max_rounds: int | None = None,
                               dialogue_mode: str | None = None) -> object:
        """Execute a manual turn with lock, then reset auto timer.

        Returns the TurnResult.
        """
        async with self._lock:
            result = await self._execute_turn(kind, max_rounds, dialogue_mode)
        self.reset_timer()
        return result

    async def _run(self) -> None:
        """Main loop: sleep until deadline, then execute a turn."""
        try:
            while True:
                # Sleep until deadline, waking early on reset
                now = time.monotonic()
                wait = max(0, self._deadline - now)
                if wait > 0:
                    self._wake.clear()
                    try:
                        await asyncio.wait_for(self._wake.wait(), timeout=wait)
                        # Woken early by reset — recalculate
                        continue
                    except TimeoutError:
                        pass  # Deadline reached, execute turn

                # Determine turn kind
                session = session_store.get_active()
                if session is None or session.status != "running":
                    logger.info("[auto-loop] Session not running, stopping loop")
                    break

                pending = session.pending_major
                if pending or self._minor_count >= MAJOR_EVERY_N_MINORS:
                    kind: ChangeKind = "major"
                    self._minor_count = 0
                else:
                    kind = "minor"
                    self._minor_count += 1

                # Execute with lock
                async with self._lock:
                    await self._execute_turn(kind)

                # Clear pending_major after major
                if pending:
                    session = session_store.get_active()
                    if session is not None:
                        updated = session.model_copy(update={"pending_major": False})
                        session_store.update(updated)

                # Set next deadline
                self._deadline = time.monotonic() + MINOR_INTERVAL_SEC

        except asyncio.CancelledError:
            logger.info("[auto-loop] Cancelled")
        except Exception:
            logger.exception("[auto-loop] Unexpected error")

    async def _execute_turn(self, kind: ChangeKind,
                            max_rounds: int | None = None,
                            dialogue_mode: str | None = None) -> object:
        """Run a single turn via Conductor."""
        session = session_store.get_active()
        if session is None or session.status != "running":
            return None

        rounds = max_rounds or MAX_DELIBERATION_ROUNDS
        mode = dialogue_mode or DEFAULT_DIALOGUE_MODE

        assert self._bus is not None and self._music is not None
        conductor = Conductor(
            agents=create_agents(),
            critic=create_critic(),
            audiences=create_audiences(),
            store=session_store,
            bus=self._bus,
            music=self._music,
            memory=memory_store,
        )
        try:
            result = await conductor.run_turn(session, kind=kind,
                                              max_rounds=rounds,
                                              dialogue_mode=mode)  # type: ignore[arg-type]
            logger.info("[auto-loop] Turn executed: kind=%s", kind)
            return result
        except Exception:
            logger.exception("[auto-loop] Turn failed")
            return None


# Singleton
auto_loop = AutoTurnLoop()
