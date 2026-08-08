"""Her agent'ın paylaştığı worker giriş noktası.

Agent dosyaları sadece kendi Agent sınıfını tanımlar; oda bağlantısı, prewarm ve
CLI kurulumu burada tek yerde durur.

DİKKAT: entrypoint modül seviyesinde bir fonksiyon olmak zorunda. LiveKit her
çağrı için ayrı bir işlem açıyor ve macOS'ta bu "spawn" ile oluyor — yani
entrypoint pickle ediliyor. `run()` içinde tanımlanan bir closure pickle
edilemez ve her çağrı "Can't pickle local object" ile düşer. Bu yüzden hangi
agent'ın çalışacağı bilgisi ortam değişkeniyle taşınıyor: ortam değişkenleri
alt işlemlere aktarılıyor, closure aktarılmıyor.
"""

from __future__ import annotations

import importlib
import inspect
import os
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

_DIR_ENV = "HALIM_AGENT_DIR"
_FACTORY_ENV = "HALIM_AGENT_FACTORY"


def _prewarm(proc: JobProcess) -> None:
    # VAD modelini worker açılışında yükle; ilk çağrının gecikmesini alır.
    proc.userdata["vad"] = silero.VAD.load()


def _load_factory(ref: str) -> Callable[[AgentConfig], Agent]:
    """ "paket.modul:SinifAdi" biçimindeki referansı çözer."""
    module_name, _, attr = ref.partition(":")
    return getattr(importlib.import_module(module_name), attr)


async def entrypoint(ctx: JobContext) -> None:
    cfg = AgentConfig.load(os.environ[_DIR_ENV])
    agent_factory = _load_factory(os.environ[_FACTORY_ENV])

    session = build_session(cfg, vad=ctx.proc.userdata.get("vad"))

    await session.start(
        room=ctx.room,
        agent=agent_factory(cfg),
        room_input_options=RoomInputOptions(),
    )
    await ctx.connect()

    if cfg.greeting:
        await session.say(cfg.greeting, allow_interruptions=True)


def _factory_ref(agent_factory: type[Agent]) -> str:
    """Sınıfı "paket.modul:SinifAdi" biçimine çevirir.

    `python -m agents.x.agent` ile çalıştırıldığında sınıfın __module__ değeri
    "__main__" oluyor; alt işlemde bu yanlış modülü gösterir. O durumda gerçek
    modül yolunu dosya konumundan üretiyoruz.
    """
    module = agent_factory.__module__
    if module == "__main__":
        kok = Path(__file__).resolve().parent.parent
        yol = Path(inspect.getfile(agent_factory)).resolve().relative_to(kok)
        module = ".".join(yol.with_suffix("").parts)
    return f"{module}:{agent_factory.__qualname__}"


def run(agent_dir: str | Path, agent_factory: type[Agent]) -> None:
    """Bir agent klasörünü LiveKit worker olarak çalıştırır."""
    agent_dir = Path(agent_dir).resolve()
    cfg = AgentConfig.load(agent_dir)

    # Alt işlemler bu iki değişkenden hangi agent olduklarını öğreniyor.
    os.environ[_DIR_ENV] = str(agent_dir)
    os.environ[_FACTORY_ENV] = _factory_ref(agent_factory)

    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=_prewarm,
            agent_name=cfg.name,
        )
    )
