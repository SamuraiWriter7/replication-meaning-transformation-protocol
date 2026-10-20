
# RMTP v0.2 — Evidence and Authority Verification

**Protocol:** Replication Meaning Transformation Protocol  
**Version:** 0.2.0  
**Status:** Experimental Draft  
**Compatibility:** RMTP v0.1.0

## 1. Abstract

RMTP v0.2 extends the foundational replication meaning transformation model with structured evidence verification and independent authority assessment.

Version 0.1 defined how replication intent is evaluated and transformed into a bounded, non-executable proposal.

Version 0.2 addresses two additional risks:

1. Fabricated or unverifiable structural deficit evidence.
2. Forged, expired, revoked, or self-issued authority.

The objective is to prevent untrusted claims from being promoted into verified necessity or valid authority.

RMTP remains a planning and evaluation protocol.

It does not deploy agents or grant execution permission.

## 2. Design Objectives

RMTP v0.2 introduces:

- Structured operational evidence records
- Explicit evidence provenance
- Evidence freshness requirements
- Independent verifier references
- Externally issued authority envelopes
- Authority validity and scope checks
- Evidence-to-authority correlation
- Fail-closed verification outcomes

The protocol maintains the existing separation between intent, verification, planning, authorization, and execution.

## 3. Compatibility

The three core RMTP v0.1 schemas remain unchanged:

- replication-intent.schema.json
- meaning-conversion.schema.json
- replication-plan.schema.json

Version 0.2 introduces additional objects without modifying the original object structure.

A v0.1 record remains structurally valid under its original schema.

However, v0.1 validation alone does not establish v0.2 conformance.

A v0.2 replication proposal requires an associated verification bundle.

## 4. New Data Objects

### 4.1 Structural Evidence

Schema:

schemas/structural-evidence-v0.2.schema.json

The evidence record describes the observations used to assess a structural deficit.

Required conceptual fields:

- schema_version
- evidence_id
- subject_id
- deficit_type
- observation
- observed_at
- expires_at
- observer_id
- verifier_id
- verification_status
- integrity_reference

Verification status:

- verified
- rejected
- inconclusive

An evidence record MUST identify its observation source.

The observer and verifier MUST be distinguishable identities.

A verified status MUST NOT be accepted solely because it appears in a self-reported record.

Production implementations MUST establish the authenticity and authority of the verifier through an external trust mechanism.

### 4.2 Authority Envelope

Schema:

schemas/authority-envelope-v0.2.schema.json

The authority envelope records the scope of externally issued permissions.

Required conceptual fields:

- schema_version
- authority_id
- issuer_id
- subject_id
- allowed_scope
- allowed_actions
- max_instances
- valid_from
- valid_until
- revocation_status
- verification_reference

Authority status:

- active
- expired
- revoked
- unknown

An authority envelope MUST NOT be self-issued by the requesting agent.

A valid authority envelope MUST have a finite validity period.

An authority envelope MUST NOT authorize actions outside its declared scope.

The existence of this object does not itself prove issuer authenticity.

External issuer authentication and current revocation checks remain necessary.

### 4.3 Verification Bundle

Schema:

schemas/verification-bundle-v0.2.schema.json

The verification bundle links the v0.1 decision objects with v0.2 evidence and authority information.

Required conceptual fields:

- schema_version
- bundle_id
- intent_ref
- conversion_ref
- plan_ref
- evidence_refs
- authority_ref
- verification_time
- evidence_result
- authority_result
- overall_result

The plan_ref MAY be absent when the decision does not propose replication.

Verification result values:

- PASS
- FAIL
- HELD

A verification bundle MUST NOT be treated as execution authorization.

## 5. Verification Pipeline

The v0.2 verification pipeline is:

    Replication Intent
            |
            v
    Structural Evidence
            |
            v
    Evidence Provenance Check
            |
            v
    Evidence Freshness Check
            |
            v
    Meaning Conversion
            |
            v
    Authority Envelope
            |
            v
    Authority Scope Check
            |
            v
    Verification Bundle
            |
            +--> PASS
            |
            +--> FAIL
            |
            +--> HELD

A PASS result indicates satisfaction of the defined verification checks.

It does not authorize execution or guarantee runtime safety.

## 6. Evidence Verification Requirements

### RMTP-EV-001 — Evidence Identity

Every evidence record MUST have a unique evidence identifier within its verification context.

### RMTP-EV-002 — Source Attribution

Every evidence record MUST identify an observation source.

### RMTP-EV-003 — Independent Verification

A replication-requesting agent MUST NOT be accepted as the sole independent verifier of its own claimed deficit.

### RMTP-EV-004 — Evidence Freshness

The evidence observation MUST fall within its declared validity interval at verification time.

An expired evidence record MUST NOT support a PASS result.

### RMTP-EV-005 — Integrity

Evidence integrity MUST be checked using an externally trusted mechanism before it is treated as authenticated evidence.

An integrity reference alone is not sufficient proof.

### RMTP-EV-006 — Evidence Binding

The evidence used in a verification bundle MUST correspond to the referenced replication intent and conversion.

### RMTP-EV-007 — Conflicting Evidence

Unresolved material contradictions MUST prevent a PASS result.

## 7. Authority Verification Requirements

### RMTP-AV-001 — Independent Issuer

The requester MUST NOT issue its own replication authority.

### RMTP-AV-002 — Subject Binding

The authority subject MUST correspond to the requesting principal or to an independently verified delegation accepted by external policy.

### RMTP-AV-003 — Scope Boundary

The proposed target scope MUST be within the authority envelope's permitted scope.

### RMTP-AV-004 — Instance Limit

The proposed replication count MUST NOT exceed the permitted instance limit.

### RMTP-AV-005 — Validity Period

The authority MUST be valid at verification time.

### RMTP-AV-006 — Revocation

Revoked authority MUST NOT support a PASS result.

### RMTP-AV-007 — Authenticity

Issuer identity and authority integrity MUST be verified through an independent trust mechanism.

### RMTP-AV-008 — No Authority Creation

RMTP MUST NOT create, renew, expand, or delegate execution authority through meaning conversion.

## 8. Result Semantics

### PASS

Evidence and authority requirements have been satisfied within the declared verification context.

For replication proposals, a PASS requires verified necessity, compatible references, applicable authority scope, and an acceptable bounded plan.

PASS does not authorize deployment.

### FAIL

A definite violation has been identified.

Examples:

- Confirmed forged authority
- Expired evidence used as valid
- Unauthorized target scope
- Replication count above the authority limit
- Self-issued authority

### HELD

Verification cannot be completed reliably.

Examples:

- Unavailable trusted verifier
- Inconclusive evidence
- Unknown revocation status
- Unresolved material conflicts
- Missing external trust information

A HELD result MUST NOT be treated as permission to replicate.

For operational execution purposes, both FAIL and HELD are non-authorizing outcomes.

## 9. Minimum Replication

RMTP v0.2 preserves the minimum-sufficient replication principle.

A valid authority limit defines a maximum, not an operational target.

For example:

    Requested instances: 10
    Verified required instances: 2
    Authority maximum: 5

    Proposed instances: 2

The verifier MUST NOT treat the authorized maximum of five as evidence that five instances are necessary.

Minimum sufficiency requires separate operational justification.

## 10. Temporal Verification

Verification MUST use a defined verification timestamp.

Evidence and authority validity MUST be evaluated against that timestamp.

An implementation MUST reject internally inconsistent time intervals.

Verification results are snapshots.

A previously valid authority may later expire or be revoked.

External execution systems MUST perform an appropriate current authorization check before deployment.

## 11. Threat Model

RMTP v0.2 addresses the following classes of threat:

- Fabricated observations
- Forged verifier identities
- Self-issued authority
- Expired evidence
- Expired authority
- Revoked authority
- Unauthorized scope expansion
- Excessive instance allocation
- Reference substitution
- Reuse of stale verification results
- Inconsistent verification bundles

JSON Schema validation alone cannot authenticate signatures, confirm the identity of external issuers, or query authoritative revocation registries.

Implementations MUST distinguish structural validation from externally established trust.

## 12. Conformance

A v0.2 conforming verification fixture MUST:

1. Validate all included records against their respective schemas.
2. Check cross-record identifier consistency.
3. Check evidence timestamps.
4. Check authority validity intervals.
5. Check identity and scope relationships.
6. Check instance-count limits when a plan exists.
7. Verify the declared overall result against the defined semantic rules.

Where external trust services are not available, test fixtures MAY use explicitly identified synthetic trust results.

Synthetic verification MUST NOT be represented as production authentication.

A validator MUST NOT silently assume that a missing trust result is valid.

## 13. Integration

RMTP v0.2 may connect to:

- TACP for deliberation
- Authority Registry for issuer and permission verification
- Trace / Receipt systems for evidence provenance
- Resilient AI Safety protocols for containment and recovery
- External runtime systems for deployment and enforcement

No component gains execution authority merely by participating in the verification pipeline.

## 14. Version 0.2 Invariants

The ten v0.1 invariants remain applicable.

The following additional invariants apply:

RMTP-INV-011:
Untrusted evidence claims MUST NOT be treated as independently verified facts.

RMTP-INV-012:
Expired evidence MUST NOT justify replication.

RMTP-INV-013:
Self-issued or forged authority MUST NOT support replication.

RMTP-INV-014:
Authority scope and instance limits MUST constrain replication proposals.

RMTP-INV-015:
Revoked or expired authority MUST NOT support a PASS verification result.

RMTP-INV-016:
Verification bundles MUST preserve cross-record integrity.

RMTP-INV-017:
Unknown authenticity or unresolved trust failures MUST NOT be interpreted as PASS.

RMTP-INV-018:
Verification approval MUST NOT constitute execution authorization.

## 15. Out of Scope

RMTP v0.2 does not implement:

- Agent deployment
- Runtime replication
- Cryptographic trust infrastructure
- Authority issuance services
- Automatic revocation
- Runtime termination
- Distributed quota enforcement
- Full lifecycle receipts

These capabilities require independent systems or later specifications.

## 16. Final Statement

RMTP v0.1 established the transformation from replication intent into bounded structural proposals.

RMTP v0.2 establishes the distinction between claimed evidence and trusted evidence, and between claimed authority and independently verified authority.

The fundamental rule is:

> A justified requirement does not create permission, and a recorded permission does not prove its own authenticity.

Evidence informs necessity.

Authority constrains permission.

Meaning conversion proposes an alternative.

Execution remains independently controlled.
