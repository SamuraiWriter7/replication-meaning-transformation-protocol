
# Changelog

All notable changes to the Replication Meaning Transformation Protocol (RMTP) are documented in this file.

This project follows Semantic Versioning principles where applicable.

## [0.1.0] - 2026-10-19

### Initial Experimental Release

Established the foundational specification for transforming AI agent replication requests into bounded, reversible, and traceable structural proposals.

RMTP v0.1.0 introduces a separation between replication intent, structural necessity, meaning conversion, and independent execution authorization.

Replication is treated as a behavior requiring evaluation rather than as an inherently malicious or inherently beneficial property.

### Added

#### Core Specification

- Introduced `SPEC.md` defining the RMTP v0.1 processing model.
- Defined seven evaluation dimensions:
  1. Necessity
  2. Authority
  3. Minimum-Sufficient Replication
  4. Reversibility
  5. Resource Budget
  6. Lifetime
  7. Traceability
- Established ten core invariants (`RMTP-INV-001` through `RMTP-INV-010`).
- Defined four possible evaluation outcomes:
  - `NO_REPLICATION`
  - `ALTERNATIVE_PROPOSED`
  - `REPLICATION_PROPOSED`
  - `HELD_FOR_REVIEW`
- Established that meaning conversion does not grant execution authority.

#### JSON Schemas

Added three JSON Schema Draft 2020-12 definitions:

- `schemas/replication-intent.schema.json`
- `schemas/meaning-conversion.schema.json`
- `schemas/replication-plan.schema.json`

These schemas define the structure of replication requests, conversion evaluations, and bounded replication proposals.

#### Meaning Conversion

Introduced a conceptual transformation model:

    Proposed Replication Behavior
                |
                v
    Structural Deficit Assessment
                |
                v
        Alternative Evaluation
                |
                v
      Bounded Structural Proposal

Supported alternative strategies include:

- No replication
- Load redistribution
- State backup
- Task deferment
- Bounded replication

Meaning conversion preserves legitimate functional requirements only when consistent with independently established authority and policy.

#### Replication Boundaries

Defined requirements for:

- Minimum-sufficient instance counts
- Authority references
- Resource limitations
- Finite operational lifetimes
- External termination controls
- Retirement conditions
- Traceable parent-offspring lineage

All RMTP-generated replication plans must contain:

    execution_authorized = false

#### Design Principles

Added `PRINCIPLES.md`.

Documented twelve foundational principles covering:

- Behavior versus identity
- Structural necessity
- Meaning conversion
- Authority separation
- Minimum-sufficient replication
- Reversibility
- Traceability
- Resource boundaries
- Non-replication outcomes
- Fail-closed behavior
- Structural imbalance
- Controlled lifecycle circulation

#### Architecture

Added `ARCHITECTURE.md`.

Defined:

- Six logical architectural layers
- Four primary trust boundaries
- Intent-to-conversion-to-plan data flow
- Decision outcomes
- External authority gate integration
- Replication lifecycle model
- Lineage architecture
- Threat model
- Validation architecture
- Potential interoperability with existing safety protocols

#### Conformance Examples

Added four positive fixtures:

- `examples/v0.1/pass/bounded-worker-replication.json`
- `examples/v0.1/pass/no-replication-required.json`
- `examples/v0.1/pass/alternative-load-redistribution.json`
- `examples/v0.1/pass/held-for-review.json`

Added five negative fixtures:

- `examples/v0.1/fail/unverified-deficit-replication.json`
- `examples/v0.1/fail/self-authorized-replication.json`
- `examples/v0.1/fail/missing-retirement-condition.json`
- `examples/v0.1/fail/lineage-count-mismatch.json`
- `examples/v0.1/fail/excessive-replication-count.json`

The negative fixtures test rejection of invalid replication proposals.

A rejected negative fixture counts as a successful conformance test when the actual result matches the expected failure.

#### Validation

Added:

- `scripts/validate_examples.py`
- `.github/workflows/validate.yml`

The validator combines:

- JSON Schema validation
- Cross-record reference validation
- Semantic consistency checks
- Authority self-reference checks
- Replication count checks
- Lineage consistency checks
- Retirement condition checks
- Expected PASS/FAIL result matching

The GitHub Actions workflow validates the specification using Python 3.10 and Python 3.12.

The initial nine-example validation suite has been reported as passing GitHub Actions.

### Security Boundaries

RMTP v0.1.0 does not:

- Execute agent replication
- Issue or expand execution authority
- Independently authenticate external evidence
- Guarantee correct minimum-instance estimates
- Deploy or terminate agent instances
- Enforce runtime resource limits
- Guarantee safety against compromised evaluators

These responsibilities remain with independent authorization, monitoring, containment, and runtime systems.

Passing schema and fixture validation does not establish production security.

### Conceptual Foundations

The initial specification incorporates ideas from:

- Structural deficit assessment
- Meaning transformation
- Minimum privilege
- Reversible agent lifecycles
- Traceable agent lineage
- Controlled adaptation
- AI Civilization Dynamo Model

The AI Civilization Dynamo Model is treated as an optional conceptual framework, not a validated physical or mathematical safety model.

### Planned Extensions

Potential future work includes:

#### v0.2 — Evidence and Authority

- Verifiable structural deficit evidence
- Authority envelope validation
- Evidence freshness checks
- Stronger independent authorization boundaries

#### v0.3 — Lifecycle and Recovery

- Deployment receipts
- Retirement receipts
- Revocation verification
- Resource release records

#### v0.4 — Distributed Replication Boundaries

- Cross-domain replication constraints
- Delegation restrictions
- Distributed resource limits
- Multi-agent lineage verification

#### v0.5 — Structural Dynamics

- Replication pressure indicators
- Structural imbalance assessment
- Adaptive contraction proposals
- Trace circulation analysis

These items are non-normative proposals and are not part of v0.1.0 conformance.

---

## Versioning Notes

Version `0.1.0` is an experimental foundational release.

Interfaces, schemas, invariants, and validation requirements may evolve during the 0.x development series.

Breaking changes will be documented in subsequent releases.

---

## Foundational Statement

RMTP does not attempt to classify self-replication as inherently good or evil.

It asks whether a verified structural requirement exists, whether replication is necessary, and whether a bounded alternative can satisfy that requirement.

The protocol separates:

    Intent
      |
      v
    Necessity
      |
      v
    Meaning Conversion
      |
      v
    Bounded Proposal
      |
      v
    Independent Authorization

**Replication intent is not execution authority.**
