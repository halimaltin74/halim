"""config.yaml'daki sağlayıcı isimlerini gerçek LiveKit plugin nesnelerine çevirir.

Yeni bir sağlayıcı eklemek = aşağıdaki fabrikalardan birine bir satır eklemek.
Agent kodlarının hiçbiri plugin'leri doğrudan import etmesin ki sağlayıcı
değişikliği tek yerden yapılabilsin.
"""

from __future__ import annotations

from typing import Any

from livekit.agents import AgentSession
from livekit.plugins import cartesia, deepgram, elevenlabs, openai, silero

from shared.config import AgentConfig, ProviderSpec


def _build_stt(spec: ProviderSpec):
    if spec.provider == "deepgram":
        # nova-3 çok dilli modda Türkçe'yi de kapsıyor; tek dile sabitlemek
        # istersen config'de language: tr ver.
        opts = {"model": "nova-3", "language": "multi", **spec.options}
        return deepgram.STT(**opts)
    if spec.provider == "openai":
        return openai.STT(**spec.options)
    raise ValueError(f"bilinmeyen STT sağlayıcısı: {spec.provider}")


def _build_llm(spec: ProviderSpec):
    if spec.provider == "openai":
        return openai.LLM(**{"model": "gpt-4o-mini", **spec.options})
    if spec.provider == "anthropic":
        from livekit.plugins import anthropic

        return anthropic.LLM(**spec.options)
    raise ValueError(f"bilinmeyen LLM sağlayıcısı: {spec.provider}")


def _build_tts(spec: ProviderSpec):
    if spec.provider == "elevenlabs":
        return elevenlabs.TTS(**spec.options)
    if spec.provider == "cartesia":
        return cartesia.TTS(**spec.options)
    if spec.provider == "openai":
        return openai.TTS(**spec.options)
    raise ValueError(f"bilinmeyen TTS sağlayıcısı: {spec.provider}")


def _build_turn_detection(kind: str):
    if kind == "multilingual":
        from livekit.plugins.turn_detector.multilingual import MultilingualModel

        return MultilingualModel()
    if kind == "english":
        from livekit.plugins.turn_detector.english import EnglishModel

        return EnglishModel()
    if kind in ("vad", "none"):
        return kind
    raise ValueError(f"bilinmeyen turn_detection: {kind}")


def build_session(cfg: AgentConfig, **overrides: Any) -> AgentSession:
    """Config'e göre STT/LLM/TTS/VAD yığınını kurulmuş bir AgentSession döndürür."""
    return AgentSession(
        stt=_build_stt(cfg.stt),
        llm=_build_llm(cfg.llm),
        tts=_build_tts(cfg.tts),
        vad=silero.VAD.load(),
        turn_detection=_build_turn_detection(cfg.turn_detection),
        **overrides,
    )
