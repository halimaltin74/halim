# CLAUDE.md

Voice agent monorepo'su. LiveKit Agents (Python 1.6.x), uv ile yönetiliyor.

## Komutlar

```bash
uv sync
uv run python -m agents.<isim>.agent console   # mikrofonla yerel test
uv run python -m agents.<isim>.agent dev       # LiveKit odası, hot reload
uv run python scripts/new_agent.py <snake_case> --display "Görünen Ad"
uv run ruff check . && uv run ruff format .
```

## Kurallar

- **Yeni agent = `scripts/new_agent.py`.** Var olan bir agent klasörünü elle
  kopyalama.
- **Agent dosyaları LiveKit plugin'lerini import etmez.** Sağlayıcı seçimi
  `config.yaml` içinde isimle yapılır, `shared/stack.py` onu nesneye çevirir.
  Yeni sağlayıcı eklerken sadece `shared/stack.py`'deki fabrikaya satır ekle.
- **Prompt'lar `prompt.md` içinde**, YAML'a veya Python string'ine gömülmez.
- **Yeni ortak davranış `shared/` altına gider**, agent'a kopyalanmaz. Agent
  klasöründe sadece o agent'a özgü prompt, config ve araçlar bulunur.
- Konuşma dili Türkçe: prompt'lar, greeting'ler ve kod yorumları Türkçe yazılır.
- Sırlar `.env` içinde, repoya girmez. `.env.example` her yeni anahtar için
  güncellenir.
- **Freya TTS'e dokunurken** `shared/freya.py` başındaki iki tuzağı oku: WAF
  `User-Agent: OpenAI/Python` başlığını 403'lüyor, ve `response_format` wav'dan
  çıkarsa ses yarı hızda çalar.

## Doğrulama

Agent değişikliğinden sonra en az config'in yüklendiğini kontrol et:

```bash
uv run python -c "from shared.config import AgentConfig; print(AgentConfig.load('agents/<isim>'))"
```

Gerçek sesli test `console` moduyla yapılır; API anahtarları gerekir.
