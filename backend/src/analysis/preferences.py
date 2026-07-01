"""Preference engine that loads user profiles and applies them to the analysis pipeline.

Reads the profile_preferences.json spec and resolves which clause types
get priority, which risk thresholds shift, and which redline templates to use.
"""

import json
import re
from typing import List, Dict, Optional, Set, Tuple
from pathlib import Path

from src.models import ClauseType
from src.models.profile import UserProfile


PROFILE_SPEC_PATH = Path("/home/team/shared/profile_preferences.json")


class PreferenceEngine:
    """
    Loads and applies user profile preferences to the analysis pipeline.
    
    Maps preference IDs to concrete actions via a lookup table derived from
    the profile_preferences.json spec. This keeps profile logic data-driven
    rather than hardcoded.
    """

    # Mapping of preference IDs to regex patterns that should trigger risk boosts
    # Derived from risk_threshold_shift descriptions in the spec
    BOOST_RULES: Dict[str, List[Tuple[str, float, str]]] = {
        # --- Reviewer preferences ---
        "liability_financial": [
            (r'(uncapped|unlimited).*(liability|indemnif)', 0.3, "No liability cap (profile: critical)"),
            (r'(one[\-]?sided|unilateral).*(liability|limit)', 0.2, "One-sided liability (profile: high)"),
            (r'Net\s+(60|90|120)', 0.2, "Extended payment terms (profile: high)"),
        ],
        "indemnity_insurance": [
            (r'unilateral.*(indemnif|indemnit)', 0.15, "Unilateral indemnity (profile: elevated)"),
            (r'(no|missing|without).*(notice|defen[ds]e).*claim', 0.15, "Missing notice/defense (profile: medium)"),
        ],
        "ip_ownership": [
            (r'vendor\s+owns.*(everything|all\s+right)', 0.3, "Vendor owns all IP (profile: critical)"),
            (r'joint\s+ownership', 0.2, "Joint ownership (profile: high)"),
        ],
        "data_privacy": [
            (r'(no|not|without).*(DPA|data\s+processing)', 0.3, "Missing DPA (profile: critical)"),
            (r'(no|not|without).*(notification|notif).*(breach|\d+.*hour)', 0.3, "Missing breach notification (profile: critical)"),
        ],
        "exit_rights": [
            (r'unilateral.*(vendor|provider).*(terminat.*convenience)', 0.2, "Vendor-only termination (profile: high)"),
            (r'(no\s+)?refund.*(no\s+)?(pre[\-]?paid|unused)', 0.15, "No pre-paid refund (profile: medium)"),
        ],
        "restrictive_covenants": [
            (r'(12|twelve)\s*month.*(non[\-]?compete|non[\-]?solicit)', 0.3, "12+ month restriction (profile: critical)"),
            (r'(broad|any\s+business|global|worldwide).*(non[\-]?compete)', 0.25, "Overbroad non-compete (profile: critical)"),
        ],
        "legal_governance": [
            (r'foreign.*(law|jurisdiction|court)', 0.3, "Foreign jurisdiction (profile: critical)"),
            (r'(Alabama|Mississippi|Arkansas|Montana)', 0.2, "Unfavorable hub (profile: high)"),
        ],
        "business_continuity": [
            (r'absolute.*(prohib|forbid).*(assign|transfer)', 0.2, "Absolute no-assignment (profile: high)"),
        ],
        # --- Creator preferences ---
        "aggressive_provisions": [
            (r'sole\s+discretion', 0.2, "Sole discretion (profile: high)"),
            (r'(absolute|100|perfect|flawless).*(perform|warrant)', 0.2, "Absolute performance (profile: high)"),
        ],
        "missing_protective_boilerplate": [
            (r'(no|missing|absent).*(entire\s+agreement|integration|merger)', 0.15, "Missing entire agreement (profile: medium)"),
            (r'(no|missing|absent).*severab', 0.1, "Missing severability (profile: medium)"),
        ],
        "market_deviation": [
            (r'Net\s+(90|120)', 0.15, "Extended terms deviation (profile: medium)"),
            (r'(perpetual|indefinite).*confidential', 0.15, "Indefinite confidentiality (profile: medium)"),
        ],
        "negotiation_friction": [
            (r'unlimited.*audit|audit.*without\s+notice', 0.2, "Unlimited audit (profile: high)"),
        ],
        "clarity_scope": [
            (r'(circular|ambiguous|unclear).*(precedence|hierarchy)', 0.1, "Unclear precedence (profile: medium)"),
        ],
        "overbroad_covenants": [
            (r'(global|worldwide|anywhere)', 0.2, "Global scope restriction (profile: high)"),
        ],
        "compliance_audit_gaps": [
            (r'unilateral.*complian|audit.*(pays?|bear).*(all|always)', 0.15, "Unfair audit cost (profile: medium)"),
        ],
        "document_consistency": [
            (r'(no|unclear|lack).*(hierarchy|precedence)', 0.1, "Missing hierarchy (profile: medium)"),
        ],
    }

    def __init__(self, profile: Optional[UserProfile] = None):
        self.profile = profile
        self._spec: Optional[dict] = None

    @property
    def is_active(self) -> bool:
        return self.profile is not None and self.profile.is_active

    def _load_spec(self) -> dict:
        """Load the profile preferences JSON spec."""
        if self._spec is None:
            with open(PROFILE_SPEC_PATH, 'r') as f:
                self._spec = json.load(f)
        return self._spec

    def get_priority_clauses(self) -> Set[ClauseType]:
        """Return clause types that should get elevated detection priority."""
        if not self.is_active:
            return set()

        spec = self._load_spec()
        priority_clauses: Set[ClauseType] = set()

        # Determine which role's preferences to load
        role_key = f"{self.profile.role}_preferences" if self.profile.role in ("reviewer", "creator") else None
        # Also check "both" role
        roles_to_check = []
        if self.profile.role == "both":
            roles_to_check = ["reviewer_preferences", "creator_preferences"]
        elif role_key:
            roles_to_check = [role_key]

        for role in roles_to_check:
            prefs_list = spec.get(role, [])
            for pref in prefs_list:
                pref_id = pref.get("id", "")
                if pref_id in self.profile.preference_ids:
                    for clause_name in pref.get("priority_clauses", []):
                        # Map clause name string to ClauseType enum (lenient matching)
                        normalized = clause_name.replace("-", "_").replace(" ", "_")
                        for ct in ClauseType:
                            ct_normalized = ct.value.replace("-", "_")
                            # Exact match or one contains the other
                            if ct_normalized == normalized or normalized in ct_normalized or ct_normalized in normalized:
                                priority_clauses.add(ct)
                                break

        return priority_clauses

    def get_risk_modifiers(self) -> Dict[ClauseType, List[Tuple[str, float, str]]]:
        """Return risk score modifier rules keyed by clause type."""
        if not self.is_active:
            return {}

        modifiers: Dict[ClauseType, List[Tuple[str, float, str]]] = {}

        for pref_id in self.profile.preference_ids:
            rules = self.BOOST_RULES.get(pref_id, [])
            for pattern, boost, description in rules:
                # Map rule to relevant clause types via heuristics in description
                for ct in ClauseType:
                    # Check if any keyword in the description matches the clause type
                    ct_keywords = ct.value.replace("_", " ").lower().split()
                    desc_lower = description.lower()
                    if any(kw in desc_lower for kw in ct_keywords):
                        if ct not in modifiers:
                            modifiers[ct] = []
                        modifiers[ct].append((pattern, boost, f"[Profile:{pref_id}] {description}"))

        return modifiers

    def get_redline_preferences(self) -> Dict[str, str]:
        """Return preferred redline categories per clause type.
        
        Returns a dict mapping clause type -> preference keyword
        (e.g., 'mutual', 'market_standard', 'protectionist').
        Currently returns empty for default behavior; can be extended
        to influence template selection order.
        """
        if not self.is_active:
            return {}

        spec = self._load_spec()
        prefs: Dict[str, str] = {}

        roles_to_check = []
        if self.profile.role in ("reviewer", "creator"):
            roles_to_check = [f"{self.profile.role}_preferences"]
        elif self.profile.role == "both":
            roles_to_check = ["reviewer_preferences", "creator_preferences"]

        for role in roles_to_check:
            prefs_list = spec.get(role, [])
            for pref in prefs_list:
                if pref.get("id", "") in self.profile.preference_ids:
                    clause_names = pref.get("priority_clauses", [])
                    for cname in clause_names:
                        if cname not in prefs:
                            prefs[cname] = "preferred"

        return prefs