#!/usr/bin/env python3
"""Yeni agent iskeleti üretir.

uv run python scripts/new_agent.py ibis_merter --display "İbis Styles Merter"
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CONFIG = """\
name: {slug}
greeting: "İyi günler, {display}. Size nasıl yardımcı olabilirim?"

stt:
  provider: deepgram
  model: nova-3
  language: multi

llm:
  provider: openai
  model: gpt-4o-mini
  temperature: 0.4

tts:
  provider: elevenlabs
  model: eleven_turbo_v2_5
  language: tr

turn_detection: multilingual

extra:
  display_name: {display}
"""

PROMPT = """\
Sen {display} için çalışan bir telefon asistanısın. Türkçe konuşuyorsun.

## Rolün
TODO: agent'ın ne yaptığını yaz.

## Konuşma tarzı
- Kısa ve net cümleler kur.
- Sıcak ama profesyonel ol.
- Emin olmadığın bilgiyi uydurma; "kontrol edip dönelim" de.

## Akış
TODO: adım adım konuşma akışı.

## Sınırlar
- Ödeme bilgisi (kart numarası, CVV) asla isteme.
"""

AGENT = '''\
"""{display} agent'ı."""

from __future__ import annotations

import logging
from pathlib import Path

from livekit.agents import Agent

from shared import AgentConfig, run

logger = logging.getLogger("{slug}")

AGENT_DIR = Path(__file__).parent


class {cls}(Agent):
    def __init__(self, cfg: AgentConfig) -> None:
        super().__init__(instructions=cfg.instructions)


if __name__ == "__main__":
    run(AGENT_DIR, {cls})
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="klasör adı, snake_case (ör. ibis_merter)")
    parser.add_argument("--display", required=True, help="görünen ad (ör. İbis Styles Merter)")
    args = parser.parse_args()

    if not re.fullmatch(r"[a-z][a-z0-9_]*", args.name):
        parser.error("name snake_case olmalı: küçük harf, rakam ve alt çizgi")

    target = ROOT / "agents" / args.name
    if target.exists():
        parser.error(f"{target} zaten var")

    slug = args.name.replace("_", "-")
    cls = "".join(part.capitalize() for part in args.name.split("_")) + "Agent"
    fields = {"slug": slug, "display": args.display, "cls": cls}

    target.mkdir(parents=True)
    (target / "__init__.py").write_text("", "utf-8")
    (target / "config.yaml").write_text(CONFIG.format(**fields), "utf-8")
    (target / "prompt.md").write_text(PROMPT.format(**fields), "utf-8")
    (target / "agent.py").write_text(AGENT.format(**fields), "utf-8")

    print(f"oluşturuldu: agents/{args.name}")
    print(f"test:        uv run python -m agents.{args.name}.agent console")


if __name__ == "__main__":
    main()
