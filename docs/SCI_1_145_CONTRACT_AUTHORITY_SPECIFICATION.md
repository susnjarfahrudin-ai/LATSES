# LAT-CES — SCI 1–145 Contract + Authority Specification

**Baseline:** `main @ dd2fc81f5347aa30adb1c0c84a9a90fbec8544dd` (PR #328 merged).

## Purpose

This specification closes the SCI 1–145 contract/authority layer before adversarial testing. It introduces no runtime module, adapter, or production abstraction. The existing SCI action classification is preserved from the central map. `MOVE` and `NEW` are explicitly `NO` in this closure pass unless a later evidence-backed review changes them.

The canonical SCI titles, implementation locations, tests and historical proof remain in `LATCES_SCI_1_145_CENTRAL_MAP_b7d1bcb0.md`. This matrix adds the missing epistemic/authority axis without replacing that source map.

## Non-negotiable epistemic invariants

1. `SOURCE != AUTHORITY`. External sources provide data; they cannot confer `VERIFIED`.
2. `INPUT != EVIDENCE`. Receipt of data is not proof.
3. `EVIDENCE != VERIFIED EVIDENCE`. `VERIFIED` is the result of an authorized verification transition.
4. `VERIFIED EVIDENCE != VALIDATED ENGINEERING RESULT`. Engineering admission additionally requires scope, identity, units, provenance, integrity and validation.
5. Claims MUST retain lineage to supporting evidence.
6. Knowledge evolution MUST create a new revision/event and preserve prior revisions and lineage.
7. Geodetic, meteorological, structural/statics and external scientific data are candidate inputs; none self-promotes to `VERIFIED`.
8. AI has no independent epistemic authority.
9. UNKNOWN, conflict, missing provenance, identity failure, incompatible units/coordinates or failed verification are valid rejection states.
10. Tests are downstream evidence of this specification; tests MUST NOT invent new epistemic rules.

## Canonical authority path

`REALITY / EXTERNAL SOURCE → INPUT → EVIDENCE CANDIDATE → VERIFICATION → VERIFIED EVIDENCE → CLAIM / KNOWLEDGE EVOLUTION → VALIDATION → ENGINEERING CORE ADMISSION`

## SCI 1–145 authority matrix

| SCI ID | Existing action | Primary epistemic role | Authority rule | External self-VERIFIED | MOVE | NEW |
|---|---|---|---|---|---|---|
| LAT-SCOPE-0001 | KEEP | GOVERNANCE | Defines/controls admissibility and authority policy; does not fabricate evidence. | NO | NO | NO |
| LAT-SCI-CORE-0002 | ADAPT | CLAIM / KNOWLEDGE CONTRACT | May formulate/consume claims; MUST retain supporting evidence lineage. | NO | NO | NO |
| LAT-SCI-CORE-0003 | ADAPT | CLAIM / KNOWLEDGE CONTRACT | May formulate/consume claims; MUST retain supporting evidence lineage. | NO | NO | NO |
| LAT-SCI-CORE-0004 | ADAPT | CLAIM / KNOWLEDGE CONTRACT | May formulate/consume claims; MUST retain supporting evidence lineage. | NO | NO | NO |
| LAT-SCI-CORE-0005 | ADAPT | CLAIM / KNOWLEDGE CONTRACT | May formulate/consume claims; MUST retain supporting evidence lineage. | NO | NO | NO |
| LAT-SCI-CORE-0006 | ADAPT | CLAIM / KNOWLEDGE CONTRACT | May formulate/consume claims; MUST retain supporting evidence lineage. | NO | NO | NO |
| LAT-SCI-CORE-0007 | ADAPT | CLAIM / KNOWLEDGE CONTRACT | May formulate/consume claims; MUST retain supporting evidence lineage. | NO | NO | NO |
| LAT-SCI-CORE-0008 | ADAPT | CLAIM / KNOWLEDGE CONTRACT | May formulate/consume claims; MUST retain supporting evidence lineage. | NO | NO | NO |
| LAT-SCI-CORE-0009 | ADAPT | CLAIM / KNOWLEDGE CONTRACT | May formulate/consume claims; MUST retain supporting evidence lineage. | NO | NO | NO |
| LAT-SCI-CORE-0010 | MERGE | INPUT / VERIFICATION | May define/receive input; MUST NOT self-promote to VERIFIED. | NO | NO | NO |
| LAT-SCI-CORE-0011 | MERGE | INPUT / VERIFICATION | May define/receive input; MUST NOT self-promote to VERIFIED. | NO | NO | NO |
| LAT-SCI-CORE-0012 | MERGE | INPUT / VERIFICATION | May define/receive input; MUST NOT self-promote to VERIFIED. | NO | NO | NO |
| LAT-SCI-CORE-0013 | MERGE | INPUT / VERIFICATION | May define/receive input; MUST NOT self-promote to VERIFIED. | NO | NO | NO |
| LAT-SCI-CORE-0014 | MERGE | INPUT / VERIFICATION | May define/receive input; MUST NOT self-promote to VERIFIED. | NO | NO | NO |
| LAT-SCI-CORE-0015 | MERGE | INPUT / VERIFICATION | May define/receive input; MUST NOT self-promote to VERIFIED. | NO | NO | NO |
| LAT-SCI-CORE-0016 | KEEP | INPUT | May define/receive input; MUST NOT self-promote to VERIFIED. | NO | NO | NO |
| LAT-SCI-CORE-0017 | KEEP | INPUT | May define/receive input; MUST NOT self-promote to VERIFIED. | NO | NO | NO |
| LAT-SCI-CORE-0018 | KEEP | INPUT | May define/receive input; MUST NOT self-promote to VERIFIED. | NO | NO | NO |
| LAT-SCI-CORE-0019 | KEEP | INPUT | May define/receive input; MUST NOT self-promote to VERIFIED. | NO | NO | NO |
| LAT-SCI-CORE-0020 | KEEP | INPUT | May define/receive input; MUST NOT self-promote to VERIFIED. | NO | NO | NO |
| LAT-SCI-CORE-0021 | KEEP | INPUT | May define/receive input; MUST NOT self-promote to VERIFIED. | NO | NO | NO |
| LAT-SCI-CORE-0022 | KEEP | INPUT | May define/receive input; MUST NOT self-promote to VERIFIED. | NO | NO | NO |
| LAT-SCI-CORE-0023 | KEEP | INPUT | May define/receive input; MUST NOT self-promote to VERIFIED. | NO | NO | NO |
| LAT-SCI-CORE-0024 | KEEP | INPUT | May define/receive input; MUST NOT self-promote to VERIFIED. | NO | NO | NO |
| LAT-SCI-CORE-0025 | KEEP | INPUT | May define/receive input; MUST NOT self-promote to VERIFIED. | NO | NO | NO |
| LAT-SCI-CORE-0026 | KEEP | INPUT | May define/receive input; MUST NOT self-promote to VERIFIED. | NO | NO | NO |
| LAT-SCI-CORE-0027 | KEEP | INPUT | May define/receive input; MUST NOT self-promote to VERIFIED. | NO | NO | NO |
| LAT-SCI-CORE-0028 | KEEP | INPUT | May define/receive input; MUST NOT self-promote to VERIFIED. | NO | NO | NO |
| LAT-SCI-CORE-0029 | KEEP | CALCULATION / VERIFICATION | May calculate from admitted inputs; calculation alone does not create VERIFIED source evidence. | NO | NO | NO |
| LAT-SCI-CORE-0030 | KEEP | CALCULATION / VERIFICATION | May calculate from admitted inputs; calculation alone does not create VERIFIED source evidence. | NO | NO | NO |
| LAT-SCI-CORE-0031 | KEEP | CALCULATION / VERIFICATION | May calculate from admitted inputs; calculation alone does not create VERIFIED source evidence. | NO | NO | NO |
| LAT-SCI-CORE-0032 | KEEP | CALCULATION / VERIFICATION | May calculate from admitted inputs; calculation alone does not create VERIFIED source evidence. | NO | NO | NO |
| LAT-SCI-CORE-0033 | KEEP | CALCULATION / VERIFICATION | May calculate from admitted inputs; calculation alone does not create VERIFIED source evidence. | NO | NO | NO |
| LAT-SCI-CORE-0034 | KEEP | CALCULATION / VERIFICATION | May calculate from admitted inputs; calculation alone does not create VERIFIED source evidence. | NO | NO | NO |
| LAT-SCI-CORE-0035 | KEEP | CALCULATION / VERIFICATION | May calculate from admitted inputs; calculation alone does not create VERIFIED source evidence. | NO | NO | NO |
| LAT-SCI-CORE-0036 | KEEP | CALCULATION / VERIFICATION | May calculate from admitted inputs; calculation alone does not create VERIFIED source evidence. | NO | NO | NO |
| LAT-SCI-CORE-0037 | KEEP | CALCULATION / VERIFICATION | May calculate from admitted inputs; calculation alone does not create VERIFIED source evidence. | NO | NO | NO |
| LAT-SCI-CORE-0038 | KEEP | CALCULATION / VERIFICATION | May calculate from admitted inputs; calculation alone does not create VERIFIED source evidence. | NO | NO | NO |
| LAT-SCI-CORE-0039 | KEEP | CALCULATION / VERIFICATION | May calculate from admitted inputs; calculation alone does not create VERIFIED source evidence. | NO | NO | NO |
| LAT-SCI-CORE-0040 | KEEP | CALCULATION / VERIFICATION | May calculate from admitted inputs; calculation alone does not create VERIFIED source evidence. | NO | NO | NO |
| LAT-SCI-CORE-0041 | KEEP | CALCULATION / VERIFICATION | May calculate from admitted inputs; calculation alone does not create VERIFIED source evidence. | NO | NO | NO |
| LAT-SCI-CORE-0042 | KEEP | CALCULATION / VERIFICATION | May calculate from admitted inputs; calculation alone does not create VERIFIED source evidence. | NO | NO | NO |
| LAT-SCI-CORE-0043 | KEEP | CALCULATION / VERIFICATION | May calculate from admitted inputs; calculation alone does not create VERIFIED source evidence. | NO | NO | NO |
| LAT-SCI-CORE-0044 | KEEP | CALCULATION / VERIFICATION | May calculate from admitted inputs; calculation alone does not create VERIFIED source evidence. | NO | NO | NO |
| LAT-SCI-CORE-0045 | KEEP | CALCULATION / VERIFICATION | May calculate from admitted inputs; calculation alone does not create VERIFIED source evidence. | NO | NO | NO |
| LAT-SCI-CORE-0046 | KEEP | EVIDENCE / MEASUREMENT | May record evidence/provenance; state promotion requires verification authority. | NO | NO | NO |
| LAT-SCI-CORE-0047 | KEEP | EVIDENCE / MEASUREMENT | May record evidence/provenance; state promotion requires verification authority. | NO | NO | NO |
| LAT-SCI-CORE-0048 | KEEP | EVIDENCE / MEASUREMENT | May record evidence/provenance; state promotion requires verification authority. | NO | NO | NO |
| LAT-SCI-CORE-0049 | KEEP | EVIDENCE / MEASUREMENT | May record evidence/provenance; state promotion requires verification authority. | NO | NO | NO |
| LAT-SCI-CORE-0050 | KEEP | EVIDENCE / MEASUREMENT | May record evidence/provenance; state promotion requires verification authority. | NO | NO | NO |
| LAT-SCI-CORE-0051 | KEEP | EVIDENCE / MEASUREMENT | May record evidence/provenance; state promotion requires verification authority. | NO | NO | NO |
| LAT-SCI-CORE-0052 | KEEP | EVIDENCE / MEASUREMENT | May record evidence/provenance; state promotion requires verification authority. | NO | NO | NO |
| LAT-SCI-CORE-0053 | KEEP | EVIDENCE / MEASUREMENT | May record evidence/provenance; state promotion requires verification authority. | NO | NO | NO |
| LAT-SCI-CORE-0054 | MERGE | EVIDENCE / PROVENANCE | May record evidence/provenance; state promotion requires verification authority. | NO | NO | NO |
| LAT-SCI-CORE-0055 | MERGE | EVIDENCE / PROVENANCE | May record evidence/provenance; state promotion requires verification authority. | NO | NO | NO |
| LAT-SCI-CORE-0056 | MERGE | EVIDENCE / PROVENANCE | May record evidence/provenance; state promotion requires verification authority. | NO | NO | NO |
| LAT-SCI-CORE-0057 | MERGE | EVIDENCE / PROVENANCE | May record evidence/provenance; state promotion requires verification authority. | NO | NO | NO |
| LAT-SCI-CORE-0058 | MERGE | VALIDATION | May establish fitness/scope only when validation criteria are satisfied. | NO | NO | NO |
| LAT-SCI-CORE-0059 | MERGE | VALIDATION | May establish fitness/scope only when validation criteria are satisfied. | NO | NO | NO |
| LAT-SCI-CORE-0060 | MERGE | VALIDATION | May establish fitness/scope only when validation criteria are satisfied. | NO | NO | NO |
| LAT-SCI-CORE-0061 | MERGE | VALIDATION | May establish fitness/scope only when validation criteria are satisfied. | NO | NO | NO |
| LAT-SCI-CORE-0062 | KEEP | CLAIM / REASONING | May formulate/consume claims; MUST retain supporting evidence lineage. | NO | NO | NO |
| LAT-SCI-CORE-0063 | KEEP | CLAIM / REASONING | May formulate/consume claims; MUST retain supporting evidence lineage. | NO | NO | NO |
| LAT-SCI-CORE-0064 | KEEP | CLAIM / REASONING | May formulate/consume claims; MUST retain supporting evidence lineage. | NO | NO | NO |
| LAT-SCI-CORE-0065 | KEEP | CLAIM / REASONING | May formulate/consume claims; MUST retain supporting evidence lineage. | NO | NO | NO |
| LAT-SCI-CORE-0066 | KEEP | CLAIM / REASONING | May formulate/consume claims; MUST retain supporting evidence lineage. | NO | NO | NO |
| LAT-SCI-CORE-0067 | KEEP | CLAIM / REASONING | May formulate/consume claims; MUST retain supporting evidence lineage. | NO | NO | NO |
| LAT-SCI-CORE-0068 | KEEP | CLAIM / REASONING | May formulate/consume claims; MUST retain supporting evidence lineage. | NO | NO | NO |
| LAT-SCI-CORE-0069 | KEEP | CLAIM / REASONING | May formulate/consume claims; MUST retain supporting evidence lineage. | NO | NO | NO |
| LAT-SCI-CORE-0070 | KEEP | CLAIM / REASONING | May formulate/consume claims; MUST retain supporting evidence lineage. | NO | NO | NO |
| LAT-SCI-CORE-0071 | KEEP | CLAIM / REASONING | May formulate/consume claims; MUST retain supporting evidence lineage. | NO | NO | NO |
| LAT-SCI-CORE-0072 | KEEP | CLAIM / REASONING | May formulate/consume claims; MUST retain supporting evidence lineage. | NO | NO | NO |
| LAT-SCI-CORE-0073 | KEEP | CLAIM / REASONING | May formulate/consume claims; MUST retain supporting evidence lineage. | NO | NO | NO |
| LAT-SCI-CORE-0074 | KEEP | KNOWLEDGE EVOLUTION | May create a new knowledge revision/event; prior revision and lineage MUST remain reconstructible. | NO | NO | NO |
| LAT-SCI-CORE-0075 | KEEP | KNOWLEDGE EVOLUTION | May create a new knowledge revision/event; prior revision and lineage MUST remain reconstructible. | NO | NO | NO |
| LAT-SCI-CORE-0076 | KEEP | KNOWLEDGE EVOLUTION | May create a new knowledge revision/event; prior revision and lineage MUST remain reconstructible. | NO | NO | NO |
| LAT-SCI-CORE-0077 | KEEP | KNOWLEDGE EVOLUTION | May create a new knowledge revision/event; prior revision and lineage MUST remain reconstructible. | NO | NO | NO |
| LAT-SCI-CORE-0078 | KEEP | GOVERNANCE | Defines/controls admissibility and authority policy; does not fabricate evidence. | NO | NO | NO |
| LAT-SCI-CORE-0079 | KEEP | GOVERNANCE | Defines/controls admissibility and authority policy; does not fabricate evidence. | NO | NO | NO |
| LAT-SCI-CORE-0080 | KEEP | GOVERNANCE | Defines/controls admissibility and authority policy; does not fabricate evidence. | NO | NO | NO |
| LAT-SCI-CORE-0081 | KEEP | GOVERNANCE | Defines/controls admissibility and authority policy; does not fabricate evidence. | NO | NO | NO |
| LAT-SCI-CORE-0082 | KEEP | KNOWLEDGE PRESERVATION | May organize/preserve knowledge; MUST retain provenance and lineage. | NO | NO | NO |
| LAT-SCI-CORE-0083 | KEEP | KNOWLEDGE PRESERVATION | May organize/preserve knowledge; MUST retain provenance and lineage. | NO | NO | NO |
| LAT-SCI-CORE-0084 | KEEP | KNOWLEDGE PRESERVATION | May organize/preserve knowledge; MUST retain provenance and lineage. | NO | NO | NO |
| LAT-SCI-CORE-0085 | KEEP | KNOWLEDGE PRESERVATION | May organize/preserve knowledge; MUST retain provenance and lineage. | NO | NO | NO |
| LAT-SCI-CORE-0086 | KEEP | INTEGRITY / TRUST | May establish integrity/trust conditions; integrity alone is not scientific truth. | NO | NO | NO |
| LAT-SCI-CORE-0087 | KEEP | INTEGRITY / TRUST | May establish integrity/trust conditions; integrity alone is not scientific truth. | NO | NO | NO |
| LAT-SCI-CORE-0088 | KEEP | INTEGRITY / TRUST | May establish integrity/trust conditions; integrity alone is not scientific truth. | NO | NO | NO |
| LAT-SCI-CORE-0089 | KEEP | INTEGRITY / TRUST | May establish integrity/trust conditions; integrity alone is not scientific truth. | NO | NO | NO |
| LAT-SCI-CORE-0090 | KEEP | VERIFICATION / ASSURANCE | Verification authority may establish VERIFIED only when defined criteria and evidence lineage are satisfied. | NO | NO | NO |
| LAT-SCI-CORE-0091 | KEEP | VERIFICATION / ASSURANCE | Verification authority may establish VERIFIED only when defined criteria and evidence lineage are satisfied. | NO | NO | NO |
| LAT-SCI-CORE-0092 | KEEP | VERIFICATION / ASSURANCE | Verification authority may establish VERIFIED only when defined criteria and evidence lineage are satisfied. | NO | NO | NO |
| LAT-SCI-CORE-0093 | KEEP | VERIFICATION / ASSURANCE | Verification authority may establish VERIFIED only when defined criteria and evidence lineage are satisfied. | NO | NO | NO |
| LAT-SCI-CORE-0094 | KEEP | KNOWLEDGE LIFECYCLE | May create a new knowledge revision/event; prior revision and lineage MUST remain reconstructible. | NO | NO | NO |
| LAT-SCI-CORE-0095 | KEEP | KNOWLEDGE LIFECYCLE | May create a new knowledge revision/event; prior revision and lineage MUST remain reconstructible. | NO | NO | NO |
| LAT-SCI-CORE-0096 | KEEP | KNOWLEDGE LIFECYCLE | May create a new knowledge revision/event; prior revision and lineage MUST remain reconstructible. | NO | NO | NO |
| LAT-SCI-CORE-0097 | KEEP | KNOWLEDGE LIFECYCLE | May create a new knowledge revision/event; prior revision and lineage MUST remain reconstructible. | NO | NO | NO |
| LAT-SCI-CORE-0098 | KEEP | KNOWLEDGE ECOSYSTEM | May organize/preserve knowledge; MUST retain provenance and lineage. | NO | NO | NO |
| LAT-SCI-CORE-0099 | KEEP | KNOWLEDGE ECOSYSTEM | May organize/preserve knowledge; MUST retain provenance and lineage. | NO | NO | NO |
| LAT-SCI-CORE-0100 | KEEP | KNOWLEDGE ECOSYSTEM | May organize/preserve knowledge; MUST retain provenance and lineage. | NO | NO | NO |
| LAT-SCI-CORE-0101 | KEEP | KNOWLEDGE ECOSYSTEM | May organize/preserve knowledge; MUST retain provenance and lineage. | NO | NO | NO |
| LAT-SCI-CORE-0102 | KEEP | KNOWLEDGE INTELLIGENCE / VERIFICATION | Verification authority may establish VERIFIED only when defined criteria and evidence lineage are satisfied. | NO | NO | NO |
| LAT-SCI-CORE-0103 | KEEP | KNOWLEDGE INTELLIGENCE / VERIFICATION | Verification authority may establish VERIFIED only when defined criteria and evidence lineage are satisfied. | NO | NO | NO |
| LAT-SCI-CORE-0104 | KEEP | KNOWLEDGE INTELLIGENCE / VERIFICATION | Verification authority may establish VERIFIED only when defined criteria and evidence lineage are satisfied. | NO | NO | NO |
| LAT-SCI-CORE-0105 | KEEP | KNOWLEDGE INTELLIGENCE / VERIFICATION | Verification authority may establish VERIFIED only when defined criteria and evidence lineage are satisfied. | NO | NO | NO |
| LAT-SCI-CORE-0106 | KEEP | KNOWLEDGE INTELLIGENCE / VERIFICATION | Verification authority may establish VERIFIED only when defined criteria and evidence lineage are satisfied. | NO | NO | NO |
| LAT-SCI-CORE-0107 | KEEP | KNOWLEDGE INTELLIGENCE / VERIFICATION | Verification authority may establish VERIFIED only when defined criteria and evidence lineage are satisfied. | NO | NO | NO |
| LAT-SCI-CORE-0108 | KEEP | KNOWLEDGE INTELLIGENCE / VERIFICATION | Verification authority may establish VERIFIED only when defined criteria and evidence lineage are satisfied. | NO | NO | NO |
| LAT-SCI-CORE-0109 | KEEP | KNOWLEDGE INTELLIGENCE / VERIFICATION | Verification authority may establish VERIFIED only when defined criteria and evidence lineage are satisfied. | NO | NO | NO |
| LAT-SCI-CORE-0110 | KEEP | GOVERNANCE / ASSURANCE | Defines/controls admissibility and authority policy; does not fabricate evidence. | NO | NO | NO |
| LAT-SCI-CORE-0111 | KEEP | GOVERNANCE / ASSURANCE | Defines/controls admissibility and authority policy; does not fabricate evidence. | NO | NO | NO |
| LAT-SCI-CORE-0112 | KEEP | GOVERNANCE / ASSURANCE | Defines/controls admissibility and authority policy; does not fabricate evidence. | NO | NO | NO |
| LAT-SCI-CORE-0113 | KEEP | GOVERNANCE / ASSURANCE | Defines/controls admissibility and authority policy; does not fabricate evidence. | NO | NO | NO |
| LAT-SCI-CORE-0114 | KEEP | GOVERNANCE / ASSURANCE | Defines/controls admissibility and authority policy; does not fabricate evidence. | NO | NO | NO |
| LAT-SCI-CORE-0115 | KEEP | GOVERNANCE / ASSURANCE | Defines/controls admissibility and authority policy; does not fabricate evidence. | NO | NO | NO |
| LAT-SCI-CORE-0116 | KEEP | GOVERNANCE / ASSURANCE | Defines/controls admissibility and authority policy; does not fabricate evidence. | NO | NO | NO |
| LAT-SCI-CORE-0117 | KEEP | GOVERNANCE / ASSURANCE | Defines/controls admissibility and authority policy; does not fabricate evidence. | NO | NO | NO |
| LAT-SCI-CORE-0118 | KEEP | KNOWLEDGE EVOLUTION / GOVERNANCE | May create a new knowledge revision/event; prior revision and lineage MUST remain reconstructible. | NO | NO | NO |
| LAT-SCI-CORE-0119 | KEEP | KNOWLEDGE EVOLUTION / GOVERNANCE | May create a new knowledge revision/event; prior revision and lineage MUST remain reconstructible. | NO | NO | NO |
| LAT-SCI-CORE-0120 | KEEP | KNOWLEDGE EVOLUTION / GOVERNANCE | May create a new knowledge revision/event; prior revision and lineage MUST remain reconstructible. | NO | NO | NO |
| LAT-SCI-CORE-0121 | KEEP | KNOWLEDGE EVOLUTION / GOVERNANCE | May create a new knowledge revision/event; prior revision and lineage MUST remain reconstructible. | NO | NO | NO |
| LAT-SCI-CORE-0122 | KEEP | INTEGRATION / FEDERATION | May federate/admit external information as candidate input; external source retains no epistemic authority. | NO | NO | NO |
| LAT-SCI-CORE-0123 | KEEP | INTEGRATION / FEDERATION | May federate/admit external information as candidate input; external source retains no epistemic authority. | NO | NO | NO |
| LAT-SCI-CORE-0124 | KEEP | INTEGRATION / FEDERATION | May federate/admit external information as candidate input; external source retains no epistemic authority. | NO | NO | NO |
| LAT-SCI-CORE-0125 | KEEP | INTEGRATION / FEDERATION | May federate/admit external information as candidate input; external source retains no epistemic authority. | NO | NO | NO |
| LAT-SCI-CORE-0126 | KEEP | INTEGRATION / FEDERATION | May federate/admit external information as candidate input; external source retains no epistemic authority. | NO | NO | NO |
| LAT-SCI-CORE-0127 | KEEP | INTEGRATION / FEDERATION | May federate/admit external information as candidate input; external source retains no epistemic authority. | NO | NO | NO |
| LAT-SCI-CORE-0128 | KEEP | INTEGRATION / FEDERATION | May federate/admit external information as candidate input; external source retains no epistemic authority. | NO | NO | NO |
| LAT-SCI-CORE-0129 | KEEP | INTEGRATION / FEDERATION | May federate/admit external information as candidate input; external source retains no epistemic authority. | NO | NO | NO |
| LAT-SCI-CORE-0130 | KEEP | SECURITY / VERIFICATION | Security authority protects integrity/authority paths; security status is not engineering truth. | NO | NO | NO |
| LAT-SCI-CORE-0131 | KEEP | SECURITY / VERIFICATION | Security authority protects integrity/authority paths; security status is not engineering truth. | NO | NO | NO |
| LAT-SCI-CORE-0132 | KEEP | SECURITY / VERIFICATION | Security authority protects integrity/authority paths; security status is not engineering truth. | NO | NO | NO |
| LAT-SCI-CORE-0133 | KEEP | SECURITY / VERIFICATION | Security authority protects integrity/authority paths; security status is not engineering truth. | NO | NO | NO |
| LAT-SCI-CORE-0134 | KEEP | SECURITY / VERIFICATION | Security authority protects integrity/authority paths; security status is not engineering truth. | NO | NO | NO |
| LAT-SCI-CORE-0135 | KEEP | SECURITY / VERIFICATION | Security authority protects integrity/authority paths; security status is not engineering truth. | NO | NO | NO |
| LAT-SCI-CORE-0136 | KEEP | SECURITY / VERIFICATION | Security authority protects integrity/authority paths; security status is not engineering truth. | NO | NO | NO |
| LAT-SCI-CORE-0137 | KEEP | SECURITY / VERIFICATION | Security authority protects integrity/authority paths; security status is not engineering truth. | NO | NO | NO |
| LAT-SCI-CORE-0138 | KEEP | SECURITY / VERIFICATION | Security authority protects integrity/authority paths; security status is not engineering truth. | NO | NO | NO |
| LAT-SCI-CORE-0139 | KEEP | SECURITY / VERIFICATION | Security authority protects integrity/authority paths; security status is not engineering truth. | NO | NO | NO |
| LAT-SCI-CORE-0140 | KEEP | SECURITY / VERIFICATION | Security authority protects integrity/authority paths; security status is not engineering truth. | NO | NO | NO |
| LAT-SCI-CORE-0141 | KEEP | SECURITY GOVERNANCE / VERIFICATION | Security authority protects integrity/authority paths; security status is not engineering truth. | NO | NO | NO |
| LAT-SCI-CORE-0142 | KEEP | SECURITY GOVERNANCE / VERIFICATION | Security authority protects integrity/authority paths; security status is not engineering truth. | NO | NO | NO |
| LAT-SCI-CORE-0143 | KEEP | SECURITY GOVERNANCE / VERIFICATION | Security authority protects integrity/authority paths; security status is not engineering truth. | NO | NO | NO |
| LAT-SCI-CORE-0144 | KEEP | SECURITY GOVERNANCE / VERIFICATION | Security authority protects integrity/authority paths; security status is not engineering truth. | NO | NO | NO |
| LAT-SCI-CORE-0145 | KEEP | SECURITY GOVERNANCE / VERIFICATION | Security authority protects integrity/authority paths; security status is not engineering truth. | NO | NO | NO |

## Adversarial tests derived only from this specification

- T1: external result → direct `VERIFIED` MUST FAIL.
- T2: external result → UNKNOWN candidate → valid verification MAY become VERIFIED.
- T3: measurement missing required traceability MUST NOT become VERIFIED.
- T4: claim without supporting evidence lineage MUST FAIL.
- T5: knowledge evolution without new evidence/verification lineage MUST FAIL.
- T6: prior knowledge revision MUST remain reconstructible after evolution.
- T7: location MUST NOT self-assert meteorology or statics.
- T8: meteorological/statics data MUST NOT self-assert engineering validity.
- T9: broken identity/units/coordinates/provenance/integrity MUST block engineering admission.
- T10: only evidence satisfying the complete admission contract MAY enter Engineering Core.

## Closure condition

**No new module or adapter is justified by this matrix alone.** A future module requires an explicit gap in this contract, followed by an evidence-backed change to this matrix before implementation.
