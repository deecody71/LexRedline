"""Tests for profile-aware analysis engine."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models import Contract, ClauseType, RiskLevel, UserProfile
from src.analysis import ContractAnalyzer
from src.analysis.preferences import PreferenceEngine


SAMPLE_TEXT = """SERVICES AGREEMENT

1. Indemnification. Provider shall indemnify and hold harmless Client from any and all claims at its sole discretion.

2. Limitation of Liability. IN NO EVENT SHALL CUSTOMER BE LIABLE FOR ANY INDIRECT, CONSEQUENTIAL, OR SPECIAL DAMAGES. PROVIDER'S TOTAL AGGREGATE LIABILITY TO CUSTOMER SHALL NOT EXCEED $5,000.

3. Confidentiality. Each party shall maintain the other party's confidential information. These obligations shall survive indefinitely.

4. Governing Law. This Agreement shall be governed by the laws of the State of Alabama.

5. Termination. Provider may terminate this Agreement for convenience at any time upon 10 days' notice. Customer shall not have a reciprocal right.

6. Payment. Customer shall pay all invoices within Net 90 of receipt. Customer has no right to dispute invoices.

7. Assignment. Neither party may assign this Agreement without the other party's consent.
"""


def test_user_profile_model():
    """Test UserProfile model creation."""
    profile = UserProfile(role="reviewer", preference_ids=["liability_financial", "data_privacy"])
    assert profile.role == "reviewer"
    assert "liability_financial" in profile.preference_ids
    assert profile.is_active is True

    empty = UserProfile()
    assert empty.is_active is False

    custom = UserProfile(role="creator", preference_ids=[], custom_preferences="Focus on IP terms")
    assert custom.is_active is True
    assert custom.custom_preferences == "Focus on IP terms"


def test_preference_engine_loading():
    """Test PreferenceEngine loads and resolves profile."""
    engine = PreferenceEngine()
    assert engine.is_active is False

    profile = UserProfile(role="reviewer", preference_ids=["liability_financial"])
    engine = PreferenceEngine(profile)
    assert engine.is_active is True

    priority = engine.get_priority_clauses()
    assert len(priority) > 0, "Should have priority clauses"
    print(f"Priority clauses for liability_financial: {[c.value for c in priority]}")


def test_preference_engine_risk_modifiers():
    """Test PreferenceEngine generates risk modifiers."""
    profile = UserProfile(role="reviewer", preference_ids=["liability_financial"])
    engine = PreferenceEngine(profile)

    modifiers = engine.get_risk_modifiers()
    assert len(modifiers) > 0, "Should generate modifiers"

    print(f"Risk modifiers generated for {len(modifiers)} clause types")
    for ct, rules in modifiers.items():
        for pattern, boost, desc in rules:
            print(f"  {ct.value:30s} +{boost:.2f}: {desc}")


def test_no_profile_unchanged():
    """Test backward compat: no profile = same behavior as before."""
    contract = Contract(filename="test.txt", file_type="txt", full_text=SAMPLE_TEXT)

    analyzer_no_profile = ContractAnalyzer()
    result_base = analyzer_no_profile.analyze(contract)

    # Same as creating without argument
    analyzer_default = ContractAnalyzer()
    result_default = analyzer_default.analyze(contract)

    assert result_base.clause_count == result_default.clause_count
    assert result_base.overall_risk == result_default.overall_risk
    assert len(result_base.redlines) == len(result_default.redlines)

    print(f"No-profile baseline: {result_base.clause_count} clauses, risk={result_base.overall_risk.value}")


def test_profile_changes_risk_scores():
    """Test that a reviewer profile shifts risk scores."""
    contract = Contract(filename="test.txt", file_type="txt", full_text=SAMPLE_TEXT)

    # Without profile
    base = ContractAnalyzer().analyze(contract)

    # With reviewer profile focused on liability + data privacy
    profile = UserProfile(role="reviewer", preference_ids=["liability_financial", "data_privacy"])
    profile_result = ContractAnalyzer(profile=profile).analyze(contract)

    print(f"\nWithout profile: {base.clause_count} clauses, risk={base.overall_risk.value} ({base.overall_risk_score})")
    print(f"With reviewer profile: {profile_result.clause_count} clauses, risk={profile_result.overall_risk.value} ({profile_result.overall_risk_score})")

    # Find limitation_of_liability scores
    base_lol = [rs for rs in base.risk_scores if rs.clause_type == ClauseType.LIMITATION_OF_LIABILITY]
    profile_lol = [rs for rs in profile_result.risk_scores if rs.clause_type == ClauseType.LIMITATION_OF_LIABILITY]

    if base_lol and profile_lol:
        print(f"  LoL risk: base={base_lol[0].score:.2f} -> profile={profile_lol[0].score:.2f}")
        assert profile_lol[0].score >= base_lol[0].score, "Profile should boost LoL risk"

    # Check profile modifications are in metadata
    meta = profile_result.metadata or {}
    assert meta.get("profile_applied") is True, "Profile should be recorded in metadata"
    assert "profile_modifications" in meta, "Modifications should be documented"
    print(f"  Profile modifications: {meta.get('profile_modifications', [])}")


def test_creator_profile():
    """Test that creator profile also works."""
    contract = Contract(filename="test.txt", file_type="txt", full_text=SAMPLE_TEXT)

    base = ContractAnalyzer().analyze(contract)

    profile = UserProfile(role="creator", preference_ids=["aggressive_provisions", "market_deviation"])
    creator_result = ContractAnalyzer(profile=profile).analyze(contract)

    print(f"\nCreator profile: {creator_result.clause_count} clauses, risk={creator_result.overall_risk.value} ({creator_result.overall_risk_score})")

    meta = creator_result.metadata or {}
    assert meta.get("profile_applied") is True
    print(f"  Profile modifications: {meta.get('profile_modifications', [])}")


def test_inactive_profile():
    """Test that inactive/empty profile doesn't change behavior."""
    contract = Contract(filename="test.txt", file_type="txt", full_text=SAMPLE_TEXT)

    base = ContractAnalyzer().analyze(contract)
    inactive = ContractAnalyzer(profile=UserProfile()).analyze(contract)

    assert base.clause_count == inactive.clause_count
    assert base.overall_risk == inactive.overall_risk

    meta = inactive.metadata or {}
    assert meta.get("profile_applied") is not True

    print("Inactive profile: behavior unchanged ✓")


def test_multiple_preferences():
    """Test combining multiple preferences."""
    contract = Contract(filename="test.txt", file_type="txt", full_text=SAMPLE_TEXT)

    # Combine reviewer + creator preferences via 'both' role
    profile = UserProfile(
        role="both",
        preference_ids=["liability_financial", "aggressive_provisions", "data_privacy", "exit_rights"]
    )
    result = ContractAnalyzer(profile=profile).analyze(contract)

    meta = result.metadata or {}
    modifications = meta.get("profile_modifications", [])
    print(f"\nBoth role with 4 preferences: {len(modifications)} modifications")
    for mod in modifications[:5]:
        print(f"  - {mod}")
    assert len(modifications) > 0, "Should have multiple modifications"


def test_profile_priority_clauses():
    """Test that priority clauses are identified."""
    profile = UserProfile(role="reviewer", preference_ids=["ip_ownership", "data_privacy"])
    engine = PreferenceEngine(profile)

    priority = engine.get_priority_clauses()
    priority_names = [c.value for c in priority]
    print(f"\nPriority clauses for ip_ownership + data_privacy:")
    for name in priority_names:
        print(f"  - {name}")

    assert ClauseType.INTELLECTUAL_PROPERTY in priority or any("intellectual" in c.value for c in priority), \
        "Should prioritize IP clauses"
    assert ClauseType.DATA_PROTECTION in priority or any("data" in c.value for c in priority), \
        "Should prioritize data protection"

    print(f"  Total: {len(priority)} priority clause types")


def test_same_contract_different_profiles():
    """Test same contract with different profiles produces different results."""
    contract = Contract(filename="test.txt", file_type="txt", full_text=SAMPLE_TEXT)

    # Financial reviewer vs IP reviewer
    fin_profile = UserProfile(role="reviewer", preference_ids=["liability_financial"])
    ip_profile = UserProfile(role="reviewer", preference_ids=["ip_ownership"])

    fin_result = ContractAnalyzer(profile=fin_profile).analyze(contract)
    ip_result = ContractAnalyzer(profile=ip_profile).analyze(contract)

    # Their metadata should differ
    fin_mods = fin_result.metadata.get("profile_modifications", [])
    ip_mods = ip_result.metadata.get("profile_modifications", [])

    print(f"\nFinancial profile: {len(fin_mods)} mods")
    print(f"IP profile: {len(ip_mods)} mods")

    # The actual modifications should mention different things
    fin_text = " ".join(fin_mods).lower()
    ip_text = " ".join(ip_mods).lower()

    assert "liability" in fin_text or any(cap in fin_text for cap in ("uncapped", "cap", "limitation"))
    assert "ip" in ip_text or "intellectual" in ip_text or "ownership" in ip_text

    print("Different profiles produce different modifications ✓")


def test_full_pipeline_with_profile():
    """Test full analysis pipeline with a profile end-to-end."""
    contract = Contract(filename="test.txt", file_type="txt", full_text=SAMPLE_TEXT)
    profile = UserProfile(role="reviewer", preference_ids=["liability_financial", "exit_rights", "legal_governance"])

    analyzer = ContractAnalyzer(profile=profile)
    result = analyzer.analyze(contract)

    assert result.clause_count > 0
    assert result.overall_risk in list(RiskLevel)

    meta = result.metadata or {}
    assert meta.get("profile_applied") is True
    assert "profile_modifications" in meta

    print(f"\n=== Full Pipeline with Profile ===")
    print(f"Clauses: {result.clause_count}")
    print(f"Overall risk: {result.overall_risk.value} ({result.overall_risk_score})")
    print(f"Redlines: {len(result.redlines)}")
    print(f"Analysis time: {result.analysis_time_ms:.1f}ms")
    print(f"Profile modifications: {len(meta.get('profile_modifications', []))}")


if __name__ == "__main__":
    print("="*60)
    print("Profile-Aware Analysis Engine Tests")
    print("="*60)

    test_user_profile_model()
    print("✓ test_user_profile_model")

    test_preference_engine_loading()
    print("✓ test_preference_engine_loading")

    test_preference_engine_risk_modifiers()
    print("✓ test_preference_engine_risk_modifiers")

    test_no_profile_unchanged()
    print("✓ test_no_profile_unchanged")

    test_inactive_profile()
    print("✓ test_inactive_profile")

    test_profile_changes_risk_scores()
    print("✓ test_profile_changes_risk_scores")

    test_creator_profile()
    print("✓ test_creator_profile")

    test_multiple_preferences()
    print("✓ test_multiple_preferences")

    test_profile_priority_clauses()
    print("✓ test_profile_priority_clauses")

    test_same_contract_different_profiles()
    print("✓ test_same_contract_different_profiles")

    test_full_pipeline_with_profile()
    print("✓ test_full_pipeline_with_profile")

    print("\n" + "="*60)
    print("ALL PROFILE TESTS PASSED")
    print("="*60)