"""Analysis engine - coordinates clause detection, risk scoring, and redline generation."""

from typing import Optional
import time

from src.models import Contract, AnalysisResult
from src.analysis.clause_detector import ClauseDetector
from src.analysis.risk_scorer import RiskScorer
from src.analysis.redline_generator import RedlineGenerator
from src.analysis.preferences import PreferenceEngine
from src.analysis.expectation_matcher import ExpectationMatcher


class ContractAnalyzer:
    """Main analysis coordinator for the LexRedline engine."""

    def __init__(self, profile=None):
        self.detector = ClauseDetector()
        self.scorer = RiskScorer()
        self.generator = RedlineGenerator()
        self.preferences = PreferenceEngine(profile) if profile else None

    def analyze(self, contract, expectations: Optional[str] = None) -> AnalysisResult:
        start_time = time.time()

        # Step 1: Detect clauses
        clauses = self.detector.detect(contract)

        # Step 2: Score risks
        risk_scores = self.scorer.score(clauses)
        overall_risk, overall_score = self.scorer.compute_overall_risk(clauses, risk_scores)

        # Step 3: Generate redlines
        redlines = self.generator.generate(clauses, risk_scores)

        # Step 4: Match expectations
        expectation_match = None
        if expectations:
            matcher = ExpectationMatcher()
            expectation_match = matcher.analyze(expectations, clauses)

        result = AnalysisResult(
            contract=contract,
            clauses=clauses,
            risk_scores=risk_scores,
            overall_risk=overall_risk,
            overall_risk_score=overall_score,
            redlines=redlines,
            analysis_time_ms=round((time.time() - start_time) * 1000, 2),
            metadata={"source": "pattern_match"},
        )

        if expectation_match:
            result.metadata["expectation_match"] = expectation_match

        return result
