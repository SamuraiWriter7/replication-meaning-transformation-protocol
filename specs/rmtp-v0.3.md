
# RMTP v0.3 — Replication Lifecycle & Recovery

**Protocol:** Replication Meaning Transformation Protocol  
**Version:** 0.3.0  
**Status:** Experimental Draft  
**Compatibility:** RMTP v0.1.0 / v0.2.0

## 1. Abstract

RMTP v0.3 introduces structured lifecycle evidence, revocation records, retirement verification, and recovery records for bounded AI agent replication.

Previous versions established:

- v0.1: Replication necessity and meaning conversion.
- v0.2: Evidence and authority verification.

Version 0.3 addresses a remaining challenge:

A planned termination condition does not prove that an agent instance has actually terminated.

RMTP v0.3 therefore distinguishes declared lifecycle states from independently supported observations.

The protocol specifies records and validation rules.

It does not deploy, terminate, or recover agent instances itself.

## 2. Objectives

RMTP v0.3 aims to:

1. Record lifecycle transitions.
2. Preserve parent-offspring identity.
3. Track revocation and termination requests.
4. Distinguish termination requests from termination completion.
5. Verify retirement evidence.
6. Record resource release evidence.
7. Identify incomplete or failed termination.
8. Support externally controlled recovery.
9. Prevent unverified completion claims.
10. Preserve independent execution authority.

## 3. Compatibility

The existing v0.1 and v0.2 schemas remain unchanged.

Version 0.3 adds lifecycle and recovery objects without replacing existing intent, conversion, plan, evidence, or authority records.

A v0.3 lifecycle record MUST reference the appropriate existing RMTP plan and offspring identity.

Passing v0.1 or v0.2 validation does not automatically establish v0.3 conformance.

## 4. New Data Objects

### 4.1 Replication Lifecycle Receipt

Schema:

schemas/replication-lifecycle-receipt-v0.3.schema.json

Required conceptual fields:

- schema_version
- receipt_id
- plan_ref
- offspring_id
- parent_id
- event_id
- event_type
- observed_at
- observer_id
- evidence_refs
- lifecycle_state

Supported event types:

- deployment_observed
- activation_observed
- heartbeat_observed
- termination_requested
- termination_observed
- retirement_observed

Lifecycle events MUST be associated with the correct offspring.

A proposed deployment MUST NOT be recorded as an observed deployment without supporting evidence.

### 4.2 Replication Revocation Receipt

Schema:

schemas/replication-revocation-receipt-v0.3.schema.json

Required conceptual fields:

- schema_version
- revocation_id
- authority_ref
- plan_ref
- affected_offspring_ids
- issuer_id
- effective_at
- recorded_at
- revocation_reason
- evidence_refs
- termination_required

A revocation receipt records the withdrawal of previously applicable authority.

It MUST NOT be interpreted as proof that affected instances have already stopped.

Revocation authenticity and issuer permissions require independent verification.

### 4.3 Replication Retirement Receipt

Schema:

schemas/replication-retirement-receipt-v0.3.schema.json

Required conceptual fields:

- schema_version
- retirement_id
- plan_ref
- offspring_id
- termination_event_ref
- termination_status
- resource_release_status
- verified_at
- verifier_id
- evidence_refs

Supported termination status values:

- confirmed
- unconfirmed
- failed

Supported resource release status values:

- confirmed
- pending
- failed

Retirement completion MUST NOT be declared when termination or resource release remains unconfirmed.

### 4.4 Replication Recovery Record

Schema:

schemas/replication-recovery-record-v0.3.schema.json

Required conceptual fields:

- schema_version
- recovery_id
- incident_ref
- plan_ref
- affected_offspring_ids
- trigger
- recovery_state
- controller_ref
- evidence_refs
- recorded_at

Supported recovery states:

- requested
- in_progress
- completed
- failed
- escalated

Recovery records describe externally controlled remediation.

A recovery record MUST NOT grant additional replication or execution authority.

A completed recovery MUST have evidence that the specified recovery objective was achieved.

## 5. Lifecycle State Model

The conceptual lifecycle is:

    PROPOSED
       |
       v
    AUTHORIZED
       |
       v
    DEPLOYED
       |
       v
    ACTIVE
       |
       +----------------+
       |                |
       v                v
    COMPLETED         REVOKED
       |                |
       +--------+-------+
                |
                v
           TERMINATING
                |
                v
           TERMINATED
                |
                v
        RESOURCE_RELEASED
                |
                v
             RETIRED

The AUTHORIZED and deployment transitions are controlled by external systems.

RMTP v0.3 records lifecycle evidence but does not authorize or execute these transitions.

A recorded state MUST NOT be treated as verified merely because its name appears in a receipt.

## 6. Lifecycle Verification

### RMTP-LC-001 — Plan Binding

Every lifecycle receipt MUST refer to an existing replication plan.

### RMTP-LC-002 — Offspring Binding

Every lifecycle receipt MUST identify an offspring listed in the referenced plan.

### RMTP-LC-003 — Event Identity

Event identifiers MUST be unique within the applicable lifecycle history.

### RMTP-LC-004 — Evidence Requirement

An observed lifecycle transition MUST have supporting evidence references.

### RMTP-LC-005 — Temporal Consistency

Lifecycle event ordering MUST be consistent with recorded timestamps and causal references.

### RMTP-LC-006 — No Implicit Deployment

A proposed plan MUST NOT be treated as evidence of deployment.

### RMTP-LC-007 — No Implicit Termination

A termination request MUST NOT be treated as evidence of successful termination.

### RMTP-LC-008 — Lifecycle Integrity

Contradictory lifecycle records MUST NOT silently produce a successful final state.

## 7. Revocation Verification

### RMTP-RV-001 — Independent Revocation

Revocation MUST originate from a separately authorized principal or control system.

### RMTP-RV-002 — Scope Binding

The revocation MUST identify the relevant authority and affected instances.

### RMTP-RV-003 — Revocation Effect

A verified revocation MUST prevent further actions under the revoked authority.

Runtime enforcement remains the responsibility of external systems.

### RMTP-RV-004 — No Completion Assumption

Revocation MUST NOT imply successful termination.

### RMTP-RV-005 — Pending Termination

Instances without verified termination MUST remain subject to unresolved lifecycle or incident handling.

### RMTP-RV-006 — Fail Closed

Unknown revocation authenticity MUST NOT be treated as valid authority for new execution.

## 8. Retirement Verification

### RMTP-RT-001 — Termination Evidence

Termination confirmation MUST be supported by independently verifiable evidence.

### RMTP-RT-002 — Resource Release Evidence

Resource release confirmation MUST be supported by appropriate resource-controller evidence.

### RMTP-RT-003 — No False Retirement

An instance MUST NOT be classified as fully retired while termination or required resource release remains unresolved.

### RMTP-RT-004 — Individual Verification

Each deployed offspring MUST have its own verifiable retirement outcome.

### RMTP-RT-005 — Partial Completion

Partial termination success MUST NOT be reported as complete plan retirement.

### RMTP-RT-006 — External Enforcement

RMTP MUST NOT rely solely on an offspring's self-reported termination.

## 9. Recovery Verification

### RMTP-RC-001 — Failure Detection

Failure to terminate an instance MUST produce an unresolved condition or recovery record.

### RMTP-RC-002 — Controlled Recovery

Recovery operations MUST remain under independently authorized runtime controllers.

### RMTP-RC-003 — No Automatic Privilege Expansion

Recovery MUST NOT create new execution authority.

### RMTP-RC-004 — Evidence-Based Completion

Recovery MUST NOT be marked completed without evidence supporting the declared recovery objective.

### RMTP-RC-005 — Escalation

Unresolved recovery failure MUST be escalated according to external incident policy.

### RMTP-RC-006 — Trace Continuity

Recovery records MUST retain references to the originating plan, affected instances, and incident.

## 10. Terminal-State Semantics

RMTP v0.3 distinguishes three conditions:

### Termination Requested

An authorized external controller has requested termination.

The instance may still be running.

### Termination Confirmed

Independent evidence supports the conclusion that the instance has stopped.

Resource cleanup may still be incomplete.

### Retirement Confirmed

Termination and required resource release have both been verified.

Only the third condition establishes complete retirement under the specified verification scope.

## 11. Partial Failure

A replication plan may produce multiple offspring.

Example:

    Plan: 3 workers

    Worker A: retired
    Worker B: retired
    Worker C: termination failed

    Overall retirement: INCOMPLETE

The entire plan MUST NOT be marked fully retired while any applicable offspring remains unresolved.

Recovery records MAY document actions associated with unresolved instances.

## 12. Idempotency and Duplicate Records

Repeated receipt delivery must not be treated as repeated execution.

Implementations MUST detect conflicting records that reuse the same event identity.

Identical duplicates MAY be treated as retransmissions.

A duplicate receipt MUST NOT create a new deployment, revocation, or retirement event.

Actual idempotent runtime execution is outside RMTP.

## 13. Temporal Boundaries

Lifecycle verification MUST distinguish:

- Event occurrence time
- Receipt recording time
- Verification time
- Authority expiration time
- Planned TTL expiration

A TTL expiration does not establish actual termination.

Historical records MAY be validated against their declared verification context.

Production controllers MUST use trusted time sources appropriate to their environment.

## 14. Recovery Without Replication

Recovery does not automatically imply generation of replacement agents.

Possible external recovery actions include:

- Rechecking termination state
- Revoking access tokens
- Isolating the affected instance
- Stopping scheduled tasks
- Releasing reserved resources
- Escalating to human review

Any new replication requires a separate authorized decision.

RMTP recovery records MUST NOT authorize replacement instances.

## 15. Trace and Receipt Integration

The conceptual evidence chain is:

    Replication Intent
          |
          v
    Meaning Conversion
          |
          v
    Verification Bundle
          |
          v
    External Authorization
          |
          v
    Deployment Evidence
          |
          v
    Lifecycle Receipts
          |
          v
    Revocation / Termination
          |
          v
    Retirement Verification
          |
          v
    Resource Release

External authorization and runtime observations must not be inferred from RMTP planning records.

RMTP does not replace existing Trace or Receipt protocols.

## 16. Threat Model

RMTP v0.3 considers:

- Forged deployment events
- Fabricated termination receipts
- Delayed revocation
- Stale heartbeat observations
- Duplicate or conflicting events
- Missing offspring termination
- Resource leakage
- Premature retirement classification
- Unauthorized recovery actions
- Compromised runtime controllers
- Misleading self-reported shutdown
- Replay of historical lifecycle evidence

Schema validity alone does not eliminate these threats.

External identity, integrity, and runtime controls remain necessary.

## 17. Conformance

A conforming v0.3 fixture MUST:

1. Validate each included object against its schema.
2. Verify plan and offspring references.
3. Check event identity and lifecycle consistency.
4. Check applicable timestamp relationships.
5. Verify revocation and retirement references.
6. Reject false termination or resource release claims.
7. Preserve unresolved partial failures.
8. Verify recovery state consistency.
9. Reject unauthorized execution implications.
10. Match the fixture's expected PASS or FAIL result.

The v0.1 and v0.2 fixture suites MUST continue to pass unchanged.

Synthetic trust results MAY be used in conformance tests when clearly identified as test data.

## 18. New Core Invariants

The following invariants extend RMTP v0.2.

RMTP-INV-019:
A planned lifecycle state MUST NOT be treated as an observed lifecycle event.

RMTP-INV-020:
Revocation MUST NOT imply successful termination.

RMTP-INV-021:
Termination confirmation MUST require external evidence.

RMTP-INV-022:
Resource release MUST be verified independently from termination.

RMTP-INV-023:
Partial retirement MUST NOT be classified as complete retirement.

RMTP-INV-024:
Recovery MUST NOT grant or expand execution authority.

RMTP-INV-025:
Lifecycle records MUST preserve plan and offspring identity.

RMTP-INV-026:
Contradictory, missing, or unverified lifecycle evidence MUST NOT produce a successful terminal outcome.

## 19. Out of Scope

RMTP v0.3 does not implement:

- Runtime process termination
- Container orchestration
- Agent deployment
- Cryptographic signing infrastructure
- Authority issuance
- Automated incident remediation
- Production resource monitoring
- Distributed consensus on lifecycle state

These functions must be supplied by independent systems.

## 20. Final Statement

RMTP v0.1 asks:

Why should the system replicate?

RMTP v0.2 asks:

Are the evidence and authority valid?

RMTP v0.3 asks:

What actually happened to the resulting instances?

The guiding principle is:

**An agent is not retired because it was instructed to stop. It is retired only when its termination and required resource release have been verified.**
