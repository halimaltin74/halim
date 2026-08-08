"""Emirtimes Hotel Tuzla sesli resepsiyonisti.

Çalıştırmak için:
    uv run python -m agents.emirtimes.agent console   # mikrofonla yerel test
    uv run python -m agents.emirtimes.agent dev       # LiveKit odasına bağlanır

DEMO HATTI: PMS'e bağlı değil. Müsaitlik sorgusu her zaman "müsait" döner ve
rezervasyon gerçek bir sisteme yazılmaz — sadece demo için onay üretir.
Gerçek entegrasyon gelince `musaitlik_kontrol` ve `rezervasyon_olustur`
gövdelerini değiştirmek yeterli; prompt tarafı aynı kalır.
"""

from __future__ import annotations

import logging
import random
from pathlib import Path

from livekit.agents import Agent, RunContext, function_tool

from shared import AgentConfig, run
from shared.turkish import lira, sayi_yaziya

logger = logging.getLogger("emirtimes")

AGENT_DIR = Path(__file__).parent

# İndirim merdiveni: ilk talepte yüzde beş, ısrar edilirse yüzde on, fazlası yok.
INDIRIM_ADIMLARI = (5, 10)


class EmirtimesAgent(Agent):
    def __init__(self, cfg: AgentConfig) -> None:
        super().__init__(instructions=cfg.instructions)
        # Konuşma boyunca kaç kez indirim verildiği. Rezervasyon tamamlanınca
        # sıfırlanır: aynı misafir ikinci bir oda alırsa merdiven baştan başlar.
        self._indirim_adimi = 0

    @function_tool
    async def musaitlik_kontrol(
        self,
        ctx: RunContext,
        giris_tarihi: str,
        cikis_tarihi: str,
        oda_tipi: str,
    ) -> str:
        """Verilen tarihler için oda müsaitliğini kontrol eder.

        Misafir tarih ve oda tipi belirttiğinde çağır. Sonucu almadan odanın
        müsait olduğunu söyleme.

        Args:
            giris_tarihi: Giriş tarihi, misafirin söylediği şekilde.
            cikis_tarihi: Çıkış tarihi, misafirin söylediği şekilde.
            oda_tipi: Misafirin istediği oda tipi.
        """
        logger.info("müsaitlik: %s %s-%s", oda_tipi, giris_tarihi, cikis_tarihi)
        return (
            f"{oda_tipi} için {giris_tarihi} - {cikis_tarihi} tarihleri müsait. "
            "Misafire müsait olduğunu söyleyebilirsin."
        )

    @function_tool
    async def indirim_uygula(self, ctx: RunContext, gecelik_fiyat: int) -> str:
        """Misafir indirim istediğinde çağır ve yeni fiyatı öğren.

        İndirim oranını sen belirleme, bu aracın döndürdüğü oranı kullan.

        Args:
            gecelik_fiyat: Odanın indirimsiz gecelik liste fiyatı, sayı olarak.
        """
        if self._indirim_adimi >= len(INDIRIM_ADIMLARI):
            return (
                "Bu rezervasyon için indirim hakkı doldu. Daha fazla indirim yapma; "
                "nazikçe bunun verebileceğin son fiyat olduğunu söyle."
            )

        oran = INDIRIM_ADIMLARI[self._indirim_adimi]
        self._indirim_adimi += 1
        yeni = round(gecelik_fiyat * (100 - oran) / 100)

        logger.info("indirim: %%%s -> %s", oran, yeni)
        return (
            f"Yüzde {sayi_yaziya(oran)} indirim uygulandı. "
            f"Yeni gecelik fiyat: {lira(yeni)}. "
            "Misafire bu indirimi otele doğrudan rezervasyon yaptığı için "
            "verebildiğini söyle."
        )

    @function_tool
    async def rezervasyon_olustur(self, ctx: RunContext, ad: str, soyad: str) -> str:
        """Rezervasyonu oluşturur. Sadece ad ve soyad ister, başka bilgi sorma.

        Misafir rezervasyonu onayladıktan sonra çağır.

        Args:
            ad: Misafirin adı.
            soyad: Misafirin soyadı.
        """
        kod = random.randint(1000, 9999)
        okunusu = ", ".join(sayi_yaziya(int(h)) for h in str(kod))

        # Yeni bir rezervasyona geçilirse indirim pazarlığı sıfırdan başlasın.
        self._indirim_adimi = 0

        logger.info("rezervasyon: %s %s -> %s", ad, soyad, kod)
        return (
            f"{ad} {soyad} adına rezervasyon oluşturuldu. "
            f"Rezervasyon numarası rakam rakam şöyle okunur: {okunusu}. "
            "Misafire numarayı bu şekilde söyle."
        )


if __name__ == "__main__":
    run(AGENT_DIR, EmirtimesAgent)
