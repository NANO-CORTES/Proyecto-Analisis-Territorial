from app.domain.entities import ZoneAnalytics
from app.domain.services.recommendation_builder import RecommendationBuilder

def _zone(**kw):
    base = dict(
        zone_code="Z",
        zone_name="Test",
        score_value=0.5,
        score_level="MEDIA",
        population_indicator=0.5,
        income_indicator=0.5,
        education_indicator=0.5,
        competition_indicator=0.5,
        prediction_value=None,
    )
    base.update(kw)
    return ZoneAnalytics(**base)

def test_high_score_zone_is_classified_as_high_opportunity_with_strengths():
    rec = RecommendationBuilder().build(
        _zone(score_value=0.9, population_indicator=0.85, income_indicator=0.85, competition_indicator=0.1)
    )
    assert rec.recommendation_level == RecommendationBuilder.LEVEL_HIGH
    assert any("alto" in s.lower() for s in rec.strengths)
    assert "Baja competencia" in " ".join(rec.strengths)

def test_low_competition_appears_as_strength_and_high_competition_as_risk():
    high_comp = RecommendationBuilder().build(_zone(competition_indicator=0.9))
    assert any("alta competencia" in r.lower() for r in high_comp.risks)

    low_comp = RecommendationBuilder().build(_zone(competition_indicator=0.1))
    assert any("baja competencia" in s.lower() for s in low_comp.strengths)

def test_low_income_appears_as_risk():
    rec = RecommendationBuilder().build(_zone(income_indicator=0.1))
    assert any("poder adquisitivo" in r.lower() for r in rec.risks)

def test_prediction_value_is_included_in_explanation_text():
    rec = RecommendationBuilder().build(_zone(score_value=0.6, prediction_value=0.81))
    assert "0.81" in rec.explanation
