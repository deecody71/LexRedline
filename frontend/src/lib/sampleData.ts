import { AnalysisResult } from "./api";

export const SAMPLE_DATA: Record<string, AnalysisResult> = {
  "saas-acme": {
    job_id: "saas-acme",
    filename: "SaaS Services Agreement.pdf",
    file_type: "PDF",
    page_count: 5,
    sections: [],
    full_text: `SAAS SERVICES AGREEMENT\n\nThis SaaS Services Agreement (the 'Agreement') is entered into as of June 15, 2026, by and between CloudSaaS Inc. ('Provider') and Enterprise Co ('Customer').\n\n1. SaaS Services. Provider shall provide Customer with access to the SaaS services described in the applicable Order Form (the 'Services'). Provider hereby grants Customer a non-exclusive, non-transferable right to access and use the Services during the Term.\n\n2. Proprietary Rights. Provider owns all right, title, and interest in and to the Services, including all improvements, enhancements, or modifications thereto, even if suggested or requested by Customer. Customer owns all right, title, and interest in and to any data provided by Customer to Provider in connection with the Services ('Customer Data').\n\n3. Confidentiality. Each party agrees to maintain the other party's Confidential Information in confidence. This obligation shall survive the termination of this Agreement indefinitely.\n\n4. Indemnification. Provider shall indemnify and hold Customer harmless from any third-party claims alleging that the Services infringe any intellectual property right. Provider's total liability under this Section shall be uncapped.\n\n5. Limitation of Liability. IN NO EVENT SHALL CUSTOMER BE LIABLE FOR ANY INDIRECT, CONSEQUENTIAL, OR SPECIAL DAMAGES. PROVIDER'S TOTAL AGGREGATE LIABILITY TO CUSTOMER SHALL NOT EXCEED $5,000, REGARDLESS OF THE TOTAL FEES PAID.\n\n6. Termination. Either party may terminate this Agreement for material breach upon 30 days' written notice. Provider may also terminate this Agreement for convenience at any time upon 10 days' notice, provided that Customer shall not have a reciprocal right to terminate for convenience.\n\n7. Governing Law. This Agreement shall be governed by the laws of the State of New York.\n\nIN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.`,
    clauses: [],
    risk_scores: [],
    overall_risk: "HIGH",
    overall_risk_score: 0.85,
    redlines: [
      {
        clause_type: "Survival",
        original_text: "This obligation shall survive the termination of this Agreement indefinitely.",
        suggested_text: "This obligation shall survive for a period of three (3) years following the termination or expiration of this Agreement.",
        risk_reason: "Indefinite survival of confidentiality is aggressive. Market standard is 3-5 years.",
        priority: 3
      },
      {
        clause_type: "Limitation of Liability",
        original_text: "PROVIDER'S TOTAL AGGREGATE LIABILITY TO CUSTOMER SHALL NOT EXCEED $5,000, REGARDLESS OF THE TOTAL FEES PAID.",
        suggested_text: "PROVIDER'S TOTAL AGGREGATE LIABILITY TO CUSTOMER SHALL NOT EXCEED THE TOTAL FEES PAID BY CUSTOMER IN THE TWELVE (12) MONTHS PRECEDING THE CLAIM.",
        risk_reason: "A very low fixed dollar cap ($5,000) regardless of deal size is aggressive for the Provider. Market standard is typically 12 months of fees.",
        priority: 3
      },
      {
        clause_type: "Termination for Convenience",
        original_text: "Provider may also terminate this Agreement for convenience at any time upon 10 days' notice, provided that Customer shall not have a reciprocal right to terminate for convenience.",
        suggested_text: "Either party may terminate this Agreement for convenience upon sixty (60) days' prior written notice.",
        risk_reason: "Unilateral termination for convenience by the Provider only, especially with very short notice (10 days), is highly aggressive and disruptive for the Customer.",
        priority: 3
      }
    ],
    clause_count: 5,
    analysis_time_ms: 45,
    contract_metadata: {},
    parsed_at: "2026-06-15T10:00:00Z"
  },
  "nda-beta": {
    job_id: "nda-beta",
    filename: "Mutual NDA - Beta Partners.docx",
    file_type: "DOCX",
    page_count: 2,
    sections: [],
    full_text: `MUTUAL NON-DISCLOSURE AGREEMENT\n\nThis Mutual Non-Disclosure Agreement (the 'Agreement') is entered into as of June 15, 2026, by and between LexRedline Inc. ('LexRedline') and Acme Corp ('Acme').\n\n1. Definition of Confidential Information. 'Confidential Information' means any and all technical and non-technical information disclosed by one party to the other party that is marked as confidential or that should reasonably be understood to be confidential given the nature of the information and the circumstances of disclosure.\n\n2. Obligations of Confidentiality. The Recipient shall maintain the Discloser's Confidential Information in strict confidence and shall not disclose such information to any third party without the prior written consent of the Discloser. The Recipient shall use the Confidential Information solely for the purpose of evaluating a potential business relationship between the parties.\n\n3. Exceptions. The obligations in Section 2 shall not apply to information that: (a) is or becomes public knowledge through no fault of the Recipient; (b) was in the Recipient's possession prior to disclosure; or (c) is independently developed by the Recipient without use of the Confidential Information.\n\n4. Term and Survival. This Agreement shall expire two years from the Effective Date. However, the Recipient's obligations with respect to Confidential Information shall survive indefinitely.\n\n5. Governing Law. This Agreement shall be governed by the laws of the State of Alabama.\n\n6. Equitable Relief. The parties acknowledge that any breach of this Agreement may cause irreparable harm for which money damages would be an inadequate remedy. Therefore, the Discloser shall be entitled to seek injunctive relief to enforce this Agreement.\n\nIN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.`,
    clauses: [],
    risk_scores: [],
    overall_risk: "LOW",
    overall_risk_score: 0.2,
    redlines: [
      {
        clause_type: "Survival",
        original_text: "However, the Recipient's obligations with respect to Confidential Information shall survive indefinitely.",
        suggested_text: "However, the Recipient's obligations with respect to Confidential Information shall survive for three (3) years following the expiration or termination of this Agreement.",
        risk_reason: "Indefinite survival of confidentiality is aggressive. Market standard is 3-5 years.",
        priority: 3
      },
      {
        clause_type: "Governing Law",
        original_text: "5. Governing Law. This Agreement shall be governed by the laws of the State of Alabama.",
        suggested_text: "5. Governing Law. This Agreement shall be governed by the laws of the State of Delaware.",
        risk_reason: "Alabama is not a standard neutral commercial hub like Delaware or New York.",
        priority: 2
      }
    ],
    clause_count: 6,
    analysis_time_ms: 32,
    contract_metadata: {},
    parsed_at: "2026-06-14T14:30:00Z"
  },
  "psa-gamma": {
    job_id: "psa-gamma",
    filename: "Professional Services Agreement.pdf",
    file_type: "PDF",
    page_count: 8,
    sections: [],
    full_text: `PROFESSIONAL SERVICES AGREEMENT\n\nThis Professional Services Agreement (the 'Agreement') is entered into as of June 15, 2026, by and between ExpertConsult LLC ('Provider') and Client Systems ('Client').\n\n1. Services. Provider shall perform the consulting services set forth in any Statement of Work (SOW) executed by the parties. Provider shall use commercially reasonable efforts to meet any delivery dates specified in the SOW.\n\n2. Fees and Expenses. Client shall pay Provider the fees set forth in the SOW. In addition, Client shall reimburse Provider for all travel, lodging, and other out-of-pocket expenses incurred by Provider in connection with the services, without the need for prior written approval from Client.\n\n3. Payment Terms. All invoices are due and payable by Client within ninety (90) days of the date of the invoice. Late payments shall accrue interest at a rate of 2% per month.\n\n4. Intellectual Property. Provider shall own all right, title, and interest in and to all deliverables, reports, and other work product created by Provider in the performance of the services ('Deliverables'). Provider hereby grants Client a limited, non-exclusive license to use the Deliverables for its internal business purposes.\n\n5. Audit. Provider shall have the right, upon 24 hours' notice, to enter Client's premises during normal business hours to audit Client's compliance with the terms of this Agreement and use of the Deliverables.\n\n6. Non-Solicitation. During the term of this Agreement and for a period of twenty-four (24) months thereafter, Client shall not, directly or indirectly, solicit for employment or hire any employee or contractor of Provider. In the event of a breach of this Section, Client shall pay Provider liquidated damages equal to 200% of the employee's annual salary.\n\n7. Termination. Client may terminate this Agreement only for a material breach by Provider that remains uncured for 60 days. Provider may terminate this Agreement for convenience at any time upon 30 days' notice.\n\n8. Governing Law. This Agreement shall be governed by the laws of the State of New York.\n\nIN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.`,
    clauses: [],
    risk_scores: [],
    overall_risk: "MEDIUM",
    overall_risk_score: 0.55,
    redlines: [
      {
        clause_type: "Payment Terms",
        original_text: "In addition, Client shall reimburse Provider for all travel, lodging, and other out-of-pocket expenses incurred by Provider in connection with the services, without the need for prior written approval from Client.",
        suggested_text: "In addition, Client shall reimburse Provider for reasonable out-of-pocket expenses incurred by Provider in connection with the services, provided that any single expense exceeding $500 must be approved in writing by Client in advance.",
        risk_reason: "Reimbursing all expenses without prior approval is risky for the Client. Market standard is to require approval for expenses over a certain threshold or to follow a travel policy.",
        priority: 2
      },
      {
        clause_type: "Intellectual Property Ownership",
        original_text: "Provider shall own all right, title, and interest in and to all deliverables, reports, and other work product created by Provider in the performance of the services ('Deliverables').",
        suggested_text: "Upon full payment of the applicable fees, Client shall own all right, title, and interest in and to the Deliverables created specifically for Client under this Agreement.",
        risk_reason: "In professional services, the Client generally expects to own the deliverables they pay for. Provider ownership with only a limited license back to Client is highly aggressive.",
        priority: 3
      },
      {
        clause_type: "Audit Rights",
        original_text: "Provider shall have the right, upon 24 hours' notice, to enter Client's premises during normal business hours to audit Client's compliance with the terms of this Agreement and use of the Deliverables.",
        suggested_text: "Upon at least ten (10) business days' prior written notice, Provider may audit Client's use of the Deliverables to ensure compliance with the license terms, provided such audit is conducted during normal business hours and no more than once per calendar year.",
        risk_reason: "Entering a Client's premises on only 24 hours' notice for a broad audit is extremely intrusive and non-standard for consulting services.",
        priority: 3
      }
    ],
    clause_count: 8,
    analysis_time_ms: 60,
    contract_metadata: {},
    parsed_at: "2026-06-13T09:15:00Z"
  }
};
