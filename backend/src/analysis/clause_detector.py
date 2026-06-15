"""Clause detection engine using pattern matching and keyword analysis.
Aligned with the Legal Domain Specialist's clause taxonomy."""

import re
from typing import List, Dict, Pattern, Optional
from src.models import Contract, Clause, ClauseType, Section


class ClauseDetector:
    """
    Detects legal clauses in contract text using keyword/pattern matching.
    Supports 33+ clause types from the specialist-defined taxonomy.
    """

    # Comprehensive pattern definitions aligned with legal taxonomy
    CLAUSE_PATTERNS: Dict[ClauseType, Dict] = {
        ClauseType.INDEMNIFICATION: {
            "keywords": [
                "indemnify", "indemnification", "indemnity", "hold harmless",
                "defend against", "indemnified party", "indemnitor"
            ],
            "patterns": [
                r'indemnif(y|ies|ication|ied)',
                r'hold\s+harmless',
                r'indemnity\s+(obligation|provision)'
            ]
        },
        ClauseType.LIMITATION_OF_LIABILITY: {
            "keywords": [
                "limitation of liability", "cap on liability", "maximum liability",
                "total liability", "not exceed", "aggregate liability",
                "exclusion of damages", "indirect damages", "consequential damages"
            ],
            "patterns": [
                r'limitation\s+of\s+liability',
                r'(limit|cap)\s+(our|the|total|aggregate)\s+liability',
                r'liability\s+(shall\s+)?not\s+exceed',
                r'(indirect|consequential|special)\s+damages',
                r'exclusion\s+of\s+damages'
            ]
        },
        ClauseType.GOVERNING_LAW: {
            "keywords": [
                "governing law", "choice of law", "governed by",
                "laws of", "conflict of laws", "applicable law"
            ],
            "patterns": [
                r'govern(ing|ed)\s+(law|by)',
                r'choice\s+of\s+law',
                r'conflict(s)?\s+of\s+laws?',
                r'applicable\s+law'
            ]
        },
        ClauseType.CONFIDENTIALITY: {
            "keywords": [
                "confidential", "confidentiality", "non-disclosure",
                "proprietary information", "trade secret",
                "shall not disclose", "confidential information"
            ],
            "patterns": [
                r'confidential(ity)?\s+(information|obligation)',
                r'non[\-]?disclosure',
                r'(proprietary|confidential)\s+information',
                r'recipient.*shall.*disclos(e|ure)'
            ]
        },
        ClauseType.NON_COMPETE: {
            "keywords": [
                "non-compete", "noncompete", "non-competition",
                "covenant not to compete", "restrictive covenant",
                "competing business", "competitive activity"
            ],
            "patterns": [
                r'non[\-]?compete',
                r'non[\-]?competition',
                r'restrictive\s+covenant',
                r'covenant\s+not\s+to\s+compete'
            ]
        },
        ClauseType.NON_SOLICITATION: {
            "keywords": [
                "non-solicitation", "nonsolicitation", "not solicit",
                "shall not solicit", "no-hire", "anti-poaching"
            ],
            "patterns": [
                r'non[\s-]?solicit(ation|s)?',
                r'(shall\s+)?not\s+solicit',
                r'no[\-]?hire',
                r'anti[\-]?poaching'
            ]
        },
        ClauseType.FORCE_MAJEURE: {
            "keywords": [
                "force majeure", "act of god", "act of God",
                "beyond reasonable control", "unforeseeable",
                "excusable delay", "uncontrollable events"
            ],
            "patterns": [
                r'force\s+majeure',
                r'act\s+of\s+(god|God)',
                r'beyond\s+(reasonable\s+)?control',
                r'uncontrollable\s+events?'
            ]
        },
        ClauseType.WARRANTY: {
            "keywords": [
                "warrant", "warranty", "warranties", "represents and warrants",
                "represent and warrant", "professional standards",
                "non-infringement", "conform", "performance warranty"
            ],
            "patterns": [
                r'warrant(y|ies|ed|s)',
                r'represents?\s+and\s+warrants?',
                r'(service|performance)\s+(level\s+)?warrant',
                r'non[\-]infringement'
            ]
        },
        ClauseType.DISCLAIMER: {
            "keywords": [
                "disclaim", "disclaimer", "as is", "as-is",
                "without warranty", "expressly disclaims",
                "implied warranty", "merchantability", "fitness"
            ],
            "patterns": [
                r'disclaim(er|ed|s)?',
                r'as[\s-]is',
                r'(implied|statutory)\s+warrant(y|ies)',
                r'merchantability|fitness\s+for\s+a\s+particular\s+purpose'
            ]
        },
        ClauseType.ASSIGNMENT: {
            "keywords": [
                "assign", "assignment", "assigns", "successors and assigns",
                "transfer", "novation", "may assign", "shall not assign"
            ],
            "patterns": [
                r'assign(ment|s|ee|or)?',
                r'successors?\s+and\s+assigns?',
                r'(transfer|novat)(ion|e)'
            ]
        },
        ClauseType.ENTIRE_AGREEMENT: {
            "keywords": [
                "entire agreement", "integration", "merger clause",
                "constitutes the entire", "supersedes",
                "complete agreement", "full and final"
            ],
            "patterns": [
                r'entire\s+agreement',
                r'(merger|integration)\s+clause',
                r'supersed(es|ing)',
                r'constitutes?\s+the\s+entire'
            ]
        },
        ClauseType.TERMINATION_FOR_CONVENIENCE: {
            "keywords": [
                "termination for convenience", "terminate for any reason",
                "optional termination", "at-will termination",
                "without cause", "no reason"
            ],
            "patterns": [
                r'terminat(ion|e).*(for\s+)?convenience',
                r'without\s+(cause|reason)',
                r'(any\s+)?reason\s+or\s+no\s+reason',
                r'optional\s+terminat'
            ]
        },
        ClauseType.TERMINATION_FOR_CAUSE: {
            "keywords": [
                "termination for cause", "material breach", "cure period",
                "events of default", "insolvency", "bankruptcy"
            ],
            "patterns": [
                r'terminat(ion|e)\s+for\s+cause',
                r'material\s+breach',
                r'cure\s+period',
                r'events?\s+of\s+default',
                r'insolven(cy|t)|bankrupt(cy|t)',
                r'\bterminat(e|ion)\b'
            ]
        },
        ClauseType.TERMINATION_FOR_CHANGE_OF_CONTROL: {
            "keywords": [
                "change of control", "merger", "acquisition",
                "change in ownership", "assignment by operation of law",
                "sale of assets"
            ],
            "patterns": [
                r'change\s+of\s+control',
                r'(merger|acquisition|consolidation)',
                r'sale\s+of\s+(substantially\s+)?all\s+(its\s+)?assets'
            ]
        },
        ClauseType.SURVIVAL: {
            "keywords": [
                "survival", "survive", "surviving obligations",
                "survive termination", "survive expiration"
            ],
            "patterns": [
                r'surviv(al|e|ing)',
                r'survive\s+(termination|expiration|cancellation)'
            ]
        },
        ClauseType.DISPUTE_RESOLUTION_ARBITRATION: {
            "keywords": [
                "arbitration", "binding arbitration", "AAA",
                "JAMS", "arbitral", "arbitrator"
            ],
            "patterns": [
                r'arbitrati(on|ng|ve|or)',
                r'(AAA|JAMS)',
                r'binding\s+arbitration'
            ]
        },
        ClauseType.DISPUTE_RESOLUTION_MEDIATION: {
            "keywords": [
                "mediation", "mediator", "alternative dispute resolution",
                "ADR", "good faith negotiation"
            ],
            "patterns": [
                r'mediat(e|ion|or)',
                r'alternative\s+dispute\s+resolution',
                r'good\s+faith\s+negotiat'
            ]
        },
        ClauseType.DISPUTE_RESOLUTION_LITIGATION: {
            "keywords": [
                "venue", "jurisdiction", "exclusive jurisdiction",
                "submit to jurisdiction", "waiver of jury trial",
                "forum", "state or federal court"
            ],
            "patterns": [
                r'(exclusive|non[\-]?exclusive)\s+jurisdiction',
                r'(submit|consent)\s+to\s+(the\s+)?jurisdiction',
                r'waiver\s+of\s+(jury\s+)?trial',
                r'(state|federal)\s+court'
            ]
        },
        ClauseType.INTELLECTUAL_PROPERTY: {
            "keywords": [
                "intellectual property", "copyright", "patent", "trademark",
                "work made for hire", "work for hire", "ownership",
                "license", "royalties", "proprietary rights",
                "background ip", "improvements", "deliverable ip"
            ],
            "patterns": [
                r'intellectual\s+propert(y|ies)',
                r'work(\s+made)?\s+for\s+hires?',
                r'(owns|retains)\s+(all\s+)?(right|title|interest)',
                r'(copyright|patent|trademark)',
                r'proprietary\s+rights?',
                r'background\s+ip',
                r'improvements'
            ]
        },
        ClauseType.DATA_PROTECTION: {
            "keywords": [
                "data protection", "personal data", "personal information",
                "PII", "GDPR", "CCPA", "HIPAA", "data breach",
                "privacy", "data processing", "data processor",
                "data controller", "data subject"
            ],
            "patterns": [
                r'data\s+protect(ion|s?)',
                r'personal\s+(data|information)',
                r'(GDPR|CCPA|HIPAA)',
                r'data\s+(breach|process(or|ing))',
                r'privacy'
            ]
        },
        ClauseType.PAYMENT_TERMS: {
            "keywords": [
                "payment", "invoice", "net 30", "net 60", "net 90",
                "late payment", "fees", "pricing", "billing"
            ],
            "patterns": [
                r'payment\s+terms?',
                r'net\s+\d{2,}',
                r'(monthly|annual|upfront)\s+(fee|payment|billing)',
                r'invoice',
                r'pric(e|ing)'
            ]
        },
        ClauseType.INTEREST_ON_LATE_PAYMENTS: {
            "keywords": [
                "interest on late payments", "late fees", "late charges",
                "finance charge", "overdue"
            ],
            "patterns": [
                r'late\s+(payment|fee|charge)',
                r'interest\s+(rate|shall\s+accrue)',
                r'overdue\s+(amount|payment|invoice)'
            ]
        },
        ClauseType.LIQUIDATED_DAMAGES: {
            "keywords": [
                "liquidated damages", "agreed damages", "service credits",
                "penalties", "buy-out fees"
            ],
            "patterns": [
                r'liquidated\s+damages',
                r'(service|performance)\s+credits?',
                r'(per[\s-])?day\s+penalt(y|ies)'
            ]
        },
        ClauseType.EXCLUSIVITY: {
            "keywords": [
                "exclusivity", "exclusive dealing", "sole provider",
                "lock-out", "exclusive"
            ],
            "patterns": [
                r'exclusiv(e|ity)',
                r'sole\s+provider',
                r'exclusive\s+deal(e|ing|er)'
            ]
        },
        ClauseType.MOST_FAVORED_NATION: {
            "keywords": [
                "most favored nation", "MFN", "price protection",
                "best price", "anti-discrimination"
            ],
            "patterns": [
                r'most[\-\s]favored[\-\s]nation',
                r'(MFN|price\s+protection)',
                r'best\s+price|most\s+favorable'
            ]
        },
        ClauseType.DELIVERABLES: {
            "keywords": [
                "deliverable", "delivery", "statement of work",
                "scope of work", "services", "work product", "SOW"
            ],
            "patterns": [
                r'deliver(able|y|ies)?',
                r'statement\s+of\s+work',
                r'scope\s+of\s+(work|service)s?',
                r'SOW'
            ]
        },
        ClauseType.AUDIT_RIGHTS: {
            "keywords": [
                "audit", "audit rights", "inspection", "inspect",
                "books and records", "examine", "review records"
            ],
            "patterns": [
                r'(right\s+to\s+)?audit',
                r'(books?\s+(and|&)\s+)records',
                r'inspect(ion|or)?'
            ]
        },
        ClauseType.INSURANCE: {
            "keywords": [
                "insurance", "coverage", "general liability",
                "professional liability", "additional insured",
                "certificate of insurance", "E&O", "cyber"
            ],
            "patterns": [
                r'insur(e|ance|ed|er)',
                r'(general|professional)\s+(liability\s+)?insurance',
                r'additional\s+insured',
                r'certificate\s+of\s+insurance'
            ]
        },
        ClauseType.SUBCONTRACTING: {
            "keywords": [
                "subcontract", "subcontracting", "subcontractor",
                "third-party", "sub-processor"
            ],
            "patterns": [
                r'sub[\-]?contract(or|ing)?',
                r'sub[\-]?processor',
                r'third[\-]?part(y|ies)\s+(performance|services)'
            ]
        },
        ClauseType.PUBLICITY: {
            "keywords": [
                "publicity", "marketing", "logo use", "press release",
                "brand", "customer list"
            ],
            "patterns": [
                r'publicit(y|ies)',
                r'(logo|marketing|brand)\s+use',
                r'press\s+release'
            ]
        },
        ClauseType.COMPLIANCE_WITH_LAWS: {
            "keywords": [
                "compliance with laws", "legal compliance", "anti-corruption",
                "anti-bribery", "FCPA", "export controls", "sanctions"
            ],
            "patterns": [
                r'compliance\s+with\s+(all\s+)?(applicable\s+)?laws?',
                r'(anti|non)[\-]?(corruption|bribery)',
                r'(FCPA|export\s+controls|sanctions)'
            ]
        },
        ClauseType.NOTICE: {
            "keywords": [
                "notice", "notices", "communications",
                "written notice", "email notice"
            ],
            "patterns": [
                r'(all\s+)?(formal\s+)?notices?\s+(shall|must|will)',
                r'notice\s+(provision|requirements?|clause)'
            ]
        },
        ClauseType.WAIVER: {
            "keywords": [
                "waiver", "no waiver", "non-waiver",
                "failure to enforce"
            ],
            "patterns": [
                r'(no[\s-]?)?waiver',
                r'failure\s+to\s+(enforce|exercise|insist)'
            ]
        },
        ClauseType.SEVERABILITY: {
            "keywords": [
                "severability", "severable", "invalidity",
                "unenforceable", "partial invalidity"
            ],
            "patterns": [
                r'severab(le|ility)',
                r'(invalid|unenforceable).*(severed|modified|valid)',
                r'partial\s+invalidity'
            ]
        },
        ClauseType.COUNTERPARTS: {
            "keywords": [
                "counterparts", "counter-signature", "electronic signature",
                "execution", "signed copies"
            ],
            "patterns": [
                r'counterparts?',
                r'(electronic|digital)\s+signature',
                r'counter[\-]?signature'
            ]
        },
        ClauseType.ORDER_OF_PRECEDENCE: {
            "keywords": [
                "order of precedence", "conflict of terms",
                "hierarchy", "prevail", "controls"
            ],
            "patterns": [
                r'order\s+of\s+precedence',
                r'conflict\s+between\s+(terms|documents)',
                r'in\s+case\s+of\s+conflict'
            ]
        },
        ClauseType.REPRESENTATIONS: {
            "keywords": [
                "representation", "representations", "represents",
                "acknowledge", "acknowledgment"
            ],
            "patterns": [
                r'represent(ation|s|ed)',
                r'acknowled(g(e|es|ement))'
            ]
        },
        ClauseType.COVENANTS: {
            "keywords": [
                "covenant", "covenants", "shall", "agree to",
                "covenant and agree"
            ],
            "patterns": [
                r'covenant(s)?',
                r'covenant\s+and\s+agree'
            ]
        },
    }

    # Section heading -> clause type mapping
    SECTION_CLAUSE_NAMES = {
        "indemnification": ClauseType.INDEMNIFICATION,
        "indemnity": ClauseType.INDEMNIFICATION,
        "hold harmless": ClauseType.INDEMNIFICATION,
        "limitation of liability": ClauseType.LIMITATION_OF_LIABILITY,
        "limitation on liability": ClauseType.LIMITATION_OF_LIABILITY,
        "limits of liability": ClauseType.LIMITATION_OF_LIABILITY,
        "limit of liability": ClauseType.LIMITATION_OF_LIABILITY,
        "liability cap": ClauseType.LIMITATION_OF_LIABILITY,
        "exclusion of damages": ClauseType.LIMITATION_OF_LIABILITY,
        "governing law": ClauseType.GOVERNING_LAW,
        "choice of law": ClauseType.GOVERNING_LAW,
        "applicable law": ClauseType.GOVERNING_LAW,
        "confidentiality": ClauseType.CONFIDENTIALITY,
        "non-disclosure": ClauseType.CONFIDENTIALITY,
        "non disclosure": ClauseType.CONFIDENTIALITY,
        "non-compete": ClauseType.NON_COMPETE,
        "noncompetition": ClauseType.NON_COMPETE,
        "covenant not to compete": ClauseType.NON_COMPETE,
        "non-solicitation": ClauseType.NON_SOLICITATION,
        "non solicitation": ClauseType.NON_SOLICITATION,
        "force majeure": ClauseType.FORCE_MAJEURE,
        "warranty": ClauseType.WARRANTY,
        "warranties": ClauseType.WARRANTY,
        "representations and warranties": ClauseType.WARRANTY,
        "disclaimer": ClauseType.DISCLAIMER,
        "as is": ClauseType.DISCLAIMER,
        "disclaimer of warranties": ClauseType.DISCLAIMER,
        "assignment": ClauseType.ASSIGNMENT,
        "entire agreement": ClauseType.ENTIRE_AGREEMENT,
        "merger": ClauseType.ENTIRE_AGREEMENT,
        "integration": ClauseType.ENTIRE_AGREEMENT,
        "termination for convenience": ClauseType.TERMINATION_FOR_CONVENIENCE,
        "term and termination": ClauseType.TERMINATION_FOR_CAUSE,
        "termination": ClauseType.TERMINATION_FOR_CAUSE,
        "default": ClauseType.TERMINATION_FOR_CAUSE,
        "change of control": ClauseType.TERMINATION_FOR_CHANGE_OF_CONTROL,
        "survival": ClauseType.SURVIVAL,
        "surviving obligations": ClauseType.SURVIVAL,
        "arbitration": ClauseType.DISPUTE_RESOLUTION_ARBITRATION,
        "dispute resolution": ClauseType.DISPUTE_RESOLUTION_ARBITRATION,
        "mediation": ClauseType.DISPUTE_RESOLUTION_MEDIATION,
        "jurisdiction": ClauseType.DISPUTE_RESOLUTION_LITIGATION,
        "venue": ClauseType.DISPUTE_RESOLUTION_LITIGATION,
        "waiver of jury trial": ClauseType.DISPUTE_RESOLUTION_LITIGATION,
        "intellectual property": ClauseType.INTELLECTUAL_PROPERTY,
        "proprietary rights": ClauseType.INTELLECTUAL_PROPERTY,
        "ownership": ClauseType.INTELLECTUAL_PROPERTY,
        "data protection": ClauseType.DATA_PROTECTION,
        "privacy": ClauseType.DATA_PROTECTION,
        "data privacy": ClauseType.DATA_PROTECTION,
        "payment": ClauseType.PAYMENT_TERMS,
        "fees and expenses": ClauseType.PAYMENT_TERMS,
        "compensation": ClauseType.PAYMENT_TERMS,
        "pricing": ClauseType.PAYMENT_TERMS,
        "billing": ClauseType.PAYMENT_TERMS,
        "invoicing": ClauseType.PAYMENT_TERMS,
        "late payments": ClauseType.INTEREST_ON_LATE_PAYMENTS,
        "interest": ClauseType.INTEREST_ON_LATE_PAYMENTS,
        "late fees": ClauseType.INTEREST_ON_LATE_PAYMENTS,
        "liquidated damages": ClauseType.LIQUIDATED_DAMAGES,
        "service credits": ClauseType.LIQUIDATED_DAMAGES,
        "exclusivity": ClauseType.EXCLUSIVITY,
        "exclusive dealing": ClauseType.EXCLUSIVITY,
        "most favored nation": ClauseType.MOST_FAVORED_NATION,
        "most-favored-nation": ClauseType.MOST_FAVORED_NATION,
        "audit": ClauseType.AUDIT_RIGHTS,
        "audit rights": ClauseType.AUDIT_RIGHTS,
        "inspection": ClauseType.AUDIT_RIGHTS,
        "records": ClauseType.AUDIT_RIGHTS,
        "insurance": ClauseType.INSURANCE,
        "insurance requirements": ClauseType.INSURANCE,
        "coverage": ClauseType.INSURANCE,
        "subcontracting": ClauseType.SUBCONTRACTING,
        "subcontractors": ClauseType.SUBCONTRACTING,
        "third-party performance": ClauseType.SUBCONTRACTING,
        "publicity": ClauseType.PUBLICITY,
        "marketing": ClauseType.PUBLICITY,
        "logo use": ClauseType.PUBLICITY,
        "press release": ClauseType.PUBLICITY,
        "compliance with laws": ClauseType.COMPLIANCE_WITH_LAWS,
        "legal compliance": ClauseType.COMPLIANCE_WITH_LAWS,
        "anti-corruption": ClauseType.COMPLIANCE_WITH_LAWS,
        "notice": ClauseType.NOTICE,
        "notices": ClauseType.NOTICE,
        "communications": ClauseType.NOTICE,
        "waiver": ClauseType.WAIVER,
        "no waiver": ClauseType.WAIVER,
        "severability": ClauseType.SEVERABILITY,
        "partial invalidity": ClauseType.SEVERABILITY,
        "counterparts": ClauseType.COUNTERPARTS,
        "counter-signature": ClauseType.COUNTERPARTS,
        "electronic signature": ClauseType.COUNTERPARTS,
        "order of precedence": ClauseType.ORDER_OF_PRECEDENCE,
        "hierarchy": ClauseType.ORDER_OF_PRECEDENCE,
        "conflict of terms": ClauseType.ORDER_OF_PRECEDENCE,
        "deliverables": ClauseType.DELIVERABLES,
        "scope": ClauseType.DELIVERABLES,
        "scope of work": ClauseType.DELIVERABLES,
        "definitions": ClauseType.DEFINITIONS,
        "representations": ClauseType.REPRESENTATIONS,
        "covenants": ClauseType.COVENANTS,
    }

    def __init__(self):
        self._compiled_patterns: Dict[ClauseType, List[Pattern]] = {}
        self._compile_patterns()

    def _compile_patterns(self):
        """Pre-compile regex patterns for performance."""
        for clause_type, config in self.CLAUSE_PATTERNS.items():
            patterns = []
            for p in config["patterns"]:
                try:
                    patterns.append(re.compile(p, re.IGNORECASE | re.MULTILINE))
                except re.error:
                    pass
            self._compiled_patterns[clause_type] = patterns

    def detect(self, contract: Contract) -> List[Clause]:
        """
        Detect all clause types present in the contract.

        Args:
            contract: Parsed Contract object.

        Returns:
            List of detected Clauses with type, text, and confidence.
        """
        clauses: List[Clause] = []
        full_text = contract.full_text

        for section in contract.sections:
            clauses.extend(self._detect_in_section(section, full_text))

        # Also scan the full text for clauses that span sections
        text_clauses = self._scan_full_text(full_text)
        existing_types = {c.clause_type for c in clauses}
        for c in text_clauses:
            if c.clause_type not in existing_types:
                clauses.append(c)

        return clauses

    def _detect_in_section(self, section: Section, full_text: str) -> List[Clause]:
        """Detect clauses within a single section (including subsections)."""
        clauses: List[Clause] = []

        # Check if the section heading itself identifies a clause type
        heading_lower = section.heading.lower().strip().rstrip(':. ')
        for name, clause_type in self.SECTION_CLAUSE_NAMES.items():
            if name in heading_lower or (len(name) > 4 and (heading_lower.startswith(name) or name.startswith(heading_lower))):
                clause_text = section.content if section.content else section.heading
                if clause_text:
                    clauses.append(Clause(
                        clause_type=clause_type,
                        section_ref=section.heading,
                        text=clause_text,
                        start_char=full_text.find(clause_text) if clause_text else 0,
                        end_char=(full_text.find(clause_text) + len(clause_text)) if clause_text else 0,
                        confidence=0.85,
                        metadata={"source": "section_heading"}
                    ))

        # Search section content for keywords/patterns
        found_types = {c.clause_type for c in clauses}
        for clause_type, patterns in self._compiled_patterns.items():
            if clause_type in found_types:
                continue

            match_count = 0
            for pattern in patterns:
                matches = pattern.findall(section.content)
                match_count += len(matches)
                if matches:
                    first_match = pattern.search(section.content)
                    if first_match:
                        start = max(0, first_match.start() - 100)
                        end = min(len(section.content), first_match.end() + 400)
                        clause_text = section.content[start:end]

                        confidence = min(0.5 + (match_count * 0.1), 0.95)

                        clauses.append(Clause(
                            clause_type=clause_type,
                            section_ref=section.heading,
                            text=clause_text,
                            start_char=full_text.find(clause_text),
                            end_char=full_text.find(clause_text) + len(clause_text),
                            confidence=confidence,
                            metadata={"match_count": match_count}
                        ))
                        break

        # Recurse into subsections
        for subsection in section.subsections:
            clauses.extend(self._detect_in_section(subsection, full_text))

        return clauses

    def _scan_full_text(self, text: str) -> List[Clause]:
        """Scan full text for clause patterns that might span sections."""
        clauses: List[Clause] = []
        found_types = set()

        for clause_type, patterns in self._compiled_patterns.items():
            match_count = 0
            for pattern in patterns:
                matches = pattern.findall(text)
                match_count += len(matches)

                if matches and match_count >= 1:
                    first_match = pattern.search(text)
                    if first_match:
                        found_types.add(clause_type)
                        start = max(0, first_match.start() - 100)
                        end = min(len(text), first_match.end() + 400)
                        clause_text = text[start:end]

                        confidence = min(0.4 + (match_count * 0.1), 0.9)
                        clauses.append(Clause(
                            clause_type=clause_type,
                            section_ref=None,
                            text=clause_text,
                            start_char=start,
                            end_char=end,
                            confidence=confidence,
                            metadata={"match_count": match_count, "source": "full_text"}
                        ))

        return clauses