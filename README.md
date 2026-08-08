# halim — Voice Agent Monorepo

Reservoice voice agent'larının ortak deposu. Her müşteri/kullanım için `agents/`
altında bir klasör; STT/LLM/TTS yığını ve worker kurulumu `shared/` altında ortak.

## Kurulum

```bash
uv sync
cp .env.example .env      # anahtarları doldur
uv run python -m agents.demo_hotel.agent download-files   # turn-detector modelleri
```

## Çalıştırma

```bash
# mikrofonla yerel test (LiveKit odası gerekmez)
uv run python -m agents.demo_hotel.agent console

# LiveKit odasına bağlan (hot reload'lu geliştirme)
uv run python -m agents.demo_hotel.agent dev

# prod worker
uv run python -m agents.demo_hotel.agent start
```

## Yeni agent ekleme

```bash
uv run python scripts/new_agent.py ibis_merter --display "İbis Styles Merter"
```

Sonra `agents/ibis_merter/prompt.md` içine prompt'u, `config.yaml` içine ses ve
model ayarlarını yaz. Araçlar (`@function_tool`) `agent.py` içinde tanımlanır.

## Yapı

```
agents/<isim>/
  agent.py      Agent sınıfı + function_tool araçları
  prompt.md     sistem prompt'u (uzun metin YAML'a gömülmez, diff okunabilir kalsın)
  config.yaml   sağlayıcı seçimleri, karşılama cümlesi, agent'a özel `extra` alanları
shared/
  config.py     config.yaml + prompt.md okuma
  stack.py      sağlayıcı adı -> LiveKit plugin nesnesi
  runner.py     ortak worker entrypoint (oda bağlantısı, prewarm, CLI)
scripts/
  new_agent.py  iskelet üretici
```

Agent dosyaları LiveKit plugin'lerini doğrudan import etmez — sağlayıcı değişimi
`shared/stack.py`'de tek satırdır.

## Notlar

- Varsayılan yığın: Deepgram nova-3 (multi) STT, GPT-4o-mini LLM, ElevenLabs
  `eleven_turbo_v2_5` TTS, çok dilli turn detection.
- Türkçe TTS için ElevenLabs multilingual model şart; `voice_id`'yi agent bazında
  `config.yaml` içinde ver.
- Telefon (SIP) tarafı henüz bağlı değil.
