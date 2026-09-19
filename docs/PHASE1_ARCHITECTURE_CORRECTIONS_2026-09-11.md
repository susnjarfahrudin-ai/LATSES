# Phase I — Architecture Corrections (2026-09-11)

This document records only corrections to existing LAT-CES Phase I semantics and authority boundaries. It does not introduce a new architecture.

## Corrections applied

1. **Reality vs measurement authority**
   - Physical reality remains the ultimate reference.
   - Measurements are evidence about reality and are not themselves an absolute authority.
   - Verification remains required before measured data can support higher-level claims.

2. **Constitutional gateway fail-closed behavior**
   - `ConstitutionalEngine.verify_state()` returns violations as data.
   - `SecureGateway.process_request()` must therefore reject a request when the returned violation list is non-empty.
   - An exception is not the only rejection path.

3. **SKO approval semantics**
   - Recording `approved_by` is an attribution/governance action.
   - It must not be described as a verification signature or as proof that scientific evidence has become VERIFIED.
   - Scientific verification and governance approval remain distinct authority concepts.

## Explicit non-changes

- No new epistemic authority path is introduced.
- No external source, AI output, model, visualization tool, or adapter gains authority to declare VERIFIED evidence.
- No Phase II input implementation is introduced here.
- Existing canonical architecture remains the basis.
