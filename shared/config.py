"""Agent config: her agent klasöründeki config.yaml + prompt.md dosyasını okur."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ProviderSpec:
    """Tek bir sağlayıcı seçimi: `provider` + o sağlayıcıya geçilecek kwargs."""

    provider: str
    options: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def parse(cls, raw: dict[str, Any] | None, default: str) -> ProviderSpec:
        raw = dict(raw or {})
        return cls(provider=raw.pop("provider", default), options=raw)


@dataclass(frozen=True)
class AgentConfig:
    name: str
    instructions: str
    greeting: str | None
    stt: ProviderSpec
    llm: ProviderSpec
    tts: ProviderSpec
    turn_detection: str
    extra: dict[str, Any]

    @classmethod
    def load(cls, agent_dir: str | Path) -> AgentConfig:
        """`agent_dir/config.yaml` ve `agent_dir/prompt.md` dosyalarından config kurar.

        Prompt her zaman prompt.md'den gelir — YAML içine uzun metin gömmüyoruz ki
        prompt değişiklikleri diff'te okunabilir kalsın.
        """
        agent_dir = Path(agent_dir)
        raw: dict[str, Any] = yaml.safe_load((agent_dir / "config.yaml").read_text("utf-8")) or {}

        return cls(
            name=raw.get("name", agent_dir.name),
            instructions=(agent_dir / "prompt.md").read_text("utf-8").strip(),
            greeting=raw.get("greeting"),
            stt=ProviderSpec.parse(raw.get("stt"), default="deepgram"),
            llm=ProviderSpec.parse(raw.get("llm"), default="openai"),
            tts=ProviderSpec.parse(raw.get("tts"), default="elevenlabs"),
            turn_detection=raw.get("turn_detection", "multilingual"),
            extra=raw.get("extra", {}),
        )
