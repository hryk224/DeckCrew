"""Meeting context for multi-round deliberation.

Shared context that accumulates all agent messages across rounds.
Each agent can read the full conversation history to inform its
next contribution.

Dialogue modes:
  - structured: fixed round count, fixed speaker order per round
  - semi_free: DJ speaker order determined dynamically per round,
    Critic/Audience remain at round boundaries

Future scope: full free-form autonomous dialogue
  - All agents decide when to speak and when to yield
  - Convergence conditions are self-determined
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

AgentRole = Literal["dj", "critic", "audience"]
DialogueMode = Literal["structured", "semi_free"]


class MeetingMessage(BaseModel):
    """A single message in the meeting context."""

    speaker: str
    role: AgentRole
    round: int
    content: str
    data: dict[str, Any] | None = None


class MeetingContext(BaseModel):
    """Shared conversation context across deliberation rounds."""

    messages: list[MeetingMessage] = Field(default_factory=list)
    current_round: int = 1
    total_rounds: int = 1
    mode: DialogueMode = "structured"

    def add(
        self,
        speaker: str,
        role: AgentRole,
        content: str,
        data: dict[str, Any] | None = None,
    ) -> None:
        """Append a message from the current round."""
        self.messages.append(
            MeetingMessage(
                speaker=speaker,
                role=role,
                round=self.current_round,
                content=content,
                data=data,
            )
        )

    def format_log(self) -> str:
        """Format the meeting history as text for LLM prompts."""
        if not self.messages:
            return ""
        lines: list[str] = []
        current_round = 0
        for msg in self.messages:
            if msg.round != current_round:
                current_round = msg.round
                lines.append(f"\n[Round {current_round}]")
            lines.append(f"  {msg.speaker} ({msg.role}): {msg.content}")
        return "\n".join(lines)
