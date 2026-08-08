"""Emirtimes Hotel Tuzla sesli resepsiyonisti.

Çalıştırmak için:
    uv run python -m agents.emirtimes.agent console   # mikrofonla yerel test
    uv run python -m agents.emirtimes.agent dev       # LiveKit odasına bağlanır

NOT: Henüz canlı tool bağlı değil. Müsaitlik, fiyat ve rezervasyon işlemleri
PMS/channel manager entegrasyonu gelene kadar resepsiyon ekibine aktarılıyor —
prompt da agent'a bunu söylüyor. Tool eklerken prompt'taki "CANLI SİSTEMLER"
bölümünü de güncelle, yoksa agent elindeki aracı kullanmayı reddeder.
"""

from __future__ import annotations

import logging
from pathlib import Path

from livekit.agents import Agent

from shared import AgentConfig, run

logger = logging.getLogger("emirtimes")

AGENT_DIR = Path(__file__).parent


class EmirtimesAgent(Agent):
    def __init__(self, cfg: AgentConfig) -> None:
        super().__init__(instructions=cfg.instructions)


if __name__ == "__main__":
    run(AGENT_DIR, EmirtimesAgent)
