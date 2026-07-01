"""Risk scoring engine for contract clauses.
Aligned with the Legal Domain Specialist's rubrics."""

from typing import List, Dict, Optional, Tuple
import re
from src.models import Clause, ClauseType, RiskScore, RiskLevel, Contract


class RiskScorer:
    """
    Evaluates risk for each detected clause using the specialist's rubric.
    
    Uses the 3-tier (LOW/MEDIUM/HIGH) framework from the knowledge base,
    with pattern matching against specific risk indicators per clause type.
    """

    # Rubric: each clause type has LOW/MEDIUM/HIGH indicator patterns
    # Each entry: (regex_pattern, risk_contribution, description)
    # Uses the specialist's taxonomy with LOW=+0 to base, MEDIUM=+0.2, HIGH=+0.4
    CLAUSE_RISK_RULES: Dict[ClauseType, List[Tuple[str, float, str]]] = {
        ClauseType.INDEMNIFICATION: [
            (r'(mutual|both\s+part(y|ies))\s+(indemnif|shall\s+indemnif)', -0.2, "Mutual indemnification (lower risk)"),
            (r'mutual.*(?:third[\-]?party|ip|infring)', -0.25, "Mutual for third-party IP claims (market)"),
            (r'indemnif.*(?:indirect|consequential)', 0.3, "Includes indirect/consequential damages"),
            (r'(first[\-]?party|direct)\s+(loss|damage|claim)', 0.3, "Covers first-party losses (aggressive)"),
            (r'breach\s+of\s+(this\s+)?(agreement|contract)', 0.2, "Indemnity for any breach (too broad)"),
            (r'uncapped|unlimited.*indemnif', 0.15, "Uncapped indemnification"),
            (r'(notice|control|defen[ds]e)\s+.*(claim|action)', -0.1, "Notice and defense provisions present"),
            (r'sole\s+discretion', 0.2, "At sole discretion of one party"),
            (r'prompt.*notif', -0.1, "Prompt notice requirement"),
        ],
        ClauseType.LIMITATION_OF_LIABILITY: [
            (r'(?:in\s+)?no\s+event\s+(?:shall\s+)?(?:either|neither)', 0.25, "Blanket liability exclusion language"),
            (r'no\s+liability\s+for\s+any', 0.3, "Complete liability exclusion"),
            (r'(?:not\s+)?liable\s+for\s+any\s+damages', 0.25, "Broad damages exclusion"),
            (r'not\s+exceed\s+(the\s+)?(?:fees|amounts?)\s+paid', 0.0, "Liability capped at fees paid (market)"),
            (r'(\$[\d,]+(?:k|K|M|m)?).*(?:cap|limit|maximum|aggregate)', 0.15, "Fixed dollar cap (varies by deal size)"),
            (r'not\s+exceed\s+(the\s+)?(?:fees|amounts?)\s+paid.*(?:12|twelve)\s+month', -0.15, "12 months fees cap (market standard)"),
            (r'not\s+exceed\s+(the\s+)?(?:fees|amounts?)\s+paid.*(?:6|six)\s+month', 0.1, "6 months fees cap (low)"),
            (r'\$[\s]*5,000|\$[\s]*10,000', 0.3, "Extremely low fixed cap ($5K-$10K)"),
            (r'mutual', -0.15, "Mutual limitation (lower risk)"),
            (r'exclusive\s+remedy', 0.05, "Exclusive remedy clause"),
            (r'(indirect|consequential|special)\s+damages', 0.15, "Exclusion of indirect damages"),
            (r'gross\s+negligence.*(?:not\s+)?(?:limit|exclude)', 0.1, "Gross negligence exception"),
            (r'super[\-]?cap|supercap', 0.1, "Super-cap for specific breaches"),
        ],
        ClauseType.GOVERNING_LAW: [
            (r'(Delaware|New\s+York|California)', -0.15, "Neutral commercial hub (Delaware/NY/CA)"),
            (r'(Alabama|Mississippi|Arkansas|Montana)', 0.25, "Unfavorable non-commercial jurisdiction"),
            (r'foreign\s+(law|jurisdiction|court)', 0.2, "Foreign jurisdiction for domestic deal"),
            (r'(exclusive|non[\-]?exclusive)\s+jurisdiction', 0.05, "Explicit jurisdiction clause (neutral)"),
            (r'govern.*(?:laws|law).*[A-Z][a-z]+.*(?:country|nation)', 0.15, "Non-US governing law for domestic deal"),
            (r'Neutral\s+Hub|\bDelaware\b', -0.15, "Neutral hub selection"),
            (r'conflict(s)?\s+of\s+laws?', 0.0, "Conflict of laws exclusion (standard)"),
        ],
        ClauseType.CONFIDENTIALITY: [
            (r'mutual', -0.2, "Mutual confidentiality (lower risk)"),
            (r'unilateral', 0.2, "Unilateral confidentiality (higher risk)"),
            (r'(perpetual|indefinite|indefinitely)', 0.3, "Indefinite survival period"),
            (r'survive.*(\d+)\s+years?', 0.0, "Defined survival period"),
            (r'survive.*(?:3|three)\s+years?', -0.15, "3-year survival (market standard)"),
            (r'survive.*(?:5|five)\s+years?', 0.0, "5-year survival (acceptable)"),
            (r'reasonable.*understood.*confidential', -0.1, "Reasonable person standard (balanced)"),
            (r'exception', -0.1, "Exceptions listed (lower risk)"),
            (r'(public|publicly\s+available|public\s+knowledge)', -0.1, "Standard exceptions included"),
            (r'(return|destroy).*(?:without\s+)?exception', 0.15, "Strict return/destroy without carve-outs"),
            (r'(legal\s+)?(compulsion|order|requirement)', -0.1, "Carve-out for legally compelled disclosure"),
        ],
        ClauseType.NON_COMPETE: [
            (r'during[\-\s]?term|while\s+this\s+agreement|for\s+the\s+term', -0.2, "During-term only (lower risk)"),
            (r'(\d+)\s*(month|year).*post[\-\s]?term', 0.1, "Post-term restriction with defined period"),
            (r'(12|twelve)\s*month|1\s*year', 0.2, "12+ month post-term (high)"),
            (r'global|worldwide|anywhere|any\s+geograph', 0.3, "Unreasonable global scope"),
            (r'any\s+(business|technology|industry|sector)', 0.3, "Overbroad business scope"),
            (r'direct\s+competitors?', -0.1, "Limited to direct competitors"),
            (r'50[\-]mile|\d+[\-]?mile', 0.1, "Geographic restriction (moderate)"),
        ],
        ClauseType.NON_SOLICITATION: [
            (r'mutual', -0.15, "Mutual non-solicit (lower risk)"),
            (r'unilateral', 0.15, "Unilateral non-solicit"),
            (r'indefinite|perpetual', 0.3, "Indefinite duration"),
            (r'(\d+)\s*(month|year)', 0.0, "Defined duration"),
            (r'(12|twelve)\s*month', 0.0, "12-month duration (market standard)"),
            (r'(general|public).*(advert|recruit|job\s+posting)', -0.15, "Exception for general recruitment"),
            (r'employee\s+applicant|independent.*contact', -0.05, "Exception for independent application"),
            (r'liquidated\s+damages.*(?:hire|solicit|employ)', 0.2, "Liquidated damages for hiring"),
            (r'200%.*salar|penalt', 0.25, "Penalty-level liquidated damages"),
        ],
        ClauseType.FORCE_MAJEURE: [
            (r'(act\s+of\s+god|war|terrorism|pandemic|epidemic|flood|fire)', -0.15, "Comprehensive event list"),
            (r'(earthquake|hurricane|natural\s+disaster)', -0.1, "Natural disaster coverage"),
            (r'government\s+(action|order|regulation)', -0.1, "Government action included"),
            (r'(economic|market).*(change|condition|hardship)', 0.25, "Economic hardship included (non-standard)"),
            (r'payment.*(?:excuse|not\s+be\s+required|shall\s+not)', 0.2, "Excuses payment obligations"),
            (r'mitigat(e|ion)', -0.1, "Obligation to mitigate"),
            (r'(prompt|timely).*(notice|notify)', -0.1, "Prompt notice requirement"),
            (r'terminat.*(?:60|sixty|90|ninety)\s+day', -0.1, "Termination right after extended event"),
        ],
        ClauseType.WARRANTY: [
            (r'(professional|industry|workmanlike).*(standard|manner)', -0.15, "Professional standard warranty"),
            (r'non[\-]infringement', -0.1, "Non-infringement warranty"),
            (r'(authorit|authoriz)', -0.05, "Authority warranty"),
            (r'(absolute|100|perfect|unconditional|flawless)', 0.3, "Absolute performance guarantee"),
            (r'(conform|comply).*specific', -0.1, "Conforms to specifications"),
            (r'(\d{1,3})\s*(day|month).*warrant', 0.0, "Limited warranty period"),
            (r'(90|ninety)\s*days?', 0.0, "90-day warranty (common for software)"),
            (r'(re[\-]?perform|correct|remedy|cure)', -0.1, "Remedy provision included"),
            (r'indefinite.*warrant|warrant.*indefinite', 0.2, "Indefinite warranty period"),
        ],
        ClauseType.DISCLAIMER: [
            (r'(ALL CAPS|BOLD|CONSPICUOUS|[A-Z]{10,})', -0.1, "Conspicuous formatting"),
            (r'(implied|statutory)\s+warrant(y|ies)', 0.0, "Implied warranty disclaimer (standard)"),
            (r'merchantability', 0.0, "Merchantability disclaimer (standard)"),
            (r'fitness\s+for\s+a\s+particular\s+purpose', 0.0, "Fitness disclaimer (standard)"),
            (r'disclaim.*express\s+warrant', 0.3, "Disclaims express warranties in contract"),
            (r'(as is|as[\s-]is|with\s+all\s+faults)', 0.15, "'As is' disclaimer"),
        ],
        ClauseType.ASSIGNMENT: [
            (r'(not\s+(be\s+)?)?unreasonably\s+withheld', -0.15, "Consent not unreasonably withheld"),
            (r'(merger|acquisition|sale\s+of\s+assets|change\s+of\s+control)', -0.15, "Permitted for M&A"),
            (r'affiliate', -0.1, "Permitted to affiliates"),
            (r'(may\s+not|cannot|shall\s+not).*(assign|transfer)', 0.15, "No assignment without consent"),
            (r'consent.*(?:shall\s+)?(?:not\s+)?(?:be\s+)?withheld', 0.0, "Consent clause"),
            (r'freely\s+assign|assign.*any\s+third', 0.2, "Free assignment to any third party"),
            (r'absolute.*prohibition|complete.*prohibition', 0.3, "Absolute prohibition even for M&A"),
            (r'(prior\s+)?written\s+consent', 0.1, "Prior written consent required"),
        ],
        ClauseType.ENTIRE_AGREEMENT: [
            (r'(entire|complete|full)\s+(agreement|understanding)', -0.1, "Standard integration clause"),
            (r'supersed(es|ing)', -0.05, "Supersedes prior agreements"),
            (r'oral\s+(modification|amendment|change)', 0.3, "Allows oral modifications"),
            (r'(amend[sed]?|modif[yied]).*(writing|written)', -0.1, "Requires written amendments"),
            (r'exhibits?|schedules?|addend', 0.0, "Mentions exhibits (standard)"),
        ],
        ClauseType.TERMINATION_FOR_CONVENIENCE: [
            (r'mutual', -0.2, "Mutual termination right"),
            (r'either\s+(part(y|ies)|party)\s+may\s+terminat', -0.15, "Either party may terminate"),
            (r'unilateral', 0.2, "Unilateral termination"),
            (r'(refund|pro[\-]?rata|unused\s+fee)', -0.1, "Refund of pre-paid fees"),
            (r'(30|thirty|60|sixty|90|ninety)\s*days?\s*(notice|prior)', -0.05, "Reasonable notice period"),
            (r'(10|ten|15|fifteen)\s*days?\s*(notice|prior)', 0.2, "Very short notice period"),
            (r'termination.*(fee|penalty|charge|cost)', 0.2, "Early termination fees"),
            (r'(no\s+)?refund.*(no\s+)?pre[\-]?paid', 0.2, "No refund of pre-paid fees"),
            (r'(provider|vendor|seller|licensor).*(terminate.*convenience)', 0.2, "Vendor-only termination for convenience"),
        ],
        ClauseType.TERMINATION_FOR_CAUSE: [
            (r'material\s+breach', -0.1, "Material breach requirement"),
            (r'(30|thirty|60|sixty)\s*(days?.*)?(cure|remedy)', -0.1, "Reasonable cure period"),
            (r'cure\s+period', -0.05, "Cure period provision"),
            (r'immediate.*terminat|terminat.*immediate', 0.2, "Immediate termination (no cure)"),
            (r'any\s+breach|all\s+breaches', 0.2, "Any breach triggers termination"),
            (r'insolven(cy|t)|bankrupt(cy|t)', 0.0, "Insolvency termination"),
            (r'mutual', -0.1, "Mutual right"),
        ],
        ClauseType.TERMINATION_FOR_CHANGE_OF_CONTROL: [
            (r'direct\s+competitor', -0.1, "Triggered only by competitor acquisition"),
            (r'(merger|acquisition|sale\s+of\s+assets)', 0.0, "Change of control triggers"),
            (r'(notice|notify).*(change\s+of\s+control)', -0.05, "Notice requirement"),
            (r'consent.*(?:merger|acquisition)', 0.2, "Consent required for change of control"),
            (r'minor.*(?:change|equity|ownership)', 0.15, "Termination for minor changes"),
        ],
        ClauseType.SURVIVAL: [
            (r'(3|three)\s*(years?|yr)', -0.15, "3-year survival (market standard)"),
            (r'(5|five)\s*(years?|yr)', -0.05, "5-year survival"),
            (r'indefinite|perpetual|indefinitely', 0.25, "Indefinite survival"),
            (r'(confidential|indemnif|payment)', -0.05, "Standard list of surviving clauses"),
            (r'performance.*surviv', 0.2, "Performance obligations survive"),
        ],
        ClauseType.DISPUTE_RESOLUTION_ARBITRATION: [
            (r'(AAA|JAMS|ICC|UNCITRAL)', -0.1, "Standard arbitration body"),
            (r'mutual|both\s+part(y|ies)', -0.1, "Mutual arbitration agreement"),
            (r'(neutral|specified)\s+venue|specified\s+location', -0.05, "Neutral venue specified"),
            (r'(one[\-]?sided|only.*may\s+elect)', 0.25, "One-sided arbitration choice"),
            (r'(loser|prevailing).*(pay|bear|cost)', 0.15, "Fee shifting to loser"),
            (r'class\s+action.*(waiver|waiv)', 0.1, "Class action waiver"),
            (r'waiv.*(jury\s+)?trial', 0.05, "Jury trial waiver"),
        ],
        ClauseType.DISPUTE_RESOLUTION_MEDIATION: [
            (r'(30|60|ninety)\s*days?', -0.1, "Reasonable mediation period"),
            (r'(good\s+faith|in\s+good\s+faith)', -0.1, "Good faith mediation"),
            (r'shared\s+(cost|expense)', -0.05, "Shared costs"),
            (r'step.*(?:negotiat|mediat|arbitrat|litigat)', -0.1, "Step-based escalation"),
        ],
        ClauseType.DISPUTE_RESOLUTION_LITIGATION: [
            (r'(exclusive|non[\-]?exclusive)\s+jurisdiction', 0.0, "Explicit jurisdiction clause"),
            (r'waiv.*(?:jury\s+)?trial', 0.05, "Jury trial waiver"),
            (r'(submit|consent).*jurisdiction', 0.0, "Submit to jurisdiction"),
            (r'forum\s+non[\-]?conveniens', 0.15, "Waiver of forum non conveniens"),
        ],
        ClauseType.INTELLECTUAL_PROPERTY: [
            (r'work[\-]?(?:made\s+)?for\s+hire', -0.15, "Work Made for Hire (standard)"),
            (r'(retain|retains).*(background|pre[\-]?exist)', -0.15, "Retains background IP"),
            (r'(customer|client)\s+owns\s+(all\s+)?(deliverable|custom)', -0.1, "Customer owns deliverables"),
            (r'vendor\s+owns.*(everything|all\s+right)', 0.3, "Vendor owns everything"),
            (r'(license|licens).*(use|access|host)', 0.0, "License grant"),
            (r'(non[\-]?exclusive|royalty[\-]?free)', -0.1, "Non-exclusive royalty-free license"),
            (r'(customer|customer).*(loses|transfer).*(background|ip)', 0.25, "Customer loses background IP"),
            (r'(perpetual|irrevocable).*license', 0.0, "Perpetual license"),
        ],
        ClauseType.DATA_PROTECTION: [
            (r'DPA|Data\s+Processing\s+Agreement', -0.2, "DPA included (market standard)"),
            (r'(48|24|72)\s*(hour).*(notif|breach)', -0.1, "Breach notification timeframe"),
            (r'(GDPR|CCPA|HIPAA|PIPEDA|LGPD)', -0.15, "Specific regulation compliance"),
            (r'(encrypt|pseudonym|anonymiz|de[\-]?identify)', -0.1, "Security measures specified"),
            (r'(no|not|without).*(breach|notification|notice)', 0.3, "No breach notification"),
            (r'(sell|commercialize|monetize).*(data|information)', 0.2, "Unrestricted data usage rights"),
            (r'(cross[\-]?border|international).*(transfe?r)', 0.1, "Cross-border data transfer"),
        ],
        ClauseType.PAYMENT_TERMS: [
            (r'Net\s+(30|45)', -0.15, "Standard Net 30/45 terms"),
            (r'Net\s+60', 0.0, "Net 60 (acceptable)"),
            (r'Net\s+(90|120)', 0.2, "Net 90+ (aggressive)"),
            (r'(dispute|contest|challenge).*(good\s+faith|bona\s+fide)', -0.15, "Right to dispute in good faith"),
            (r'no\s+right\s+to\s+(dispute|contest|withhold)', 0.3, "No right to dispute invoices"),
            (r'(upfront|pre[\-]?paid).*(without\s+refund|non[\-]?refund|no\s+refund)', 0.15, "Non-refundable upfront payment"),
        ],
        ClauseType.INTEREST_ON_LATE_PAYMENTS: [
            (r'(1|1\.5)\s*%\s*per\s*month', -0.1, "Standard 1-1.5% monthly interest"),
            (r'maximum.*(legal|allowed|permitted)', 0.0, "Maximum allowed by law"),
            (r'(only|solely).*(undisputed|agreed)', -0.1, "Applies to undisputed amounts only"),
            (r'(usuri|exceeding.*legal|above.*legal)', 0.3, "Usurious interest rates"),
            (r'(disputed|contested|challenged)', 0.2, "Applied to disputed amounts"),
        ],
        ClauseType.LIQUIDATED_DAMAGES: [
            (r'(reasonab|bona\s+fide).*(estimate|approximat)', -0.2, "Reasonable estimate of damages"),
            (r'(sole|exclusive)\s+(remedy|remedies)', -0.15, "Exclusive remedy provision"),
            (r'(cap|limit|capped|maximum).*damages', -0.1, "Capped liquidated damages"),
            (r'(punitive|penalty|excessive|unreasonab)', 0.25, "Punitive/excessive liquidated damages"),
            (r'(non[\-]?exclusive|in\s+addition).*(remedy|right)', 0.2, "Non-exclusive remedy"),
            (r'uncapped|no\s+cap|unlimited', 0.2, "Uncapped liquidated damages"),
        ],
        ClauseType.EXCLUSIVITY: [
            (r'(narrow|limited|specific).*(scope|product|service)', -0.15, "Narrow/limited scope"),
            (r'(time[\-]?limited|for\s+\d+\s+(month|year))', -0.1, "Time-limited exclusivity"),
            (r'(broad|indefinite|unlimited).*(scope|geograph)', 0.25, "Broad/indefinite scope"),
            (r'(minimum|commitment|guarantee|volume)', -0.1, "Minimum purchase commitment"),
            (r'(carve[\-]?out|exception)', -0.1, "Carve-outs for existing relationships"),
            (r'(no|without).*(commitment|minimum)', 0.2, "No minimum commitment"),
        ],
        ClauseType.MOST_FAVORED_NATION: [
            (r'(similar\s+)?(volume|size|scope)', -0.1, "Limited to similar volume/scope"),
            (r'(upon\s+)?request|manual|notice', 0.0, "Upon request (manual)"),
            (r'(automatic|retroactive)', 0.25, "Automatic retroactive application"),
            (r'(audit|self[\-]?certif)', -0.05, "Audit/certification right"),
            (r'(all\s+customers|any\s+customer)', 0.2, "Applies to all customers regardless"),
        ],
        ClauseType.DELIVERABLES: [
            (r'(SOW|statement\s+of\s+work)', -0.1, "SOW-defined scope"),
            (r'(describ|outlin|specif).*(SOW|scope|attach)', -0.05, "Work described in SOW/attachment"),
        ],
        ClauseType.AUDIT_RIGHTS: [
            (r'once?\s+per\s+(year|annum|calendar)', -0.2, "Audit limited to once per year"),
            (r'(reasonab\s+)?(notice|prior\s+notice)', -0.15, "Reasonable notice required"),
            (r'business\s+hours|normal\s+business', -0.1, "During normal business hours"),
            (r'(auditee|audited\s+party).*(pays?|pay\s+for)', -0.1, "Audited party pays only if discrepancy found"),
            (r'(unlimited|anytime|without\s+notice|no\s+notice)', 0.3, "Unlimited/no notice audits"),
            (r'vast|all\s+(system|data|record)|extreme\s+broad', 0.15, "Extremely broad audit scope"),
        ],
        ClauseType.INSURANCE: [
            (r'\$[12]\s*[Mm]\s*(per\s+occurrence|each\s+occurrence)', -0.15, "Standard $1M-$2M occurrence limits"),
            (r'(\$5M|\$5\s*[Mm]|\$10M|\$10\s*[Mm])', 0.1, "Higher limits ($5M-$10M)"),
            (r'(E&O|cyber|professional.*liability)', -0.05, "Appropriate coverage types"),
            (r'certificate.*(?:insur|upon\s+request)', -0.05, "COI upon request"),
            (r'(24|48|72)\s*(hour).*(:?cancel|change)', 0.2, "Short notice for policy changes"),
        ],
        ClauseType.SUBCONTRACTING: [
            (r'(prime|principal).*(remains?|liable)', -0.15, "Prime remains liable (standard)"),
            (r'(approval|consent).*(major|key|sub[\-]?processor)', -0.1, "Approval required for key subs"),
            (r'(flow[\-]?down|same\s+terms)', -0.1, "Flow-down provisions included"),
            (r'(complete|total|absolute).*(prohib|forbid|ban)', 0.2, "Complete prohibition on subcontracting"),
            (r'(no|not).*liable.*(subcontract|third[\-]?party)', 0.2, "No liability for subcontractor actions"),
        ],
        ClauseType.PUBLICITY: [
            (r'(prior\s+)?(written\s+)?consent', -0.15, "Prior written consent required"),
            (r'(customer\s+)?list|log\s+list|referenc', -0.1, "Logo on customer list only"),
            (r'brand.*(guideline|standard)', -0.05, "Brand guidelines required"),
            (r'any\s+(marketing|advertis|promot).*(without.*consent)', 0.2, "Unrestricted marketing use"),
            (r'(absolute|complete).*prohib.*(mention|public|name)', 0.15, "Absolute gag order"),
        ],
        ClauseType.COMPLIANCE_WITH_LAWS: [
            (r'mutual', -0.15, "Mutual compliance obligation"),
            (r'(all\s+)?(applicable|relevant|governing)\s+(laws?|regulation)', 0.0, "Standard compliance language"),
            (r'(anti[\-]?bribery|anti[\-]?corruption|FCPA)', 0.0, "Anti-corruption provisions"),
            (r'(unilateral|only.*shall)', 0.15, "Unilateral compliance obligation"),
            (r'(internal|unknown|undisclosed).*(policy|procedure)', 0.2, "Compliance with unknown internal policies"),
        ],
        ClauseType.NOTICE: [
            (r'email.*(permitted|allowed|acceptable)', -0.1, "Email notice permitted"),
            (r'(certified|registered)\s+mail', 0.0, "Certified mail option"),
            (r'(personal|hand).*delivery', 0.15, "Personal service required"),
            (r'(contact|address|email).*(set\s+forth|below|above)', -0.05, "Contact information provided"),
        ],
        ClauseType.WAIVER: [
            (r'(writing|written).*(sign|execut)', -0.1, "Written waiver required"),
            (r'(fail|delay).*enforce.*right', 0.0, "Non-waiver of future enforcement"),
            (r'oral.*waiver|waiv.*orally', 0.2, "Oral waiver allowed"),
        ],
        ClauseType.SEVERABILITY: [
            (r'(sever|modif|reform|blue[\-]?penc)', -0.1, "Standard severability"),
            (r'invalid.*(?:sever|remov|modif|limit)', -0.05, "Invalidity severance provision"),
            (r'invalid.*(?:void|terminat|kill|end).*(?:entire|whole|agreement)', 0.2, "Invalidity voids entire contract"),
        ],
        ClauseType.COUNTERPARTS: [
            (r'(electronic|digital).*(signature|execution)', -0.1, "Electronic signature accepted"),
            (r'PDF|fax.*(signature|counterpart)', -0.05, "PDF/fax signatures accepted"),
            (r'(wet[\-]?ink|original\s+signature|manual.*sign)', 0.1, "Wet-ink originals required"),
        ],
        ClauseType.ORDER_OF_PRECEDENCE: [
            (r'agreement\s+control.*legal.*term', -0.1, "Agreement controls legal terms"),
            (r'SOW.*control.*(commercial|technical|specific)', -0.1, "SOW controls commercial/technical terms"),
            (r'clear|specif|certain.*hierarch', -0.15, "Clear hierarchy defined"),
        ],
        ClauseType.REPRESENTATIONS: [
            (r'mutual', -0.1, "Mutual representations"),
            (r'standard.*represent', 0.0, "Standard representations"),
        ],
        ClauseType.COVENANTS: [
            (r'mutual', -0.1, "Mutual covenants"),
            (r'further\s+(assur|act)', 0.0, "Further assurances covenant"),
        ],
    }

    # Default risk assignments for types without specific rules
    DEFAULT_CLAUSE_RISK: Dict[ClauseType, float] = {
        ClauseType.DEFINITIONS: 0.1,
        ClauseType.SIGNATURES: 0.05,
        ClauseType.SCHEDULE: 0.05,
        ClauseType.EXPENSES: 0.15,
        ClauseType.UNKNOWN: 0.15,
    }

    def score(self, clauses: List[Clause], contract: Optional[Contract] = None) -> List[RiskScore]:
        """Score each clause for risk level."""
        risk_scores: List[RiskScore] = []
        for clause in clauses:
            score, reasoning, flags = self._evaluate_clause(clause)
            risk_level = self._score_to_level(score)
            risk_scores.append(RiskScore(
                clause_type=clause.clause_type,
                risk_level=risk_level,
                score=score,
                reasoning=reasoning,
                flags=flags
            ))
        return risk_scores

    def apply_modifiers(self, risk_scores: List[RiskScore], clauses: List[Clause],
                        modifiers: Dict[ClauseType, List[Tuple[str, float, str]]]) -> int:
        """Apply profile-driven risk modifiers to already-scored clauses.
        
        Args:
            risk_scores: List of RiskScore from score().
            clauses: Original clauses for text matching.
            modifiers: Dict mapping ClauseType to list of (pattern, boost, description).
        
        Returns:
            Number of clause types that were modified.
        """
        modified_count = 0
        clause_map = {c.clause_type: c for c in clauses}

        for i, rs in enumerate(risk_scores):
            rules = modifiers.get(rs.clause_type, [])
            if not rules:
                continue
            clause = clause_map.get(rs.clause_type)
            if not clause:
                continue

            for pattern, boost, description in rules:
                if re.search(pattern, clause.text, re.IGNORECASE):
                    rs.score = min(1.0, rs.score + boost)
                    rs.risk_level = self._score_to_level(rs.score)
                    rs.flags.append(description)
                    if rs.reasoning:
                        rs.reasoning += "; " + description
                    else:
                        rs.reasoning = description
                    modified_count += 1

        return modified_count

    def _evaluate_clause(self, clause: Clause) -> Tuple[float, str, List[str]]:
        """Evaluate a single clause and return (score, reasoning, flags)."""
        score = 0.3  # Start at low-medium
        flags: List[str] = []
        reasons: List[str] = []

        rules = self.CLAUSE_RISK_RULES.get(clause.clause_type, [])
        text = clause.text

        for pattern, weight, description in rules:
            try:
                if re.search(pattern, text, re.IGNORECASE):
                    score += weight
                    if weight > 0:
                        flags.append(description)
                        reasons.append(f"+{weight:.2f}: {description}")
                    elif weight < 0:
                        reasons.append(f"{weight:.2f}: {description}")
                    else:
                        reasons.append(f" 0.00: {description}")
            except re.error:
                continue

        score = max(0.0, min(1.0, score))

        if not reasons:
            default = self.DEFAULT_CLAUSE_RISK.get(clause.clause_type, 0.2)
            score = default
            reasons.append(f"Default risk: no specific indicators detected ({default:.2f})")

        return score, "; ".join(reasons), flags

    def _score_to_level(self, score: float) -> RiskLevel:
        """Convert numeric score to RiskLevel."""
        if score < 0.25:
            return RiskLevel.LOW
        elif score < 0.45:
            return RiskLevel.MEDIUM
        elif score < 0.70:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

    def compute_overall_risk(self, clauses: List[Clause], risk_scores: List[RiskScore]) -> Tuple[RiskLevel, float]:
        """Compute overall contract risk."""
        if not risk_scores:
            return RiskLevel.LOW, 0.0

        weights = {
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.HIGH: 3,
            RiskLevel.CRITICAL: 4,
        }

        total_weight = 0
        weighted_sum = 0.0
        for rs in risk_scores:
            w = weights[rs.risk_level]
            total_weight += w
            weighted_sum += rs.score * w

        overall_score = weighted_sum / total_weight if total_weight > 0 else 0.0

        # Boost for multiple high-risk clauses
        high_risk_count = sum(1 for rs in risk_scores if rs.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL))
        if high_risk_count >= 3:
            overall_score = min(1.0, overall_score * 1.15)
        if high_risk_count >= 5:
            overall_score = min(1.0, overall_score * 1.3)

        return self._score_to_level(overall_score), round(overall_score, 3)