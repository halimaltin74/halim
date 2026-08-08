"""Freya TTS (tts.freyavoice.ai) — OpenAI uyumlu API üzerinden.

Freya'nın TTS endpoint'i OpenAI'nin `/v1/audio/speech` sözleşmesini konuşuyor,
bu yüzden ayrı bir TTS sınıfı yazmaya gerek yok: LiveKit'in openai plugin'ini
Freya'ya yönlendiriyoruz.

İki tuzak var, ikisi de burada çözülü:

1. Freya'nın WAF'ı `User-Agent: OpenAI/Python ...` başlığını 403 ile blokluyor.
   OpenAI SDK'sı bu başlığı kendi koyduğu için `default_headers` ile eziyoruz.
2. Freya 48 kHz WAV döndürüyor, openai plugin'i 24 kHz bildiriyor. LiveKit'in
   AudioEmitter'ı WAV başlığını okuyup doğru resample ettiği için ses hızı
   bozulmuyor — bu yüzden `response_format` wav'da bırakılmalı. `pcm`'e
   geçersen başlık olmayacağı için ses yarı hızda çalar.
"""

from __future__ import annotations

import os
from typing import Any

import httpx
import openai as openai_sdk
from livekit.plugins import openai as lk_openai

DEFAULT_BASE_URL = "https://tts.freyavoice.ai/v1"
USER_AGENT = "reservoice-agent/1.0"

# API'nin kabul ettiği sesler (OpenAPI spec'inden).
VOICES = ("leyla", "zeynep", "alev", "ali", "alper", "mustafa")


def tts(**options: Any) -> lk_openai.TTS:
    """Freya'ya bağlı bir TTS örneği döndürür.

    Args:
        **options: `voice` (bkz. VOICES), `model` (tts-1 | tts-1-hd) ve
            `base_url` / `api_key` override'ları.
    """
    api_key = options.pop("api_key", None) or os.environ.get("FREYA_API_KEY")
    if not api_key:
        raise RuntimeError("FREYA_API_KEY tanımlı değil (.env dosyasına ekle)")

    base_url = options.pop("base_url", None) or os.environ.get("FREYA_BASE_URL") or DEFAULT_BASE_URL

    voice = options.pop("voice", "leyla")
    if voice not in VOICES:
        raise ValueError(f"geçersiz Freya sesi: {voice!r} — seçenekler: {', '.join(VOICES)}")

    client = openai_sdk.AsyncClient(
        max_retries=0,
        api_key=api_key,
        base_url=base_url,
        default_headers={"User-Agent": USER_AGENT},
        http_client=httpx.AsyncClient(
            # Freya streaming yapmıyor: tüm cümleyi tek seferde üretiyor, bu
            # yüzden read timeout'u openai plugin'inin 5 sn varsayılanından
            # yüksek tutuyoruz.
            timeout=httpx.Timeout(connect=15.0, read=30.0, write=5.0, pool=5.0),
            follow_redirects=True,
            limits=httpx.Limits(max_connections=50, max_keepalive_connections=50),
        ),
    )

    return lk_openai.TTS(
        model=options.pop("model", "tts-1"),
        voice=voice,
        response_format="wav",
        client=client,
        **options,
    )
