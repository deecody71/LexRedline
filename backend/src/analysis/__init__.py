"""Analysis engine - coordinates clause detection, risk scoring, and redline generation."""

from typing import Optional, List, Dict, Any
import time

from src.models import Contract, Clause, AnalysisResult, RiskLevel, UserProfile
from src.analysis.clause_detector import ClauseDetector
from src.analysis.risk_scorer import RiskScorer
from src.analysis.redline_generator import RedlineGenerator
from src.analysis.preferences import PreferenceEngine


class ContractAnalyzer:
    """
    Main analysis coordinator for the LexRedline engine.
    
    Runs the full pipeline: clause detection → risk scoring → redline generation.
    Optionally accepts a UserProfile to preference-aware analysis.
    """

    def __init__(self, profile: Optional[UserProfile] = None):
        self.detector = ClauseDetector()
        self.scorer = RiskScorer()
        self.generator = RedlineGenerator()
        self.preferences = PreferenceEngine(profile) if profile else PreferenceEngine()

    def analyze(self, contract: Contract) -> AnalysisResult:
        """
        Run the full analysis pipeline on a parsed contract.

        Args:
            contract: Parsed Contract object.

        Returns:
            Complete AnalysisResult with clauses, risk scores, redlines, and profile info.
        """
        start_time = time.time()
        profile_modifications: List[str] = []

        # Step 1: Detect clauses (preferences can influence priorities)
        clauses = self.detector.detect(contract)
        if self.preferences.is_active:
            priority = self.preferences.get_priority_clauses()
            if priority:
                profile_modifications.append(f"Priority clauses: {[c.value for c in priority]}")

        # Step 2: Score each clause for risk
        risk_scores = self.scorer.score(clauses, contract)

        # Step 2b: Apply profile-driven risk modifiers
        if self.preferences.is_active:
            modifiers = self.preferences.get_risk_modifiers()
            if modifiers:
                modified_count = self.scorer.apply_modifiers(risk_scores, clauses, modifiers)
                profile_modifications.append(f"Risk modifiers applied to {modified_count} clause types")
                for ct, rules in modifiers.items():
                    for _, boost, desc in rules:
                        profile_modifications.append(f"  +{boost:.2f}: {desc}")

        # Step 3: Compute overall risk
        overall_level, overall_score = self.scorer.compute_overall_risk(clauses, risk_scores)

        # Step 4: Generate redline suggestions
        redline_prefs = self.preferences.get_redline_preferences() if self.preferences.is_active else {}
        redlines = self.generator.suggest(clauses, risk_scores) if risk_scores else []

        if redline_prefs and redlines:
            profile_modifications.append(f"Redline preferences active for {len(redline_prefs)} clause types")

        elapsed_ms = (time.time() - start_time) * 1000

        analysis_metadata: Dict[str, Any] = {}
        if self.preferences.is_active:
            analysis_metadata["profile_applied"] = True
            analysis_metadata["profile_role"] = self.preferences.profile.role if self.preferences.profile else None
            analysis_metadata["profile_preferences"] = self.preferences.profile.preference_ids if self.preferences.profile else []
            analysis_metadata["profile_modifications"] = profile_modifications

        return AnalysisResult(
            contract=contract,
            clauses=clauses,
            risk_scores=risk_scores,
            overall_risk=overall_level,
            overall_risk_score=overall_score,
            redlines=redlines,
            clause_count=len(clauses),
            analysis_time_ms=round(elapsed_ms, 2),
            metadata=analysis_metadata,
        )