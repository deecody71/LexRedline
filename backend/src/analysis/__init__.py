"""Analysis engine - coordinates clause detection, risk scoring, and redline generation."""

from typing import Optional, List, Dict, Any
import time

from src.models import Contract, Clause, AnalysisResult, RiskLevel, UserProfile
from src.analysis.clause_detector import ClauseDetector
from src.analysis.risk_scorer import RiskScorer
from src.analysis.redline_generator import RedlineGenerator
from src.analysis.preferences import PreferenceEngine
from src.analysis.expectation_matcher import ExpectationMatcher


class ContractAnalyzer:
    """
    Main analysis coordinator for the LexRedline engine.
    Runs the full pipeline: clause detection → risk scoring → redline generation.
    Optionally accepts a UserProfile for preference-aware analysis.
    """

    def __init__(self, profile: Optional[UserProfile] = None):
        self.detector = ClauseDetector()
        self.scorer = RiskScorer()
        self.generator = RedlineGenerator()
        self.preferences = PreferenceEngine(profile) if profile else PreferenceEngine()

    def analyze(self, contract: Contract, expectations: Optional[str] = None) -> AnalysisResult:
        """
        Run the full analysis pipeline on a parsed contract.
        """
        start_time = time.time()
        profile_modifications: List[str] = []

        # Step 1: Detect clauses
        clauses = self.detector.detect(contract)
        if self.preferences.get_priority_clauses():
            profile_modifications.append(f"Prioritized clauses: {', '.join(self.preferences.get_priority_clauses())}")

        # Step 2: Score risks
        risk_scores = self.scorer.score(clauses, preference_engine=self.preferences)
        overall_risk, overall_score = self.scorer.calculate_overall(risk_scores)

        # Step 2.5: Match expectations
        expectation_match = None
        if expectations:
            matcher = ExpectationMatcher()
            expectation_match = matcher.analyze(expectations, clauses)

        # Step 3: Generate redlines
        if self.preferences.profile and self.preferences.profile.is_active:
            redlines = self.preferences.select_redlines(risk_scores, self.generator)
            profile_modifications.append(f"Applied profile: {self.preferences.profile.role or 'custom'}")
        else:
            redlines = self.generator.generate(clauses, risk_scores)

        # Step 4: Apply risk modifiers
        risk_scores = self.scorer.apply_modifiers(risk_scores, self.preferences)
        overall_risk, overall_score = self.scorer.calculate_overall(risk_scores)

        # Build result
        result = AnalysisResult(
            contract=contract,
            clauses=clauses,
            risk_scores=risk_scores,
            overall_risk=overall_risk,
            overall_risk_score=overall_score,
            redlines=redlines,
            analysis_time_ms=round((time.time() - start_time) * 1000, 2),
            metadata={
                "profile_applied": self.preferences.profile is not None and self.preferences.profile.is_active,
                "profile_role": self.preferences.profile.role if self.preferences.profile else None,
                "profile_preferences": self.preferences.profile.preference_ids if self.preferences.profile else [],
                "profile_modifications": profile_modifications,
                "source": "pattern_match",
            },
        )

        if expectation_match:
            result.metadata["expectation_match"] = expectation_match

        return result
