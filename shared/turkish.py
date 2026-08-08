"""Türkçe sesli çıktı yardımcıları.

TTS rakamları güvenilir okumadığı için tool sonuçlarındaki sayıları yazıya
çeviriyoruz. Prompt de aynı kuralı söylüyor ama tool çıktısı LLM'e ham metin
olarak gittiği için burada garantiye alıyoruz.
"""

from __future__ import annotations

_BIRLER = ("", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz")
_ONLAR = ("", "on", "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan")
_BASAMAK = ((10**9, "milyar"), (10**6, "milyon"), (10**3, "bin"))


def _uc_hane(n: int) -> list[str]:
    parts: list[str] = []
    yuz, kalan = divmod(n, 100)
    if yuz:
        # "bir yüz" denmez, "yüz" denir
        parts.append("yüz" if yuz == 1 else f"{_BIRLER[yuz]} yüz")
    on, bir = divmod(kalan, 10)
    if on:
        parts.append(_ONLAR[on])
    if bir:
        parts.append(_BIRLER[bir])
    return parts


def sayi_yaziya(n: int) -> str:
    """Tam sayıyı Türkçe okunuşuna çevirir. 4200 -> 'dört bin iki yüz'."""
    if n == 0:
        return "sıfır"
    if n < 0:
        return "eksi " + sayi_yaziya(-n)

    parts: list[str] = []
    for deger, ad in _BASAMAK:
        bolum, n = divmod(n, deger)
        if not bolum:
            continue
        # "bir bin" denmez, "bin" denir; ama "bir milyon" denir
        if bolum == 1 and ad == "bin":
            parts.append("bin")
        else:
            parts.extend(_uc_hane(bolum))
            parts.append(ad)
    parts.extend(_uc_hane(n))
    return " ".join(parts)


def lira(n: int) -> str:
    """Tutarı sesli okunacak biçimde döndürür. 3990 -> 'üç bin dokuz yüz doksan lira'."""
    return f"{sayi_yaziya(n)} lira"
