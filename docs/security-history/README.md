# LAT-CES Security Defense History

This directory is an independent, human-readable and machine-readable record
of security attacks, concrete defensive responses, measurements and verified
lessons.

## Authority boundary

- Runtime A/B defense components **read** this history; they never write it.
- A raw observation is not a lesson.
- Only a record with an explicit Verification SHA may be returned by the
  read-only learning interface.
- Promotion from `observed`/`contained` to `verified` is a reviewed repository
  change backed by the existing Verification pipeline.
- The history is not a second key, replay, persistence, threat-policy or flow
  authority.

## Mathematical learning loop

Each record should preserve enough quantitative evidence to compare attacks
across time and tune the model without silently moving its trusted baseline.
For the four-dimensional Flow Guard this includes:

`baseline → observed values → deviation → duration/trend → throttle → final action → Verification SHA`

The trusted baseline is never learned from untrusted traffic. The history can
show that an attack exceeded a boundary, but only verified evidence can become
an A/B lesson.

## Status lifecycle

`observed → contained → verified → learned`

A record may remain `contained` or `observed` until a concrete Verification
run proves the corresponding defense. `learned` means the verified record is
eligible for A/B recall.

## Ledger format

`defense_history.jsonl` is append-oriented repository evidence, not a runtime
write target. Each line is one immutable JSON record. Changes require normal
review and Verification; the runtime reader exposes no write operation.
