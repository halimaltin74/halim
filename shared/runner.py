"""Her agent'ın paylaştığı worker giriş noktası.

Agent dosyaları sadece kendi Agent sınıfını tanımlar; oda bağlantısı, prewarm ve
CLI kurulumu burada tek yerde durur.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    JobContext,
    JobProcess,
    RoomInputOptions,
    WorkerOptions,
    cli,
)
from livekit.plugins import silero

from shared.config import AgentConfig
from shared.stack import build_session

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def _prewarm(proc: JobProcess) -> None:
    # VAD modelini worker açılışında yükle; ilk çağrının gecikmesini alır.
    proc.userdata["vad"] = silero.VAD.load()


def run(agent_dir: str | Path, agent_factory: Callable[[AgentConfig], Agent]) -> None:
    """Bir agent klasörünü LiveKit worker olarak çalıştırır."""
    cfg = AgentConfig.load(agent_dir)

    async def entrypoint(ctx: JobContext) -> None:
        session = build_session(cfg, vad=ctx.proc.userdata.get("vad"))

        await session.start(
            room=ctx.room,
            agent=agent_factory(cfg),
            room_input_options=RoomInputOptions(),
        )
        await ctx.connect()

        if cfg.greeting:
            await session.say(cfg.greeting, allow_interruptions=True)

    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=_prewarm,
            agent_name=cfg.name,
        )
    )
