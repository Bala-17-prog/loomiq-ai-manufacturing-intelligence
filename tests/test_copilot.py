import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base
from backend.ai.copilot import CopilotEngine
from backend.models.models import Machine, MachineMetric, QualityInspection, Production, Defect
from backend.ai.llm_provider import LLMProvider
from datetime import date, datetime

# Use an in-memory SQLite database for testing deterministic responses
@pytest.fixture(scope="module")
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    # Seed deterministic test data
    d = date(2026, 9, 1)
    m1 = Machine(machine_id="M-001", machine_name="Loom 1", department="Weaving", machine_type="Loom", installation_date=d, status="RUNNING")
    m2 = Machine(machine_id="M-017", machine_name="Loom 17", department="Weaving", machine_type="Loom", installation_date=d, status="WARNING")
    m3 = Machine(machine_id="M-012", machine_name="Loom 12", department="Weaving", machine_type="Loom", installation_date=d, status="RUNNING")
    db.add_all([m1, m2, m3])

    # Downtime data
    dt = datetime(2026, 9, 1, 0, 0, 0)
    db.add(MachineMetric(machine_id="M-001", downtime_minutes=120, vibration=10.0, temperature=40.0, energy_consumption=100.0, timestamp=dt, rpm=1000.0, running_hours=8.0))
    db.add(MachineMetric(machine_id="M-017", downtime_minutes=744, vibration=50.0, temperature=90.0, energy_consumption=200.0, timestamp=dt, rpm=1000.0, running_hours=8.0)) # 12.4 hours
    db.add(MachineMetric(machine_id="M-012", downtime_minutes=492, vibration=12.0, temperature=42.0, energy_consumption=105.0, timestamp=dt, rpm=1000.0, running_hours=8.0)) # 8.2 hours

    # Quality data
    db.add(QualityInspection(inspection_id="INS-1", original_image_path="test1.jpg", processed_image_path="test1.jpg", anomaly_score=0.1, result="PASS", severity="LOW"))
    db.add(QualityInspection(inspection_id="INS-2", original_image_path="test2.jpg", processed_image_path="test2.jpg", anomaly_score=0.9, result="REVIEW", severity="HIGH", potential_issue="Stain"))
    db.add(QualityInspection(inspection_id="INS-3", original_image_path="test3.jpg", processed_image_path="test3.jpg", anomaly_score=0.6, result="REVIEW", severity="MEDIUM", potential_issue="Tear"))

    # Production data
    db.add(Production(date=d, machine_id="M-001", shift="S1", fabric_type="Cotton", target_quantity=11000, actual_quantity=10000, efficiency=90.0))
    db.add(Defect(date=d, machine_id="M-001", fabric_type="Cotton", defect_type="Tear", severity="HIGH", quantity=150))

    db.commit()
    yield db
    db.close()

@pytest.fixture(autouse=True)
def disable_llm(monkeypatch):
    monkeypatch.setattr(LLMProvider, "is_available", lambda self: False)

def test_highest_downtime_intent(db_session):
    engine = CopilotEngine(db_session)
    # Using regex fallback or LLM, it should route correctly
    res1 = engine.ask("Which machine has the highest downtime?")
    assert "M-017" in res1["answer"]
    assert "12.4" in res1["answer"]
    assert res1["context_data"]["intent"] == "highest_downtime"
    assert res1["context_data"]["machine_id"] == "M-017"

    # Alternate phrasing
    res2 = engine.ask("Which machine has the most downtime?")
    assert "M-017" in res2["answer"]
    assert res2["context_data"]["intent"] == "highest_downtime"

def test_machine_risk_intent(db_session, monkeypatch):
    # Mock MachineService to return deterministic health scores for the test
    def mock_get_details(self, machine_id):
        if machine_id == "M-017":
            return {"machine_id": "M-017", "machine_name": "Loom 17", "status": "WARNING", "health": {"score": 45, "risk": "HIGH", "deviations": {"vibration": 0.5}}}
        return {"machine_id": machine_id, "machine_name": f"Loom {machine_id}", "status": "RUNNING", "health": {"score": 90, "risk": "LOW", "deviations": {}}}
    
    from backend.services.machine_service import MachineService
    monkeypatch.setattr(MachineService, "get_machine_details", mock_get_details)
    
    engine = CopilotEngine(db_session)
    
    # Test standard variation
    res = engine.ask("Which machine needs the most attention?")
    assert res["context_data"]["intent"] == "machine_risk"
    assert res["context_data"]["machine_id"] == "M-017"
    assert "factors" in res["context_data"]
    
    # Test the new natural language variations
    variants = [
        "Why is the highest-risk machine considered risky?",
        "Why is the highest risk machine risky?",
        "What makes the highest-risk machine risky?",
        "Why should I inspect the highest-risk machine?",
        "Why is this machine considered high risk?"
    ]
    for variant in variants:
        res = engine.ask(variant)
        assert res["context_data"]["intent"] == "machine_risk"

def test_percentage_formatting(db_session, monkeypatch):
    # Verify the formatting produces +8.88% or -8.88% and NEVER +-8.88%
    engine = CopilotEngine(db_session)
    
    def mock_get_details(*args):
        return {
            "machine_id": "M-017",
            "machine_name": "Loom 17",
            "status": "WARNING",
            "health": {
                "score": 45, 
                "risk": "HIGH", 
                "deviations": {
                    "vibration": {"deviation_pct": 8.88},
                    "temperature": {"deviation_pct": -8.88},
                    "energy": {"deviation_pct": 0.0}
                }
            }
        }
        
    from backend.services.machine_service import MachineService
    monkeypatch.setattr(MachineService, "get_machine_details", mock_get_details)
    
    # Disable LLM to hit Demo Engine formatter
    monkeypatch.setattr(engine.llm, "is_available", lambda: False)
    
    res = engine.ask("Which machine is at highest risk?")
    ans = res["answer"]
    
    assert "+8.88%" in ans
    assert "-8.88%" in ans
    assert "+0.00%" in ans or "0.00%" in ans
    assert "+-8.88%" not in ans
    
def test_production_summary(db_session):
    engine = CopilotEngine(db_session)
    res = engine.ask("Summarize today's production.")
    assert res["context_data"]["intent"] == "production_summary"
    assert res["context_data"]["production_quantity"] == 10000
    
def test_defect_rate_classification(db_session):
    engine = CopilotEngine(db_session)
    # Production Defect Rate
    res = engine.ask("What is the production defect rate?")
    assert res["context_data"]["intent"] == "defect_rate"
    assert res["context_data"]["total_production_units"] == 10000
    assert res["context_data"]["defective_units"] == 150
    assert res["context_data"]["defect_rate_percent"] == 1.5

def test_visual_inspection_classification(db_session):
    engine = CopilotEngine(db_session)
    # Visual Inspection Review Rate
    res = engine.ask("What is the visual inspection review rate?")
    assert res["context_data"]["intent"] == "visual_inspection"
    assert res["context_data"]["total_inspections"] == 3
    assert res["context_data"]["inspections_require_review"] == 2
    assert res["context_data"]["review_rate_percent"] == round((2/3)*100, 2)

def test_unknown_intent_fallback(db_session):
    engine = CopilotEngine(db_session)
    res = engine.ask("What is the meaning of life?")
    assert "Could you rephrase" in res["answer"]
    assert res["context_data"] is None

def test_llm_fallback_on_exception(db_session, monkeypatch):
    engine = CopilotEngine(db_session)
    
    # Mock LLM provider to throw an exception
    def mock_generate(*args, **kwargs):
        raise Exception("insufficient_quota")
        
    def mock_intent(*args, **kwargs):
        raise Exception("insufficient_quota")

    monkeypatch.setattr(engine.llm, "generate_explanation", mock_generate)
    monkeypatch.setattr(engine.llm, "determine_intent", mock_intent)
    # Ensure it's treated as available so the try/except block runs
    monkeypatch.setattr(LLMProvider, "is_available", lambda self: True)

    res = engine.ask("Which machine needs the most attention?")
    
    # Must fallback correctly
    assert res["mode"] == "demo"
    assert res["context_data"]["intent"] == "machine_risk"
    assert res["context_data"]["machine_id"] == "M-001" # because mock isn't applied here, M-001 is the default worst from baseline

def test_deterministic_consistency(db_session):
    engine = CopilotEngine(db_session)
    answers = [engine.ask("Which machine has the highest downtime?")["answer"] for _ in range(10)]
    assert len(set(answers)) == 1, "Expected identical deterministic responses"
