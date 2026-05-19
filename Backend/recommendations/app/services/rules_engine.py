from typing import List, Tuple


# Umbrales definidos en la HU-25
SCORE_ALTA = 0.7
SCORE_BAJA = 0.4
COMPETITION_HIGH = 0.7
INCOME_LOW = 0.3
POPULATION_HIGH = 0.6
EDUCATION_HIGH = 0.6


class RulesEngine:
    """
    Motor de reglas para generar recomendaciones.
    SRP: solo contiene la lógica de reglas de negocio.
    OCP: se pueden agregar nuevas reglas sin modificar las existentes.
    Patrón Strategy: cada regla es independiente y combinable.
    """

    def evaluate(self, zone_data: dict) -> Tuple[List[str], List[str]]:
        """
        Evalúa las reglas y retorna (fortalezas, riesgos).
        zone_data debe tener: score_value, population_indicator,
        income_indicator, education_indicator, competition_indicator.
        """
        fortalezas = []
        riesgos = []

        score = zone_data.get("score_value", 0.0)
        population = zone_data.get("population_indicator", 0.0)
        income = zone_data.get("income_indicator", 0.0)
        education = zone_data.get("education_indicator", 0.0)
        competition = zone_data.get("competition_indicator", 0.0)

        # ── REGLAS DE FORTALEZA ───────────────────────────────────────────────

        if score > SCORE_ALTA:
            fortalezas.append(
                "Zona de alta oportunidad comercial con score territorial superior a 0.7."
            )

        if population > POPULATION_HIGH:
            fortalezas.append(
                "Alta densidad poblacional que garantiza una base sólida de clientes potenciales."
            )

        if income > 0.6:
            fortalezas.append(
                "Nivel de ingreso alto de sus habitantes, favoreciendo negocios de mayor valor agregado."
            )

        if education > EDUCATION_HIGH:
            fortalezas.append(
                "Alto nivel educativo de la población, ideal para servicios especializados y productos premium."
            )

        if competition < 0.3:
            fortalezas.append(
                "Baja competencia en el sector, lo que representa una ventana de oportunidad para nuevos negocios."
            )

        # ── REGLAS DE RIESGO ──────────────────────────────────────────────────

        if competition > COMPETITION_HIGH:
            riesgos.append(
                "Alta competencia: existen muchos negocios similares establecidos en la zona. "
                "Se requiere diferenciación clara del producto o servicio."
            )

        if income < INCOME_LOW:
            riesgos.append(
                "Bajo poder adquisitivo: el ingreso promedio de los habitantes es reducido, "
                "lo que puede limitar el ticket promedio de compra."
            )

        if score < SCORE_BAJA:
            riesgos.append(
                "Score territorial bajo: la combinación de indicadores no es favorable "
                "para la mayoría de tipos de negocio en este momento."
            )

        if education < 0.3:
            riesgos.append(
                "Bajo nivel educativo promedio, lo que puede reducir el mercado "
                "para servicios especializados o productos de alto valor."
            )

        if population < 0.3:
            riesgos.append(
                "Baja densidad poblacional, lo que puede limitar el volumen "
                "de clientes potenciales disponibles en la zona."
            )

        # Garantizar al menos una fortaleza y un riesgo (criterio de aceptación HU-25)
        if not fortalezas:
            fortalezas.append(
                "La zona presenta condiciones básicas para el establecimiento de negocios "
                "de primera necesidad y servicios comunitarios."
            )

        if not riesgos:
            riesgos.append(
                "Se recomienda monitorear periódicamente los indicadores de la zona "
                "para detectar cambios en las condiciones del mercado."
            )

        return fortalezas, riesgos

    def build_explanation(
        self,
        zone_name: str,
        score_value: float,
        level: str,
        fortalezas: List[str],
        riesgos: List[str],
    ) -> str:
        """
        Construye el texto explicativo general en lenguaje natural.
        """
        nivel_texto = {
            "ALTA": "alta oportunidad",
            "MEDIA": "oportunidad media",
            "BAJA": "baja oportunidad",
        }.get(level, "oportunidad no determinada")

        num_fortalezas = len(fortalezas)
        num_riesgos = len(riesgos)

        explanation = (
            f"{zone_name.capitalize()} es una zona de {nivel_texto} "
            f"con un score territorial de {score_value:.2f}. "
            f"El análisis identificó {num_fortalezas} fortaleza(s) y {num_riesgos} riesgo(s). "
        )

        if level == "ALTA":
            explanation += (
                "Las condiciones actuales son favorables para la apertura de nuevos negocios. "
                "Se recomienda avanzar con el plan de negocio teniendo en cuenta los riesgos identificados."
            )
        elif level == "MEDIA":
            explanation += (
                "Las condiciones son moderadas. Se recomienda evaluar cuidadosamente "
                "el tipo de negocio y su propuesta de valor antes de invertir."
            )
        else:
            explanation += (
                "Las condiciones actuales presentan desafíos significativos. "
                "Se recomienda considerar zonas alternativas o ajustar el modelo de negocio "
                "para adaptarse a las condiciones del mercado local."
            )

        return explanation