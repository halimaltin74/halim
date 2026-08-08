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
  freya.py      Freya TTS (OpenAI uyumlu API üzerinden)
  turkish.py    sayı -> Türkçe okunuş (tool çıktılarındaki tutarlar için)
scripts/
  new_agent.py  iskelet üretici
```

Agent dosyaları LiveKit plugin'lerini doğrudan import etmez — sağlayıcı değişimi
`shared/stack.py`'de tek satırdır.

## Notlar

- Varsayılan yığın: Deepgram nova-3 (`language: tr`) STT, GPT-4o-mini LLM,
  **Freya** TTS, çok dilli turn detection.

### Deepgram STT — `language` mutlaka `tr` olmalı

Üç Türkçe cümleyle ölçüldü (aynı ses dosyaları, aynı koşullar):

| Ayar | Doğruluk | Gecikme |
|---|---|---|
| `nova-3` + `language: multi` | **kullanılamaz** — konuşmayı Hintçe sanıp anlamsız metin döndürdü | 0.3-1.7s |
| `nova-2` + `language: tr` | iyi, 3 cümlede 1 kelime hatası | 1.2-2.3s |
| `nova-3` + `language: tr` | **3/3 tam doğru** | 0.41-0.47s |

nova-3 Türkçe'yi destekliyor ama sadece dil açıkça verilince; `multi` modunun
dil listesinde Türkçe yok. Varsayılan bu yüzden `nova-3` + `tr`.

Freya'nın kendi ASR'ı da denendi: doğruluğu benzer ve sayıları rakama çeviriyor
(`iki bin beş yüz lira` → `2.500 lira`), ki LLM için okuması daha kolay. Ama
dosya yükleme endpoint'i — streaming yok. Gerçek zamanlı çağrıda kullanmak için
VAD ile parçalama gerekir ve gecikme artar, o yüzden STT'de Deepgram'da kalındı.

### Freya TTS

OpenAI uyumlu API (`tts.freyavoice.ai/v1/audio/speech`), ayrı plugin yok —
`shared/freya.py` LiveKit'in openai plugin'ini Freya'ya yönlendiriyor.

- Sesler: `leyla`, `zeynep`, `alev`, `ali`, `alper`, `mustafa`
- Model: `tts-1` (hızlı) veya `tts-1-hd` (kaliteli)
- **Gecikme**: streaming yok, cümle tamamlanmadan ses başlamıyor. Ölçüm:
  TTFB kısa cümlede ~1.0-1.2 sn, uzun cümlede ~1.9 sn. Telefonda her yanıttan
  önce ~1 saniye sessizlik demek (ElevenLabs turbo'da bu ~0.3 sn).
- `response_format` **wav'da kalmalı** — `pcm`'e geçilirse ses yarı hızda çalar
  (openai plugin'i 24 kHz varsayıyor, Freya 48 kHz gönderiyor; doğru resample
  sadece WAV başlığı varken oluyor).

Telefon (SIP) tarafı henüz bağlı değil.
