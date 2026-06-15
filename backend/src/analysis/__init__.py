"""Analysis engine - coordinates clause detection, risk scoring, and redline generation."""

from typing import Optional, List
import time

from src.models import Contract, Clause, AnalysisResult, RiskLevel
from src.analysis.clause_detector import ClauseDetector
from src.analysis.risk_scorer import RiskScorer
from src.analysis.redline_generator import RedlineGenerator


class ContractAnalyzer:
    """
    Main analysis coordinator for the LexRedline engine.
    
    Runs the full pipeline: clause detection → risk scoring → redline generation.
    """

    def __init__(self):
        self.detector = ClauseDetector()
        self.scorer = RiskScorer()
        self.generator = RedlineGenerator()

    def analyze(self, contract: Contract) -> AnalysisResult:
        """
        Run the full analysis pipeline on a parsed contract.

        Args:
            contract: Parsed Contract object.

        Returns:
            Complete AnalysisResult with clauses, risk scores, and redlines.
        """
        start_time = time.time()

        # Step 1: Detect clauses
        clauses = self.detector.detect(contract)

        # Step 2: Score each clause for risk
        risk_scores = self.scorer.score(clauses, contract)

        # Step 3: Compute overall risk
        overall_level, overall_score = self.scorer.compute_overall_risk(clauses, risk_scores)

        # Step 4: Generate redline suggestions
        redlines = self.generator.suggest(clauses, risk_scores) if risk_scores else []

        elapsed_ms = (time.time() - start_time) * 1000

        return AnalysisResult(
            contract=contract,
            clauses=clauses,
            risk_scores=risk_scores,
            overall_risk=overall_level,
            overall_risk_score=overall_score,
            redlines=redlines,
            clause_count=len(clauses),
            analysis_time_ms=round(elapsed_ms, 2)
        )