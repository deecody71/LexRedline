"""Tests for the LexRedline Contract Engine."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models import Contract, Section, Clause, ClauseType, RiskLevel
from src.parsers.base import BaseParser
from src.analysis.clause_detector import ClauseDetector
from src.analysis.risk_scorer import RiskScorer
from src.analysis.redline_generator import RedlineGenerator
from src.analysis import ContractAnalyzer


def test_contract_model_creation():
    """Test basic Contract model."""
    contract = Contract(
        filename="test.pdf",
        file_type="pdf",
        full_text="Test contract text here."
    )
    assert contract.filename == "test.pdf"
    assert contract.file_type == "pdf"
    assert contract.full_text == "Test contract text here."
    assert contract.page_count is None


def test_section_model():
    """Test Section model with subsections."""
    sub = Section(heading="1.1 Subsection", level=2, content="Subsection content")
    main = Section(
        heading="1. Main Section",
        level=1,
        content="Main content",
        subsections=[sub]
    )
    assert main.heading == "1. Main Section"
    assert len(main.subsections) == 1
    assert main.subsections[0].heading == "1.1 Subsection"


def test_clause_model():
    """Test Clause model."""
    clause = Clause(
        clause_type=ClauseType.INDEMNIFICATION,
        section_ref="Section 6",
        text="Party shall indemnify...",
        confidence=0.85
    )
    assert clause.clause_type == ClauseType.INDEMNIFICATION
    assert clause.section_ref == "Section 6"
    assert clause.confidence == 0.85


def test_text_parsing():
    """Test parsing a text-based contract (simulated)."""
    contract = Contract(
        filename="sample_contract.txt",
        file_type="txt",
        full_text="""1. Definitions. This is a definition.
2. Payment Terms. Payment shall be net 30.
3. Indemnification. Party A shall indemnify Party B.
4. Limitation of Liability. Liability shall not exceed fees paid.
5. Termination. Either party may terminate.
6. Governing Law. Governed by Delaware law.
7. Confidentiality. Confidential information shall be protected.
8. Warranty. Warranted for 90 days.
"""
    )
    assert len(contract.full_text) > 50
    assert contract.file_type == "txt"


def test_clause_detection_basic():
    """Test clause detector with known text."""
    contract = Contract(
        filename="test.txt",
        file_type="txt",
        full_text="""1. Indemnification. The Provider shall indemnify and hold harmless the Client from any claims.
2. Limitation of Liability. Neither party's liability shall exceed the fees paid.
3. Governing Law. This Agreement shall be governed by the laws of Delaware.
4. Confidentiality. Each party shall protect the other's confidential information.
5. Termination. Either party may terminate this Agreement.
6. Force Majeure. Neither party shall be liable for acts of God.
7. Warranty. Provider warrants the services.
8. Assignment. Neither party may assign without consent.
9. Entire Agreement. This constitutes the entire agreement.
"""
    )

    detector = ClauseDetector()
    clauses = detector.detect(contract)

    detected_types = {c.clause_type for c in clauses}
    print(f"Detected clause types: {detected_types}")

    # Should detect most of these
    assert ClauseType.INDEMNIFICATION in detected_types, f"Missing INDEMNIFICATION in {detected_types}"
    assert ClauseType.LIMITATION_OF_LIABILITY in detected_types, f"Missing LIMITATION in {detected_types}"
    assert ClauseType.GOVERNING_LAW in detected_types, f"Missing GOV LAW in {detected_types}"
    assert ClauseType.CONFIDENTIALITY in detected_types, f"Missing CONFIDENTIALITY in {detected_types}"
    assert ClauseType.TERMINATION_FOR_CAUSE in detected_types or ClauseType.TERMINATION_FOR_CONVENIENCE in detected_types, f"Missing TERMINATION in {detected_types}"
    assert ClauseType.FORCE_MAJEURE in detected_types, f"Missing FORCE MAJEURE in {detected_types}"
    assert ClauseType.WARRANTY in detected_types, f"Missing WARRANTY in {detected_types}"
    assert ClauseType.ASSIGNMENT in detected_types, f"Missing ASSIGNMENT in {detected_types}"
    assert ClauseType.ENTIRE_AGREEMENT in detected_types, f"Missing ENTIRE AGREEMENT in {detected_types}"

    # Check confidence values are reasonable
    for c in clauses:
        assert 0.0 <= c.confidence <= 1.0, f"Invalid confidence: {c.confidence}"
        assert c.text, f"Empty text for clause type {c.clause_type}"

    print(f"All {len(clauses)} clauses detected correctly")


def test_risk_scoring():
    """Test risk scoring with known clauses."""
    clauses = [
        Clause(clause_type=ClauseType.INDEMNIFICATION, text="Provider shall indemnify and hold harmless Client from any and all claims at its sole discretion.", confidence=0.9),
        Clause(clause_type=ClauseType.LIMITATION_OF_LIABILITY, text="In no event shall either party be liable for any damages whatsoever.", confidence=0.9),
        Clause(clause_type=ClauseType.GOVERNING_LAW, text="This Agreement shall be governed by the laws of Delaware. The parties submit to the exclusive jurisdiction of the courts.", confidence=0.85),
        Clause(clause_type=ClauseType.CONFIDENTIALITY, text="Confidentiality obligations shall survive perpetually.", confidence=0.85),
        Clause(clause_type=ClauseType.TERMINATION_FOR_CAUSE, text="This Agreement may be terminated for cause only.", confidence=0.8),
        Clause(clause_type=ClauseType.WARRANTY, text="Services are provided AS IS without any warranty.", confidence=0.85),
    ]

    scorer = RiskScorer()
    risk_scores = scorer.score(clauses)

    assert len(risk_scores) == len(clauses)

    for rs in risk_scores:
        assert rs.clause_type in [c.clause_type for c in clauses]
        assert 0.0 <= rs.score <= 1.0
        assert rs.risk_level in list(RiskLevel)
        assert rs.reasoning, f"Missing reasoning for {rs.clause_type}"

    # High-risk clauses should score higher
    indemn_rs = [rs for rs in risk_scores if rs.clause_type == ClauseType.INDEMNIFICATION][0]
    assert indemn_rs.score >= 0.5, f"Indemnification risk too low: {indemn_rs.score}"

    liability_rs = [rs for rs in risk_scores if rs.clause_type == ClauseType.LIMITATION_OF_LIABILITY][0]
    assert liability_rs.score >= 0.5, f"Liability risk too low: {liability_rs.score}"

    print("Risk scoring tests passed")


def test_overall_risk():
    """Test overall risk computation."""
    clauses = [
        Clause(clause_type=ClauseType.INDEMNIFICATION, text="Indemnify at sole discretion all claims.", confidence=0.9),
        Clause(clause_type=ClauseType.LIMITATION_OF_LIABILITY, text="No liability for any damages.", confidence=0.9),
        Clause(clause_type=ClauseType.WARRANTY, text="AS IS without warranty.", confidence=0.85),
    ]

    scorer = RiskScorer()
    risk_scores = scorer.score(clauses)
    overall_level, overall_score = scorer.compute_overall_risk(clauses, risk_scores)

    assert 0.0 <= overall_score <= 1.0
    assert overall_level in list(RiskLevel)
    assert overall_score > 0.3, f"Overall risk should be elevated: {overall_score}"

    print(f"Overall risk: {overall_level.value} ({overall_score})")


def test_redline_generation():
    """Test redline generation."""
    clauses = [
        Clause(clause_type=ClauseType.INDEMNIFICATION, text="Provider shall indemnify at its sole discretion.", confidence=0.9),
        Clause(clause_type=ClauseType.LIMITATION_OF_LIABILITY, text="No liability for any damages.", confidence=0.9),
        Clause(clause_type=ClauseType.CONFIDENTIALITY, text="Confidentiality shall survive perpetually.", confidence=0.85),
    ]

    scorer = RiskScorer()
    risk_scores = scorer.score(clauses)

    generator = RedlineGenerator()
    redlines = generator.suggest(clauses, risk_scores)

    assert len(redlines) > 0
    for r in redlines:
        assert r.clause_type in [c.clause_type for c in clauses]
        assert r.original_text
        assert r.suggested_text
        assert r.priority in list(RiskLevel)
        assert r.risk_reason

    print(f"Generated {len(redlines)} redline suggestions")


def test_full_analysis_pipeline():
    """Test the complete analysis pipeline with a realistic contract."""
    contract = Contract(
        filename="test_agreement.txt",
        file_type="txt",
        full_text="""1. Definitions. "Confidential Information" means proprietary data.

2. Services. Provider shall deliver services as described in each SOW.

3. Payment. Client shall pay within Net 30 of invoice. Late payments accrue 1.5% monthly interest.

4. Term and Termination. This Agreement begins on the Effective Date and continues for two (2) years. Either party may terminate for any reason with 30 days notice. Either party may terminate for material breach with 30 days to cure.

5. Limitation of Liability. Neither party's aggregate liability shall exceed the total fees paid during the 12 months preceding the claim. This limitation does not apply to indemnification, confidentiality breaches, or IP infringement.

6. Indemnification. Provider shall indemnify Client against third-party claims arising from Provider's breach of this Agreement. Client shall indemnify Provider against claims arising from Client's breach.

7. Confidentiality. Each party shall protect the other's Confidential Information. These obligations survive for three (3) years after termination.

8. Governing Law. This Agreement is governed by the laws of New York. The parties consent to the exclusive jurisdiction of New York courts.

9. Warranties. Provider warrants services will be performed professionally. Provider warrants deliverables will conform to specifications for 90 days.

10. Force Majeure. Neither party is liable for delays caused by events beyond its reasonable control, including acts of God, war, or pandemic.

11. Entire Agreement. This Agreement is the entire agreement between the parties and supersedes all prior agreements.
"""
    )

    analyzer = ContractAnalyzer()
    result = analyzer.analyze(contract)

    assert result.clause_count > 0
    assert len(result.risk_scores) > 0
    assert result.overall_risk in list(RiskLevel)

    # Should detect these clauses
    detected_types = {c.clause_type for c in result.clauses}
    assert ClauseType.INDEMNIFICATION in detected_types
    assert ClauseType.LIMITATION_OF_LIABILITY in detected_types
    assert ClauseType.GOVERNING_LAW in detected_types
    assert ClauseType.CONFIDENTIALITY in detected_types
    assert ClauseType.TERMINATION_FOR_CAUSE in detected_types or ClauseType.TERMINATION_FOR_CONVENIENCE in detected_types, f"Missing TERMINATION in {detected_types}"
    assert ClauseType.FORCE_MAJEURE in detected_types
    assert ClauseType.WARRANTY in detected_types
    assert ClauseType.ENTIRE_AGREEMENT in detected_types

    # Analysis time should be reasonable
    assert result.analysis_time_ms < 5000, f"Analysis took too long: {result.analysis_time_ms}ms"

    print(f"Full pipeline: {result.clause_count} clauses detected in {result.analysis_time_ms:.1f}ms")
    print(f"Overall risk: {result.overall_risk.value} ({result.overall_risk_score})")
    print(f"Redlines generated: {len(result.redlines)}")


def test_sample_contract():
    """Test with the sample contract file."""
    sample_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample', 'sample_contract.txt')
    with open(sample_path, 'r') as f:
        text = f.read()

    contract = Contract(
        filename="sample_contract.txt",
        file_type="txt",
        full_text=text
    )

    analyzer = ContractAnalyzer()
    result = analyzer.analyze(contract)

    print(f"\n=== Sample Contract Analysis ===")
    print(f"Clauses detected: {result.clause_count}")
    print(f"Overall risk: {result.overall_risk.value} ({result.overall_risk_score})")
    print(f"Analysis time: {result.analysis_time_ms:.1f}ms")
    print(f"Redlines: {len(result.redlines)}")

    print("\nDetected clauses:")
    for c in result.clauses:
        print(f"  - {c.clause_type.value:30s} (conf: {c.confidence:.2f})")

    print("\nRisk scores:")
    for rs in result.risk_scores:
        print(f"  - {rs.clause_type.value:30s} {rs.risk_level.value:10s} ({rs.score:.2f})")

    print("\nRedline suggestions:")
    for r in result.redlines[:5]:
        print(f"  - [{r.priority.value}] {r.clause_type.value}: {r.risk_reason[:80]}...")

    assert result.clause_count >= 8  # Should detect most clauses
    assert len(result.redlines) > 0


if __name__ == "__main__":
    print("=== LexRedline Contract Engine Tests ===\n")

    test_contract_model_creation()
    print("✓ test_contract_model_creation")

    test_section_model()
    print("✓ test_section_model")

    test_clause_model()
    print("✓ test_clause_model")

    test_text_parsing()
    print("✓ test_text_parsing")

    test_clause_detection_basic()
    print("✓ test_clause_detection_basic")

    test_risk_scoring()
    print("✓ test_risk_scoring")

    test_overall_risk()
    print("✓ test_overall_risk")

    test_redline_generation()
    print("✓ test_redline_generation")

    test_full_analysis_pipeline()
    print("✓ test_full_analysis_pipeline")

    test_sample_contract()
    print("✓ test_sample_contract")

    print("\n=== All Tests Passed ===")