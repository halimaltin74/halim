"""config.yaml'daki sağlayıcı isimlerini gerçek LiveKit plugin nesnelerine çevirir.

Yeni bir sağlayıcı eklemek = aşağıdaki fabrikalardan birine bir satır eklemek.
Agent kodlarının hiçbiri plugin'leri doğrudan import etmesin ki sağlayıcı
değişikliği tek yerden yapılabilsin.
"""

from __future__ import annotations

from typing import Any

from livekit.agents import AgentSession

# turn_detector modül seviyesinde import edilmeli. Fonksiyon içinde import
# edilirse plugin kaydolmuyor ve `download-files` model dosyalarını atlıyor;
# sonuç olarak worker açılıyor ama gelen her çağrı "Could not find file
# languages.json" ile düşüyor.
from livekit.plugins import (  # noqa: F401
    cartesia,
    deepgram,
    elevenlabs,
    openai,
    silero,
    turn_detector,
)

from shared.config import AgentConfig, ProviderSpec


def _build_stt(spec: ProviderSpec):
    if spec.provider == "deepgram":
        # DİKKAT: language "multi" bırakılırsa Türkçe tanınmıyor — ölçümde
        # nova-3/multi konuşmayı Hintçe sanıp anlamsız metin döndürdü.
        # Dili açıkça "tr" sabitlemek şart; o haliyle nova-3 hem en doğru
        # hem en hızlı sonucu veriyor (~0.45 sn).
        opts = {"model": "nova-3", "language": "tr", **spec.options}
        return deepgram.STT(**opts)
    if spec.provider == "openai":
        return openai.STT(**spec.options)
    raise ValueError(f"bilinmeyen STT sağlayıcısı: {spec.provider}")


def _build_llm(spec: ProviderSpec):
    if spec.provider == "openai":
        return openai.LLM(**{"model": "gpt-4o-mini", **spec.options})
    if spec.provider == "anthropic":
        try:
            from livekit.plugins import anthropic
        except ImportError as e:
            raise RuntimeError(
                "anthropic sağlayıcısı için paket kurulu değil: uv add livekit-plugins-anthropic"
            ) from e

        return anthropic.LLM(**spec.options)
    raise ValueError(f"bilinmeyen LLM sağlayıcısı: {spec.provider}")


def _build_tts(spec: ProviderSpec):
    if spec.provider == "freya":
        from shared import freya

        return freya.tts(**spec.options)
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
    """Config'e göre STT/LLM/TTS/VAD yığınını kurulmuş bir AgentSession döndürür.

    `overrides` içinde verilen her alan config'ten üretilenin yerine geçer.
    Örneğin worker prewarm'da yüklenmiş bir VAD'ı `vad=...` ile geçirebilir;
    o durumda modeli yeniden yüklemeyiz.
    """
    kwargs: dict[str, Any] = {
        "stt": _build_stt(cfg.stt),
        "llm": _build_llm(cfg.llm),
        "tts": _build_tts(cfg.tts),
        "turn_detection": _build_turn_detection(cfg.turn_detection),
    }
    kwargs.update(overrides)
    kwargs.setdefault("vad", None)
    if kwargs["vad"] is None:
        kwargs["vad"] = silero.VAD.load()
    return AgentSession(**kwargs)
