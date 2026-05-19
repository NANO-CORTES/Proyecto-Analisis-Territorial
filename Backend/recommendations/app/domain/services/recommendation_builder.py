from __future__ import annotations

from typing import Iterable, List

from app.domain.entities import ZoneAnalytics, ZoneRecommendation

class RecommendationBuilder:
    STRENGTH_THRESHOLD = 0.7
    RISK_HIGH_THRESHOLD = 0.7
    RISK_LOW_THRESHOLD = 0.3

    LEVEL_HIGH = "Alta oportunidad"
    LEVEL_MEDIUM = "Media oportunidad"
    LEVEL_LOW = "Baja oportunidad"

    def build_many(self, zones: Iterable[ZoneAnalytics]) -> List[ZoneRecommendation]:
        return [self.build(z) for z in zones]

    def build(self, zone: ZoneAnalytics) -> ZoneRecommendation:
        strengths = self._strengths(zone)
        risks = self._risks(zone)
        level = self._level(zone)
        explanation = self._explanation(zone, strengths, risks, level)
        return ZoneRecommendation(
            zone_code=zone.zone_code,
            zone_name=zone.zone_name,
            recommendation_level=level,
            strengths=strengths,
            risks=risks,
            explanation=explanation,
        )

    def _strengths(self, zone: ZoneAnalytics) -> List[str]:
        items: List[str] = []
        if zone.score_value > self.STRENGTH_THRESHOLD:
            items.append("Score territorial alto: la zona destaca frente a la mayoria de territorios analizados.")
        if zone.population_indicator > self.STRENGTH_THRESHOLD:
            items.append("Alta densidad poblacional, mercado potencial relevante.")
        if zone.income_indicator > self.STRENGTH_THRESHOLD:
            items.append("Nivel de ingreso favorable, indica buena capacidad de compra.")
        if zone.education_indicator > self.STRENGTH_THRESHOLD:
            items.append("Perfil educativo alto, util para negocios especializados.")
        if zone.competition_indicator < self.RISK_LOW_THRESHOLD:
            items.append("Baja competencia: hay espacio para nuevos negocios.")
        if zone.prediction_value is not None and zone.prediction_value > self.STRENGTH_THRESHOLD:
            items.append("El modelo predictivo refuerza el potencial de la zona.")
        if not items:
            items.append("Sin fortalezas destacadas a partir de los indicadores actuales.")
        return items

    def _risks(self, zone: ZoneAnalytics) -> List[str]:
        items: List[str] = []
        if zone.competition_indicator > self.RISK_HIGH_THRESHOLD:
            items.append("Alta competencia: la zona ya esta saturada de oferta similar.")
        if zone.income_indicator < self.RISK_LOW_THRESHOLD:
            items.append("Bajo poder adquisitivo, puede limitar el ticket promedio esperado.")
        if zone.population_indicator < self.RISK_LOW_THRESHOLD:
            items.append("Poca poblacion: tamano de mercado limitado.")
        if zone.education_indicator < self.RISK_LOW_THRESHOLD:
            items.append("Bajo nivel educativo, puede no encajar con perfiles especializados.")
        if zone.prediction_value is not None and zone.prediction_value < self.RISK_LOW_THRESHOLD:
            items.append("El modelo predictivo proyecta bajo potencial en el corto plazo.")
        if not items:
            items.append("Sin riesgos relevantes detectados con los indicadores actuales.")
        return items

    def _level(self, zone: ZoneAnalytics) -> str:
        if zone.score_value > self.STRENGTH_THRESHOLD:
            return self.LEVEL_HIGH
        if zone.score_value >= 0.4:
            return self.LEVEL_MEDIUM
        return self.LEVEL_LOW

    def _explanation(
        self,
        zone: ZoneAnalytics,
        strengths: List[str],
        risks: List[str],
        level: str,
    ) -> str:
        prediction_text = ""
        if zone.prediction_value is not None:
            prediction_text = f" El modelo predictivo aporta un valor de {zone.prediction_value:.2f}."
        return (
            f"La zona {zone.zone_name} se clasifica como {level} con un score de "
            f"{zone.score_value:.2f}.{prediction_text} "
            f"Se identificaron {len(strengths)} fortalezas y {len(risks)} riesgos clave."
        )
