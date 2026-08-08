"""Demo otel resepsiyon agent'ı — yeni agent'lar için şablon.

Çalıştırmak için:
    uv run python -m agents.demo_hotel.agent console   # mikrofonla yerel test
    uv run python -m agents.demo_hotel.agent dev       # LiveKit odasına bağlanır
"""

from __future__ import annotations

import logging
from pathlib import Path

from livekit.agents import Agent, RunContext, function_tool

from shared import AgentConfig, run

logger = logging.getLogger("demo-hotel")

AGENT_DIR = Path(__file__).parent


class HotelReceptionist(Agent):
    def __init__(self, cfg: AgentConfig) -> None:
        super().__init__(instructions=cfg.instructions)
        self.hotel_name = cfg.extra.get("hotel_name", "otel")

    @function_tool
    async def check_availability(
        self,
        ctx: RunContext,
        check_in: str,
        check_out: str,
        guests: int,
    ) -> str:
        """Verilen tarihler için oda müsaitliğini kontrol eder.

        Args:
            check_in: Giriş tarihi, YYYY-MM-DD formatında.
            check_out: Çıkış tarihi, YYYY-MM-DD formatında.
            guests: Konuk sayısı.
        """
        # TODO: gerçek PMS/channel manager entegrasyonu buraya bağlanacak.
        logger.info("müsaitlik sorgusu: %s -> %s, %s kişi", check_in, check_out, guests)
        return (
            f"{check_in} - {check_out} arası {guests} kişilik standart oda müsait, gecelik 2500 TL."
        )

    @function_tool
    async def create_reservation(
        self,
        ctx: RunContext,
        full_name: str,
        phone: str,
        check_in: str,
        check_out: str,
        guests: int,
    ) -> str:
        """Rezervasyon kaydını oluşturur ve rezervasyon numarasını döndürür.

        Sadece konuk tüm bilgileri sözlü olarak teyit ettikten sonra çağrılmalı.

        Args:
            full_name: Konuğun ad ve soyadı.
            phone: İletişim telefon numarası.
            check_in: Giriş tarihi, YYYY-MM-DD formatında.
            check_out: Çıkış tarihi, YYYY-MM-DD formatında.
            guests: Konuk sayısı.
        """
        # TODO: gerçek rezervasyon API'sine yazılacak.
        logger.info("rezervasyon: %s (%s) %s -> %s", full_name, phone, check_in, check_out)
        return "Rezervasyon oluşturuldu. Rezervasyon numarası: DH-10432."


if __name__ == "__main__":
    run(AGENT_DIR, HotelReceptionist)
