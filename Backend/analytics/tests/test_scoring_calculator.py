from app.domain.entities import ZoneIndicators
from app.domain.services.score_classifier import ScoreClassifier
from app.domain.services.scoring_calculator import ScoringCalculator
from app.domain.value_objects import CombinedWeights, ScoringWeights

def _calc():
    return ScoringCalculator(ScoreClassifier())

def test_score_uses_weighted_formula_with_competition_penalty():
    weights = ScoringWeights(0.25, 0.25, 0.25, 0.25)
    indicators = [ZoneIndicators("Z1", "uno", population=1.0, income=1.0, education=1.0, competition=0.0)]
    [s] = _calc().calculate(indicators, weights)
    assert s.score_value == 0.75
    assert s.score_level.value == "ALTA"

def test_competition_subtracts_and_score_is_clamped_to_zero():
    weights = ScoringWeights(0.1, 0.1, 0.1, 0.9)
    indicators = [ZoneIndicators("Z2", "dos", population=0.1, income=0.1, education=0.1, competition=1.0)]
    [s] = _calc().calculate(indicators, weights)
    assert s.score_value == 0.0
    assert s.score_level.value == "BAJA"

def test_ranks_are_assigned_in_descending_order():
    weights = ScoringWeights.default()
    indicators = [
        ZoneIndicators("A", "a", population=0.1, income=0.1, education=0.1, competition=0.5),
        ZoneIndicators("B", "b", population=0.9, income=0.9, education=0.9, competition=0.1),
        ZoneIndicators("C", "c", population=0.5, income=0.5, education=0.5, competition=0.3),
    ]
    ranking = _calc().calculate(indicators, weights)
    codes = [s.zone_code for s in ranking]
    positions = [s.rank_position for s in ranking]
    assert codes == ["B", "C", "A"]
    assert positions == [1, 2, 3]

def test_combine_flags_high_discrepancy_between_score_and_prediction():
    weights = ScoringWeights.default()
    scores = _calc().calculate(
        [ZoneIndicators("Z", "z", population=0.8, income=0.8, education=0.8, competition=0.1)],
        weights,
    )
    enriched = _calc().combine(scores, predictions={"Z": 0.2}, weights=CombinedWeights(0.6, 0.4))
    z = enriched[0]
    assert z.prediction_value == 0.2
    assert z.combined_score is not None and 0.0 <= z.combined_score <= 1.0
    assert z.discrepancy_flag is True
