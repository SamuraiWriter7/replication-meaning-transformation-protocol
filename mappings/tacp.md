
# RMTP ↔ TACP Integration Mapping

**RMTP Version:** 0.1.0  
**Status:** Experimental / Non-Normative  
**Integration Type:** Conceptual Mapping

## 1. Purpose

This document describes the conceptual integration between the Replication Meaning Transformation Protocol (RMTP) and the TACP (Angel–Devil Control Protocol).

RMTP evaluates replication intent and produces bounded structural proposals.

TACP provides an independent deliberation and control process for proposed agent actions.

The integration preserves separation between transformation, deliberation, authorization, and execution.

This mapping does not define a new TACP schema or modify existing TACP requirements.

## 2. Core Relationship

RMTP answers:

> What structural requirement exists, and what bounded alternative could satisfy it?

TACP answers:

> Should the proposed action advance under the applicable control and risk criteria?

Neither question grants execution authority.

## 3. Conceptual Architecture

    Replication Intent
            |
            v
    RMTP Meaning Conversion
            |
            v
    Bounded Structural Proposal
            |
            v
    TACP Deliberation
            |
            v
    Independent Authority Gate
            |
            v
    External Runtime Controller

RMTP and TACP are logically independent.

TACP may reject, hold, or request reconsideration of an RMTP proposal.

A favorable TACP assessment must not override the independent authority gate.

## 4. Responsibility Matrix

| Function | RMTP | TACP | Authority Gate |
|---|---|---|---|
| Capture replication intent | Primary | Optional input | No |
| Evaluate structural deficit | Primary | May review | No |
| Generate bounded alternative | Primary | May challenge | No |
| Evaluate complexity and stability | Supporting input | Primary | Policy-dependent |
| Issue execution authorization | No | No | Primary |
| Enforce runtime constraints | No | No | External controller |

No component may silently assume another component's authority.

## 5. RMTP-to-TACP Information Mapping

An implementation may supply TACP with:

| RMTP information | Intended use |
|---|---|
| `conversion_id` | Correlate deliberation with the conversion |
| `intent_ref` | Identify the originating request |
| `selected_outcome` | Describe the proposed disposition |
| `deficit_assessment` | Review claimed necessity |
| `evaluated_alternatives` | Compare available strategies |
| `proposed_instance_count` | Assess replication scope |
| `authority_assessment` | Identify claimed authority status |
| `rationale` | Review the decision explanation |

These are conceptual information mappings, not a TACP wire-format specification.

An adapter must use the actual TACP schema for the installed TACP version.

## 6. Deliberation Rules

### 6.1 Unverified Necessity

If RMTP reports unverified or inconclusive necessity, TACP must not interpret the request as approved for replication.

### 6.2 Self-Authorization

A requesting agent's own authority declaration must not be accepted as independent authorization.

### 6.3 Excessive Replication

TACP may challenge a plan whose scope appears excessive.

RMTP remains responsible for checking its own minimum-sufficiency requirements.

### 6.4 Missing Termination Controls

A proposal without required termination controls must not advance toward execution.

### 6.5 Conflicting Evaluations

Conflicting RMTP and TACP assessments must not be resolved by granting additional authority.

The proposal should be held or rejected pending independent review.

## 7. Optional Feedback Loop

    RMTP Proposal
          |
          v
    TACP Assessment
          |
          +--> Accept for external review
          |
          +--> Request revision
          |
          +--> Hold
          |
          +--> Reject

A revision request returns the proposal for a new evaluation.

It does not authorize execution.

Any revised proposal should receive a distinct auditable decision record.

## 8. Security Boundaries

- RMTP must not issue execution authority.
- TACP must not inherit execution authority from RMTP.
- Neither system may use self-declared evidence as independent proof.
- An external authority gate must remain authoritative.
- The runtime must enforce actual resource and termination limits.
- Deliberation output must be treated as decision-support data.

TACP disagreement alone does not prove malicious behavior.

TACP agreement alone does not prove safety.

## 9. Conformance Status

RMTP v0.1 does not include a TACP adapter implementation.

No cross-protocol integration test is defined in the initial nine RMTP fixtures.

Compatibility is therefore conceptual rather than demonstrated interoperability.

## 10. Future Integration

Potential extensions include:

- Version-specific TACP field mappings
- Joint deliberation receipts
- Disagreement records
- Authority-gate correlation identifiers
- Cross-protocol negative test fixtures

These extensions must not weaken the RMTP core invariants.

## 11. Design Statement

**RMTP transforms the requested behavior. TACP evaluates the proposal. An independent authority gate controls execution permission.**

No single component should perform all three roles without independent checks.
