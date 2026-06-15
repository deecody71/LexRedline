"""Redline suggestion engine - generates alternative language for flagged clauses.
Aligned with the Legal Domain Specialist's redline templates."""

from typing import List, Dict, Optional
import re
from src.models import Clause, ClauseType, RedlineSuggestion, RiskLevel, RiskScore


class RedlineGenerator:
    """
    Generates suggested redline edits for flagged clauses using the specialist's templates.
    
    Each clause type has trigger-specific suggestions with market-standard replacements.
    Priority is adjusted based on detected risk level.
    """

    # Templates from the Legal Domain Specialist's knowledge base
    REDLINE_TEMPLATES: Dict[ClauseType, List[Dict]] = {
        ClauseType.CONFIDENTIALITY: [
            {
                "trigger": r'unilateral',
                "suggestion": "Make obligations mutual.",
                "replacement": "Each party (the 'Recipient') shall keep confidential all non-public information disclosed by the other party (the 'Discloser').",
                "priority": RiskLevel.HIGH,
            },
            {
                "trigger": r'(perpetual|indefinite)',
                "suggestion": "Limit survival to 3-5 years.",
                "replacement": "The obligations of confidentiality shall survive for three (3) years following termination.",
                "priority": RiskLevel.HIGH,
            },
            {
                "trigger": r'no\s+carve[\-]?out|no\s+exception',
                "suggestion": "Add standard exceptions including legally compelled disclosure.",
                "replacement": "Confidential Information does not include information that: (a) is or becomes publicly available without breach; (b) was known prior to disclosure; (c) is independently developed; or (d) is rightfully obtained from a third party. Recipient may disclose Confidential Information to the extent required by law, court order, or government regulation.",
                "priority": RiskLevel.MEDIUM,
            },
        ],
        ClauseType.INDEMNIFICATION: [
            {
                "trigger": r'unilateral.*(?:indemnif|indemnit)',
                "suggestion": "Make indemnification mutual for IP infringement.",
                "replacement": "Each party shall indemnify and hold harmless the other party from and against any third-party claims alleging that the indemnifying party's technology or IP infringes a third-party patent or copyright.",
                "priority": RiskLevel.HIGH,
            },
            {
                "trigger": r'breach\s+of\s+(this\s+)?(agreement|contract)',
                "suggestion": "Limit indemnity to specific high-risk items like IP or data breach.",
                "replacement": "Party A's indemnification obligations shall be limited to third-party claims arising from Party A's gross negligence, willful misconduct, or infringement of third-party intellectual property rights.",
                "priority": RiskLevel.HIGH,
            },
            {
                "trigger": r'(indirect|consequential)',
                "suggestion": "Remove indirect/consequential damages from indemnification scope.",
                "replacement": "Indemnification obligations under this Section shall be limited to direct damages and shall exclude any indirect, incidental, special, or consequential damages.",
                "priority": RiskLevel.MEDIUM,
            },
        ],
        ClauseType.LIMITATION_OF_LIABILITY: [
            {
                "trigger": r'(?:in\s+)?no\s+event\s+(?:shall\s+)?(?:either|neither)',
                "suggestion": "Insert a mutual cap on direct damages.",
                "replacement": "Except for excluded claims, each party's total aggregate liability under this agreement shall not exceed the fees paid or payable by Customer in the twelve (12) months preceding the claim.",
                "priority": RiskLevel.CRITICAL,
            },
            {
                "trigger": r'(no|not).*(indirect|consequential)',
                "suggestion": "Add mutual exclusion of consequential/indirect damages.",
                "replacement": "In no event shall either party be liable for any indirect, incidental, special, or consequential damages, including loss of profits or data, whether based on contract, tort, or any other theory of liability.",
                "priority": RiskLevel.HIGH,
            },
            {
                "trigger": r'\$[\s]*5,000|\$[\s]*10,000',
                "suggestion": "Change cap to 12 months of fees instead of fixed low dollar amount.",
                "replacement": "PROVIDER'S TOTAL AGGREGATE LIABILITY TO CUSTOMER SHALL NOT EXCEED THE TOTAL FEES PAID BY CUSTOMER IN THE TWELVE (12) MONTHS PRECEDING THE CLAIM.",
                "priority": RiskLevel.CRITICAL,
            },
        ],
        ClauseType.TERMINATION_FOR_CONVENIENCE: [
            {
                "trigger": r'unilateral.*(vendor|provider|licensor)',
                "suggestion": "Add mutual termination right or remove the vendor-only right.",
                "replacement": "Either party may terminate this Agreement for convenience upon ninety (90) days' prior written notice to the other party.",
                "priority": RiskLevel.HIGH,
            },
            {
                "trigger": r'(no\s+)?refund.*(no\s+)?pre[\-]?paid',
                "suggestion": "Add requirement to refund unused portion of pre-paid fees.",
                "replacement": "In the event of termination for convenience by Customer, Vendor shall provide a pro-rata refund of any pre-paid, unused fees for the remainder of the Term.",
                "priority": RiskLevel.MEDIUM,
            },
            {
                "trigger": r'(10|ten|15|fifteen)\s*days?\s*(notice|prior)',
                "suggestion": "Extend notice period to 60-90 days.",
                "replacement": "Either party may terminate this Agreement for convenience upon sixty (60) days' prior written notice.",
                "priority": RiskLevel.HIGH,
            },
        ],
        ClauseType.GOVERNING_LAW: [
            {
                "trigger": r'(Alabama|Mississippi|Arkansas|Montana)',
                "suggestion": "Change to Delaware or New York.",
                "replacement": "This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware, without regard to its conflict of laws principles.",
                "priority": RiskLevel.HIGH,
            },
            {
                "trigger": r'foreign.*(law|jurisdiction)',
                "suggestion": "Change to a US jurisdiction aligned with the parties.",
                "replacement": "This Agreement shall be governed by the laws of the State of New York, without regard to its conflict of laws principles. The parties submit to the non-exclusive jurisdiction of the state and federal courts located in New York, New York.",
                "priority": RiskLevel.HIGH,
            },
        ],
        ClauseType.NON_COMPETE: [
            {
                "trigger": r'(12|twelve)\s*month|1\s*year',
                "suggestion": "Narrow to direct competitors for 6 months, with reasonable geographic scope.",
                "replacement": "For a period of six (6) months following termination, neither party shall directly engage in the development of a product that is a direct functional equivalent to the core Services provided hereunder within the territory where Services were provided.",
                "priority": RiskLevel.HIGH,
            },
            {
                "trigger": r'(global|worldwide|anywhere)',
                "suggestion": "Limit geographic scope to where the party actually does business.",
                "replacement": "This non-compete is limited to the geographic areas in which the restricted party provided services or had a material business presence during the term of this Agreement.",
                "priority": RiskLevel.HIGH,
            },
        ],
        ClauseType.NON_SOLICITATION: [
            {
                "trigger": r'(indefinite|perpetual)',
                "suggestion": "Limit to 12 months post-termination.",
                "replacement": "For a period of twelve (12) months following termination, neither party shall directly solicit any employee or independent contractor of the other party who was materially involved in the services provided under this Agreement.",
                "priority": RiskLevel.HIGH,
            },
            {
                "trigger": r'liquidated.*(hire|solicit|employ)',
                "suggestion": "Remove liquidated damages for hiring; use standard remedy.",
                "replacement": "In the event of a breach of this non-solicitation obligation, the non-breaching party shall be entitled to seek injunctive relief and/or damages as provided by law.",
                "priority": RiskLevel.MEDIUM,
            },
        ],
        ClauseType.FORCE_MAJEURE: [
            {
                "trigger": r'payment.*(?:excuse|not\s+be\s+required)',
                "suggestion": "Clarify that force majeure does not excuse payment.",
                "replacement": "Neither party shall be liable for delays in performance due to Force Majeure; provided, however, that this Section shall not excuse Customer's obligation to pay for Services already rendered.",
                "priority": RiskLevel.HIGH,
            },
            {
                "trigger": r'(economic|market).*(change|condition)',
                "suggestion": "Remove economic hardship from force majeure. Keep only uncontrollable events.",
                "replacement": "Force Majeure means events beyond a party's reasonable control, including acts of God, war, terrorism, pandemic, epidemic, government action or regulation, fire, flood, earthquake, and labor disputes. Economic hardship or market changes do not constitute Force Majeure.",
                "priority": RiskLevel.MEDIUM,
            },
        ],
        ClauseType.ASSIGNMENT: [
            {
                "trigger": r'(may\s+not|cannot|shall\s+not).*(assign|transfer)',
                "suggestion": "Allow assignment in connection with a merger or sale of assets.",
                "replacement": "Neither party may assign this Agreement without consent, except that either party may assign this Agreement without consent to an affiliate or in connection with a merger, acquisition, or sale of substantially all of its assets.",
                "priority": RiskLevel.HIGH,
            },
            {
                "trigger": r'(freely\s+assign|assign.*any\s+third)',
                "suggestion": "Require consent (not to be unreasonably withheld) and notice for assignment.",
                "replacement": "Neither party may assign this Agreement without the other party's prior written consent, which shall not be unreasonably withheld or delayed. Either party may assign this Agreement to an affiliate or in connection with a change of control upon notice to the other party.",
                "priority": RiskLevel.MEDIUM,
            },
        ],
        ClauseType.ENTIRE_AGREEMENT: [
            {
                "trigger": r'oral.*(modification|amendment)',
                "suggestion": "Ensure all amendments must be in writing.",
                "replacement": "This Agreement may only be amended or modified by a written instrument signed by authorized representatives of both parties.",
                "priority": RiskLevel.HIGH,
            },
        ],
        ClauseType.WARRANTY: [
            {
                "trigger": r'(absolute|100|perfect|unconditional)',
                "suggestion": "Change to commercially reasonable / professional standards.",
                "replacement": "Vendor warrants that the Services will be performed in a professional and workmanlike manner consistent with industry standards. Vendor warrants that the Deliverables will conform in all material respects to the specifications set forth in the applicable Statement of Work.",
                "priority": RiskLevel.CRITICAL,
            },
            {
                "trigger": r'(as is|as[\s-]is|with\s+all\s+faults)',
                "suggestion": "Replace 'as-is' with a standard limited warranty.",
                "replacement": "Vendor warrants that the Services will be performed in a professional manner consistent with industry standards. This warranty is in lieu of all other warranties, express or implied, except as expressly set forth herein.",
                "priority": RiskLevel.HIGH,
            },
        ],
        ClauseType.DISCLAIMER: [
            {
                "trigger": r'(implied|statutory|merchantability|fitness)',
                "suggestion": "Ensure disclaimer is in all-caps or bold to be conspicuous.",
                "replacement": "EXCEPT AS EXPRESSLY SET FORTH HEREIN, VENDOR DISCLAIMS ALL WARRANTIES, EXPRESS OR IMPLIED, INCLUDING THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.",
                "priority": RiskLevel.MEDIUM,
            },
        ],
        ClauseType.LIQUIDATED_DAMAGES: [
            {
                "trigger": r'(non[\-]?exclusive|in\s+addition).*(remedy|right)',
                "suggestion": "Make liquidated damages the sole and exclusive remedy for the specific breach.",
                "replacement": "The liquidated damages set forth in this Section shall be the Customer's sole and exclusive remedy for the specific delay or failure described herein.",
                "priority": RiskLevel.HIGH,
            },
        ],
        ClauseType.EXCLUSIVITY: [
            {
                "trigger": r'(broad|indefinite|unlimited)',
                "suggestion": "Narrow exclusivity scope and add time limit or minimum commitment.",
                "replacement": "During the Term, Customer agrees to use Provider as the exclusive provider of [specific services] for [specific business unit/geography]. This exclusivity shall be subject to review and renewal on each anniversary of the Effective Date.",
                "priority": RiskLevel.HIGH,
            },
        ],
        ClauseType.MOST_FAVORED_NATION: [
            {
                "trigger": r'(automatic|retroactive)',
                "suggestion": "Make MFN manual (upon request) rather than automatic retroactive.",
                "replacement": "Upon Customer's written request, Provider shall confirm whether more favorable pricing has been offered to customers with similar volume and scope. If so, Provider shall extend such pricing to Customer prospectively.",
                "priority": RiskLevel.MEDIUM,
            },
        ],
        ClauseType.PAYMENT_TERMS: [
            {
                "trigger": r'Net\s+(90|120)',
                "suggestion": "Change to Net 30 or Net 45 payment terms.",
                "replacement": "All invoices are due and payable within thirty (30) days of the invoice date.",
                "priority": RiskLevel.MEDIUM,
            },
            {
                "trigger": r'no\s+right\s+to\s+(dispute|contest|withhold)',
                "suggestion": "Add right to withhold disputed amounts in good faith.",
                "replacement": "Customer may withhold payment of amounts disputed in good faith, provided that Customer notifies Provider of the nature of the dispute within fifteen (15) days of the invoice date.",
                "priority": RiskLevel.HIGH,
            },
        ],
        ClauseType.INTEREST_ON_LATE_PAYMENTS: [
            {
                "trigger": r'(usuri|exceeding.*legal|above.*legal)',
                "suggestion": "Reduce interest rate to standard 1-1.5% per month or maximum allowed by law.",
                "replacement": "Late payments shall accrue interest at the rate of 1.5% per month or the maximum rate permitted by applicable law, whichever is less.",
                "priority": RiskLevel.CRITICAL,
            },
            {
                "trigger": r'(disputed|contested|challenged)',
                "suggestion": "Interest should only apply to undisputed amounts.",
                "replacement": "Interest on late payments shall apply only to undisputed amounts that are not paid by the due date.",
                "priority": RiskLevel.MEDIUM,
            },
        ],
        ClauseType.AUDIT_RIGHTS: [
            {
                "trigger": r'(unlimited|anytime|without\s+notice)',
                "suggestion": "Limit audits to once per year with reasonable notice.",
                "replacement": "Customer may audit Provider's records related to this Agreement no more than once per calendar year, upon at least ten (10) business days' written notice, during normal business hours. If the audit reveals a discrepancy exceeding 5%, Provider shall pay for the cost of the audit.",
                "priority": RiskLevel.HIGH,
            },
        ],
        ClauseType.INSURANCE: [
            {
                "trigger": r'(24|48|72)\s*(hour).*(cancel|change|terminat)',
                "suggestion": "Extend notice period to 30 days for policy changes or cancellations.",
                "replacement": "Provider shall provide Customer with at least thirty (30) days' prior written notice before any material change, cancellation, or non-renewal of the required insurance policies.",
                "priority": RiskLevel.MEDIUM,
            },
        ],
        ClauseType.SUBCONTRACTING: [
            {
                "trigger": r'(complete|total|absolute).*(prohib|forbid|ban)',
                "suggestion": "Allow subcontracting with consent and prime liability.",
                "replacement": "Provider may subcontract any portion of the Services with Customer's prior written consent, which shall not be unreasonably withheld. Provider shall remain fully liable for the performance of all subcontractors.",
                "priority": RiskLevel.MEDIUM,
            },
            {
                "trigger": r'(no|not).*liable.*(subcontract|third[\-]?party)',
                "suggestion": "Prime contractor must remain fully liable.",
                "replacement": "Provider shall remain fully responsible and liable for the acts and omissions of its subcontractors as if Provider had performed the Services directly.",
                "priority": RiskLevel.HIGH,
            },
        ],
        ClauseType.PUBLICITY: [
            {
                "trigger": r'any.*(marketing|advertis|promot).*(without.*consent)',
                "suggestion": "Require prior written consent for all marketing uses.",
                "replacement": "Neither party shall use the other party's name, logo, or trademarks in any press release, marketing material, or public announcement without the prior written consent of the other party, which shall not be unreasonably withheld.",
                "priority": RiskLevel.MEDIUM,
            },
        ],
        ClauseType.COMPLIANCE_WITH_LAWS: [
            {
                "trigger": r'(unilateral|only.*shall|without.*reciprocal)',
                "suggestion": "Make compliance obligations mutual.",
                "replacement": "Each party shall comply with all applicable laws and regulations in its performance under this Agreement.",
                "priority": RiskLevel.MEDIUM,
            },
        ],
        ClauseType.ORDER_OF_PRECEDENCE: [
            {
                "trigger": r'(unclear|ambiguous|circular)',
                "suggestion": "Set a clear hierarchy: Agreement controls legal terms, SOW controls commercial/technical terms.",
                "replacement": "In the event of any conflict between the terms of this Agreement and any Statement of Work, the Agreement shall control with respect to general legal and administrative terms, and the Statement of Work shall control with respect to commercial and technical terms specific to such SOW.",
                "priority": RiskLevel.MEDIUM,
            },
        ],
        ClauseType.DATA_PROTECTION: [
            {
                "trigger": r'(no|not|without).*(breach|notification|notice)',
                "suggestion": "Add breach notification requirement (48-72 hours is standard).",
                "replacement": "Provider shall notify Customer within 48 hours of becoming aware of any data breach involving Customer's data, and shall provide reasonable cooperation in investigating and remediating the breach.",
                "priority": RiskLevel.CRITICAL,
            },
            {
                "trigger": r'(sell|commercialize|monetize).*(data|information)',
                "suggestion": "Restrict data usage to providing the Services only.",
                "replacement": "Provider shall use Customer Data solely for the purpose of providing the Services under this Agreement. Provider shall not sell, commercialize, or use Customer Data for any other purpose without Customer's express written consent.",
                "priority": RiskLevel.HIGH,
            },
        ],
        ClauseType.INTELLECTUAL_PROPERTY: [
            {
                "trigger": r'vendor.*owns.*(everything|all\s+right|all.*improvement)',
                "suggestion": "Clarify that Customer owns custom deliverables and retains its data.",
                "replacement": "Customer retains all right, title, and interest in and to Customer Data. Provider assigns to Customer all intellectual property rights in the custom Deliverables created specifically for Customer under this Agreement. Provider retains all rights in its pre-existing technology and any generally applicable improvements thereto.",
                "priority": RiskLevel.CRITICAL,
            },
            {
                "trigger": r'(customer|customer).*(loses|transfer).*(background|ip)',
                "suggestion": "Ensure Customer retains all background IP.",
                "replacement": "Each party retains all right, title, and interest in and to its pre-existing intellectual property. Neither party shall acquire any ownership interest in the other party's pre-existing intellectual property by virtue of this Agreement.",
                "priority": RiskLevel.HIGH,
            },
        ],
        ClauseType.SURVIVAL: [
            {
                "trigger": r'(indefinite|perpetual|indefinitely)',
                "suggestion": "Limit survival periods to specific durations.",
                "replacement": "The following sections shall survive termination: Section [Confidentiality] for three (3) years, Section [Indemnification] for the applicable statute of limitations, and Section [Payment] until all amounts due are paid.",
                "priority": RiskLevel.HIGH,
            },
        ],
    }

    DEFAULT_SUGGESTION = {
        "suggestion": "Review this clause against your organization's standard playbook. Consider whether the language is mutual and balanced.",
        "replacement": None,
        "priority": RiskLevel.MEDIUM,
    }

    def suggest(self, clauses: List[Clause], risk_scores: Optional[List[RiskScore]] = None) -> List[RedlineSuggestion]:
        """Generate redline suggestions for detected clauses."""
        suggestions: List[RedlineSuggestion] = []
        suggested_types: set = set()

        risk_lookup: Dict[ClauseType, float] = {}
        if risk_scores:
            for rs in risk_scores:
                risk_lookup[rs.clause_type] = rs.score

        for clause in clauses:
            if clause.clause_type in suggested_types:
                continue

            templates = self.REDLINE_TEMPLATES.get(clause.clause_type, [])
            if not templates:
                continue

            suggested_types.add(clause.clause_type)

            matched_templates = []
            for template in templates:
                trigger = template.get("trigger", "")
                if trigger and re.search(trigger, clause.text, re.IGNORECASE):
                    matched_templates.append(template)

            if not matched_templates:
                matched_templates = [templates[0]]

            for template in matched_templates:
                priority = template.get("priority", RiskLevel.MEDIUM)
                clause_risk = risk_lookup.get(clause.clause_type, 0.5)
                if clause_risk > 0.60:
                    priority = RiskLevel.CRITICAL
                elif clause_risk > 0.40 and priority == RiskLevel.MEDIUM:
                    priority = RiskLevel.HIGH

                replacement = template.get("replacement", "")
                suggestion_text = template.get("suggestion", self.DEFAULT_SUGGESTION["suggestion"])

                suggestions.append(RedlineSuggestion(
                    clause_type=clause.clause_type,
                    original_text=clause.text[:500],
                    suggested_text=replacement or suggestion_text,
                    risk_reason=suggestion_text,
                    priority=priority,
                ))

        return suggestions