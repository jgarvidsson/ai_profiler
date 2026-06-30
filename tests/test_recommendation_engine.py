import pytest
from src.recommendation_engine import RecommendationEngine

def test_engine_initialization():
    engine = RecommendationEngine()
    assert engine is not None
    assert engine.available_ram >= 0
    assert engine.hardware is not None
    assert 'ram_gb' in engine.hardware

def test_assess_use_cases():
    engine = RecommendationEngine()
    model_technical = {
        'name': 'DeepSeek-Coder-6.7B',
        'tags': ['codificación', 'eficiente'],
        'description': 'Especializado en programación',
        'context': '128K'
    }
    uc = engine._assess_use_cases(model_technical)
    assert uc['technical']['suitable'] is True
    assert uc['vision']['suitable'] is False

def test_evaluate_models():
    engine = RecommendationEngine()
    results = engine.evaluate_models()
    assert len(results) > 0
    assert 'model' in results[0]
    assert 'compatibility' in results[0]
    assert 'use_cases' in results[0]

def test_get_recommendations():
    engine = RecommendationEngine()
    recs = engine.get_recommendations(top_n=3)
    assert len(recs) <= 3
    for rec in recs:
        assert 'model' in rec
        assert 'compatibility' in rec
        assert 'use_cases' in rec

def test_generate_report():
    engine = RecommendationEngine()
    report = engine.generate_report()
    assert isinstance(report, str)
    assert len(report) > 100
    assert "RECOMENDACIÓN" in report
