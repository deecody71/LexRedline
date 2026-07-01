"""Contract Expectations Matching Engine.

When a user types free-form expectations like "I need 30-day termination for convenience"
or "Liability cap should be at least $1M", this engine parses the expectations,
matches them against detected clauses, and returns a match analysis.
"""

import re
from typing import List, Dict, Tuple, Optional
from src.models import Clause, ClauseType

# Keyword-to-clause-type mapping for expectation parsing
EXPECTATION_KEYWORDS: Dict[str, List[ClauseType]] = {
    # Termination
    "termination": [ClauseType.TERMINATION_FOR_CONVENIENCE, ClauseType.TERMINATION_FOR_CAUSE],
    "cancel": [ClauseType.TERMINATION_FOR_CONVENIENCE],
    "exit": [ClauseType.TERMINATION_FOR_CONVENIENCE],
    "notice period": [ClauseType.TERMINATION_FOR_CAUSE],
    "cure period": [ClauseType.TERMINATION_FOR_CAUSE],
    "for cause": [ClauseType.TERMINATION_FOR_CAUSE],
    "for convenience": [ClauseType.TERMINATION_FOR_CONVENIENCE],
    "survival": [ClauseType.SURVIVAL],
    
    # Liability
    "liability cap": [ClauseType.LIMITATION_OF_LIABILITY],
    "limit": [ClauseType.LIMITATION_OF_LIABILITY],
    "damages": [ClauseType.LIMITATION_OF_LIABILITY],
    "cap": [ClauseType.LIMITATION_OF_LIABILITY],
    "exclusion": [ClauseType.LIMITATION_OF_LIABILITY],
    
    # Indemnification
    "indemnify": [ClauseType.INDEMNIFICATION],
    "indemnification": [ClauseType.INDEMNIFICATION],
    "hold harmless": [ClauseType.INDEMNIFICATION],
    
    # Confidentiality
    "confidential": [ClauseType.CONFIDENTIALITY],
    "nda": [ClauseType.CONFIDENTIALITY],
    "secret": [ClauseType.CONFIDENTIALITY],
    "non-disclosure": [ClauseType.CONFIDENTIALITY],
    "proprietary": [ClauseType.CONFIDENTIALITY],
    
    # Payment
    "payment": [ClauseType.PAYMENT_TERMS],
    "net 30": [ClauseType.PAYMENT_TERMS],
    "net 60": [ClauseType.PAYMENT_TERMS],
    "invoice": [ClauseType.PAYMENT_TERMS],
    "late payment": [ClauseType.INTEREST_ON_LATE_PAYMENTS],
    "late fee": [ClauseType.INTEREST_ON_LATE_PAYMENTS],
    "interest": [ClauseType.INTEREST_ON_LATE_PAYMENTS],
    
    # Data
    "data": [ClauseType.DATA_PROTECTION],
    "privacy": [ClauseType.DATA_PROTECTION],
    "gdpr": [ClauseType.DATA_PROTECTION],
    "ccpa": [ClauseType.DATA_PROTECTION],
    "personal data": [ClauseType.DATA_PROTECTION],
    "data breach": [ClauseType.DATA_PROTECTION],
    
    # Non-compete
    "non-compete": [ClauseType.NON_COMPETE],
    "noncompete": [ClauseType.NON_COMPETE],
    "restrictive covenant": [ClauseType.NON_COMPETE],
    
    # Governing law
    "governing law": [ClauseType.GOVERNING_LAW],
    "jurisdiction": [ClauseType.GOVERNING_LAW, ClauseType.DISPUTE_RESOLUTION_LITIGATION],
    "choice of law": [ClauseType.GOVERNING_LAW],
    
    # IP
    "ip": [ClauseType.INTELLECTUAL_PROPERTY],
    "intellectual property": [ClauseType.INTELLECTUAL_PROPERTY],
    "ownership": [ClauseType.INTELLECTUAL_PROPERTY],
    "copyright": [ClauseType.INTELLECTUAL_PROPERTY],
    "license": [ClauseType.INTELLECTUAL_PROPERTY],
    
    # Dispute resolution
    "arbitration": [ClauseType.DISPUTE_RESOLUTION_ARBITRATION],
    "mediation": [ClauseType.DISPUTE_RESOLUTION_MEDIATION],
    "dispute": [ClauseType.DISPUTE_RESOLUTION_ARBITRATION,
                 ClauseType.DISPUTE_RESOLUTION_MEDIATION,
                 ClauseType.DISPUTE_RESOLUTION_LITIGATION],
    
    # Warranty
    "warranty": [ClauseType.WARRANTY],
    "warrant": [ClauseType.WARRANTY],
    "as is": [ClauseType.DISCLAIMER],
    "disclaimer": [ClauseType.DISCLAIMER],
    
    # Assignment
    "assign": [ClauseType.ASSIGNMENT],
    "assignment": [ClauseType.ASSIGNMENT],
    
    # Force majeure
    "force majeure": [ClauseType.FORCE_MAJEURE],
    "act of god": [ClauseType.FORCE_MAJEURE],
    
    # Insurance
    "insurance": [ClauseType.INSURANCE],
    
    # Audit
    "audit": [ClauseType.AUDIT_RIGHTS],
    
    # Boilerplate
    "entire agreement": [ClauseType.ENTIRE_AGREEMENT],
    "integration": [ClauseType.ENTIRE_AGREEMENT],
    "severability": [ClauseType.SEVERABILITY],
    "waiver": [ClauseType.WAIVER],
    "notice": [ClauseType.NOTICE],
    "counterparts": [ClauseType.COUNTERPARTS],
    "amendment": [ClauseType.ENTIRE_AGREEMENT],
    
    # Commercial
    "exclusivity": [ClauseType.EXCLUSIVITY],
    "liquidated damages": [ClauseType.LIQUIDATED_DAMAGES],
    "most favored nation": [ClauseType.MOST_FAVORED_NATION],
    "mfn": [ClauseType.MOST_FAVORED_NATION],
    
    # Operational
    "deliverable": [ClauseType.DELIVERABLES],
    "sow": [ClauseType.DELIVERABLES],
    "statement of work": [ClauseType.DELIVERABLES],
    "subcontract": [ClauseType.SUBCONTRACTING],
    "publicity": [ClauseType.PUBLICITY],
    "compliance": [ClauseType.COMPLIANCE_WITH_LAWS],
    
    # Non-solicit
    "non-solicit": [ClauseType.NON_SOLICITATION],
    "non-solicitation": [ClauseType.NON_SOLICITATION],
    "no-poach": [ClauseType.NON_SOLICITATION],
}


class ExpectationMatcher:
    """
    Parses free-form user expectations and compares them against detected clauses.
    
    For each expectation in the user's text, it:
    1. Maps keywords to clause types
    2. Checks which clause types were detected in the contract
    3. Calculates a match percentage
    4. Identifies gaps and generates recommendations
    """

    def __init__(self):
        # Pre-compile keyword patterns for matching against detected clause types
        self._clause_type_labels: Dict[ClauseType, List[str]] = {}
        for keyword, clause_types in EXPECTATION_KEYWORDS.items():
            for ct in clause_types:
                if ct not in self._clause_type_labels:
                    self._clause_type_labels[ct] = []
                if keyword not in self._clause_type_labels[ct]:
                    self._clause_type_labels[ct].append(keyword)

    def parse_expectations(self, expectations_text: str) -> List[Dict]:
        """
        Parse free-form expectations text into structured expectations.
        
        Returns a list of dicts with:
        - keyword: the matched keyword
        - clause_types: the clause types it maps to
        - original_phrase: the surrounding text context
        """
        if not expectations_text or not expectations_text.strip():
            return []

        text_lower = expectations_text.lower()
        expectations = []
        found_keywords = set()

        # Sort keywords by length (longest first) so "governing law" matches before just "law"
        sorted_keywords = sorted(EXPECTATION_KEYWORDS.keys(), key=len, reverse=True)

        for keyword in sorted_keywords:
            if keyword in found_keywords:
                continue
            # Match as whole word or at word boundaries
            pattern = r'\b' + re.escape(keyword) + r'\b'
            matches = list(re.finditer(pattern, text_lower))
            for match in matches:
                start = max(0, match.start() - 40)
                end = min(len(text_lower), match.end() + 60)
                context = expectations_text[start:end].strip()
                expectations.append({
                    "keyword": keyword,
                    "clause_types": EXPECTATION_KEYWORDS[keyword],
                    "original_phrase": context,
                    "matched_clause_types": [ct.value for ct in EXPECTATION_KEYWORDS[keyword]],
                })
                found_keywords.add(keyword)
                break  # One match per keyword

        return expectations

    def match_against_clauses(self, expectations: List[Dict],
                               detected_clauses: List[Clause]) -> Dict:
        """
        Compare parsed expectations against detected clauses.
        
        Returns a match analysis:
        - total_expectations: count
        - matched: expectations that found a corresponding clause
        - unmatched: expectations not addressed by any clause
        - match_percentage: 0-100
        - matched_types: set of clause types that were both expected and detected
        - recommendations: suggestions for unmatched expectations
        """
        if not expectations:
            return {
                "total_expectations": 0,
                "matched": [],
                "unmatched": [],
                "match_percentage": 100.0,
                "matched_types": set(),
                "recommendations": [],
            }

        detected_types = {c.clause_type for c in detected_clauses}
        matched = []
        unmatched = []
        matched_types = set()

        for exp in expectations:
            # Check if any of the mapped clause types was detected
            expected_cts = [ct for ct in exp["clause_types"]
                           if ct != ClauseType.UNKNOWN]
            found = False
            for ct in expected_cts:
                if ct in detected_types:
                    found = True
                    matched_types.add(ct)
                    break

            entry = {
                "keyword": exp["keyword"],
                "phrase": exp["original_phrase"],
                "expected_types": [ct.value for ct in expected_cts],
            }

            if found:
                entry["status"] = "matched"
                matched.append(entry)
            else:
                entry["status"] = "unmatched"
                unmatched.append(entry)

        total = len(expectations)
        match_pct = round((len(matched) / total) * 100, 1) if total > 0 else 100.0

        # Generate recommendations for unmatched expectations
        recommendations = []
        for exp in unmatched:
            for ct in exp["clause_types"]:
                if ct == ClauseType.UNKNOWN:
                    continue
                ct_label = ct.value.replace("_", " ").title()
                recommendations.append(
                    f"'{exp['keyword']}' expected. Consider adding a '{ct_label}' clause."
                )

        return {
            "total_expectations": total,
            "matched": matched,
            "unmatched": unmatched,
            "match_percentage": match_pct,
            "matched_types": list(matched_types),
            "recommendations": recommendations,
        }

    def analyze(self, expectations_text: str, detected_clauses: List[Clause]) -> Dict:
        """
        Convenience method: parse expectations + match against clauses.
        Returns the full match analysis dict.
        """
        expectations = self.parse_expectations(expectations_text)
        return self.match_against_clauses(expectations, detected_clauses)