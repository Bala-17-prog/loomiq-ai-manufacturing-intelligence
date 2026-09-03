from sqlalchemy.orm import Session
from backend.ai.llm_provider import LLMProvider
from backend.ai.demo_engine import DemoEngine
from backend.ai.prompts import INTENT_CLASSIFICATION_PROMPT, EXPLANATION_PROMPT
import re

class CopilotEngine:
    def __init__(self, db: Session):
        self.db = db
        self.llm = LLMProvider()
        self.demo = DemoEngine(db)

    def ask(self, query: str) -> dict:
        """
        Processes a natural language query, determines intent, fetches real data, 
        and formulates a deterministic response using facts and (optionally) LLM explanation.
        """
        # 1. Intent Detection
        intent = self._detect_intent(query)
        
        # 2. Fact Retrieval
        facts = {}
        if intent == "highest_downtime":
            facts = self.demo.get_highest_downtime()
        elif intent == "machine_risk":
            facts = self.demo.get_machine_risk()
        elif intent == "production_summary":
            facts = self.demo.get_production_summary()
        elif intent == "defect_rate":
            facts = self.demo.get_defect_rate()
        elif intent == "visual_inspection":
            facts = self.demo.get_visual_inspection_review_rate()
        elif intent == "machine_status":
            # For specific machines explicitly mentioned
            match = re.search(r'm-\d+', query.lower())
            if match:
                facts = self._get_machine_status(match.group(0).upper())
            else:
                intent = "unknown"
        else:
            intent = "unknown"

        # 3. Fallback
        if intent == "unknown" or "error" in facts:
            return {
                "answer": "I can help with production, machine health, downtime, quality inspections, maintenance, and shift comparisons. Could you rephrase your question?",
                "context_data": None
            }

        # 4. Response Generation
        answer = None
        mode = "demo"
        
        try:
            if self.llm.is_available():
                answer = self.llm.generate_explanation(EXPLANATION_PROMPT, query, facts)
                if answer:
                    mode = "llm"
        except Exception as e:
            # LLM provider failure: Log safe error and rely on deterministic fallback
            print(f"LLM provider unavailable; using deterministic fallback. Error: {e}")
            answer = None
            mode = "demo"
            
        # If LLM failed, returned None, or is disabled (Demo Mode), generate a deterministic response
        if not answer:
            answer = self._generate_deterministic_response(intent, facts)

        return {
            "answer": answer,
            "context_data": facts,
            "mode": mode
        }

    def _detect_intent(self, query: str) -> str:
        """
        Uses LLM to detect intent. Falls back to regex if LLM is unavailable.
        """
        if self.llm.is_available():
            try:
                llm_intent = self.llm.determine_intent(query, INTENT_CLASSIFICATION_PROMPT)
                if llm_intent in ["highest_downtime", "machine_risk", "production_summary", "defect_rate", "visual_inspection"]:
                    return llm_intent
            except Exception as e:
                print(f"Unable to determine Copilot intent using LLM provider. Error: {e}")
                
        # Regex fallback for deterministic Demo Mode
        query_lower = query.lower()
        if "highest downtime" in query_lower or "most downtime" in query_lower or "maximum downtime" in query_lower:
            return "highest_downtime"
        if "most attention" in query_lower or "highest risk" in query_lower or "worst condition" in query_lower or "maintenance attention" in query_lower or "risky" in query_lower or "high risk" in query_lower or "riskiest" in query_lower or "highest-risk" in query_lower or "machine health" in query_lower or "machine warnings" in query_lower:
            return "machine_risk"
        if ("summarize" in query_lower and "production" in query_lower) or "total production" in query_lower or "production achievement" in query_lower or "shift comparison" in query_lower:
            return "production_summary"
        if "defect rate" in query_lower:
            if "production" in query_lower:
                return "defect_rate"
            return "defect_rate" # default to production defect rate if unspecified
        if "review rate" in query_lower or "inspections require review" in query_lower or "quality inspection" in query_lower:
            return "visual_inspection"
        if re.search(r'm-\d+', query_lower):
            return "machine_status"
            
        return "unknown"

    def _get_machine_status(self, machine_id: str):
        from backend.services.machine_service import MachineService
        svc = MachineService(self.db)
        details = svc.get_machine_details(machine_id)
        if not details:
            return {"error": f"Machine {machine_id} not found."}
        return details

    def _generate_deterministic_response(self, intent: str, facts: dict) -> str:
        """
        Generates a hard-coded response based purely on the retrieved facts if the LLM is not available.
        """
        if intent == "highest_downtime":
            return f"Machine **{facts.get('machine_id')}** has the highest downtime at **{facts.get('downtime_hours')} hours** for the selected period."
            
        if intent == "machine_risk":
            factors_str = ", ".join([f"{f['metric']} ({f['deviation_percent']:+.2f}%)" for f in facts.get('factors', [])])
            return f"Machine **{facts.get('machine_id')}** ({facts.get('machine_name')}) is currently the highest-risk machine with a health score of **{facts.get('health_score')}/100** and **{facts.get('risk_level')}** risk. The main contributing factors are: {factors_str} relative to baseline."
            
        if intent == "production_summary":
            return f"For the latest production day ({facts.get('date')}), the factory produced **{facts.get('production_quantity'):,}** units against a target of **{facts.get('target_quantity'):,}** units. This represents a **{facts.get('achievement_percent')}%** achievement rate with an overall efficiency of **{facts.get('efficiency_percent')}%**."
            
        if intent == "defect_rate":
            return f"The {facts.get('metric_name')} is currently **{facts.get('defect_rate_percent')}%** ({facts.get('defective_units'):,} defective units out of {facts.get('total_production_units'):,} total units produced)."
            
        if intent == "visual_inspection":
            return f"To date, **{facts.get('total_inspections')}** visual inspections have been recorded by the OpenCV pipeline. **{facts.get('inspections_require_review')}** inspections require review (Result: REVIEW), giving a **{facts.get('metric_name')}** of **{facts.get('review_rate_percent')}%**."
            
        if intent == "machine_status":
            health = facts.get("health", {})
            return f"Machine **{facts.get('machine_id')}** is currently **{facts.get('status')}**. Health Score: {health.get('score')}/100 (Risk: {health.get('risk')})."
            
        return "I have retrieved the requested data but cannot format it currently."
