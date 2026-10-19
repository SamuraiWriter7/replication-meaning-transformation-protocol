
# RMTP ↔ Trace Integration Mapping

**RMTP Version:** 0.1.0  
**Status:** Experimental / Non-Normative  
**Integration Type:** Conceptual Mapping

## 1. Purpose

This document describes how RMTP evaluation records may be associated with external Trace and Receipt systems.

The integration objective is to preserve the provenance and lifecycle of replication-related decisions.

RMTP does not replace an existing Trace protocol.

It supplies structured records that may be linked to independently generated authorization and runtime evidence.

## 2. Core Principle

> A replication proposal must be distinguishable from an actual replication event.

A proposed offspring is not a deployed offspring.

An authority reference is not an authorization receipt.

A retirement condition is not proof of retirement.

These distinctions must be preserved in trace records.

## 3. Conceptual Trace Flow

    Replication Intent
           |
           v
    Meaning Conversion
           |
           v
    Replication Proposal
           |
           v
    External Authorization
           |
           v
    Deployment Event
           |
           v
    Runtime Observation
           |
           v
    Termination Event
           |
           v
    Resource Release

The first three stages are represented by RMTP v0.1 data objects.

Later stages require external systems.

## 4. Mapping Table

| RMTP field | Trace interpretation |
|---|---|
| `intent_id` | Originating request identifier |
| `requester_id` | Requesting agent reference |
| `observed_deficit_ref` | Referenced observation |
| `conversion_id` | Conversion decision identifier |
| `intent_ref` | Decision-to-request relationship |
| `evidence_refs` | Referenced assessment evidence |
| `selected_outcome` | Decision outcome |
| `plan_id` | Proposed plan identifier |
| `conversion_ref` | Plan-to-decision relationship |
| `authority_ref` | Claimed authority reference |
| `parent_id` | Proposed parent identifier |
| `offspring_id` | Proposed offspring identifier |
| `lineage_ref` | Proposed lineage relationship |
| `retirement_condition` | Planned lifecycle termination trigger |

These values are identifiers and claims until independently verified.

## 5. Trace Relationships

A Trace system should preserve relationships such as:

    Intent --evaluated_by--> Conversion

    Conversion --produces--> Plan

    Plan --references--> Authority

    Parent --proposes_offspring--> Offspring

    Deployment --instantiates--> Offspring

    Termination --ends--> Deployed Instance

The relationship labels above are illustrative.

They are not registered normative relationship types in RMTP v0.1.

Implementations must map them to the vocabulary of the selected Trace protocol.

## 6. Proposed Versus Observed State

Trace systems must distinguish:

### Proposed State

Information about what RMTP recommends or evaluates.

Examples:

- Requested instances
- Proposed instance count
- Planned lifetime
- Planned resource limits

### Authorized State

Information independently issued by an authority system.

Examples:

- Authorized target scope
- Authorized maximum instance count
- Authorization validity period

### Observed Runtime State

Information produced by a runtime or monitoring system.

Examples:

- Actual deployment
- Actual resource usage
- Actual termination
- Actual cleanup

A proposed state must not be silently promoted into an observed state.

## 7. Lineage Integrity

Every proposed offspring must have a lineage record.

RMTP semantic validation checks structural relationships, including:

- Number of lineage records
- Duplicate offspring identifiers
- Parent consistency
- Authority reference consistency

An external Trace system should additionally support:

- Tamper-evident record storage
- Reliable event ordering
- Identity verification
- Cross-system correlation
- Retention and privacy controls

RMTP v0.1 does not define cryptographic signatures or canonical record hashing.

## 8. Trace and Authority Separation

A Trace record does not grant permission.

The presence of a valid historical record must not be interpreted as authorization for future replication.

Likewise, an authorization reference must not be interpreted as proof that a proposed instance was created.

Trace supports auditability.

Authority systems control permission.

Runtime systems establish observed execution events.

## 9. Failure Conditions

Trace-integrated implementations should detect:

- Missing parent references
- Duplicate offspring identifiers
- Missing decision references
- Contradictory lineage records
- Unauthorized state transitions
- Deployment without a corresponding authorization record
- Retirement claims without termination evidence
- Inconsistent proposed and observed instance counts

Detection of these conditions should trigger independent review or incident handling.

No missing evidence should be silently fabricated.

## 10. Data Minimization

Trace collection should preserve sufficient evidence for accountability while avoiding unnecessary exposure of sensitive information.

Implementations should:

- Use stable opaque identifiers where appropriate
- Avoid recording secrets
- Minimize sensitive payload retention
- Apply access controls to trace records
- Define retention and deletion policies
- Distinguish record deletion from actual agent termination

Complete traceability does not require unlimited retention of raw logs.

## 11. External Receipt Integration

Potential receipt types include:

- Evaluation Receipt
- Authorization Receipt
- Deployment Receipt
- Revocation Receipt
- Termination Receipt
- Resource Release Receipt

These are possible integration artifacts.

They are not new mandatory RMTP v0.1 schemas.

Receipt formats must be defined by their owning protocol or by a later RMTP version.

## 12. Current Conformance Scope

RMTP v0.1 validates its own intent, conversion, and plan structures.

The initial fixture suite checks selected cross-record relationships.

It does not verify:

- External authorization receipts
- Actual deployment events
- Actual termination events
- Cryptographic signatures
- Distributed trace consistency
- Real-time resource consumption

These require separate implementations and tests.

## 13. Future Extensions

Potential extensions include:

- Trace receipt adapters
- Signed conversion records
- Cross-domain lineage records
- Revocation evidence
- Retirement confirmation
- Resource release verification
- Cross-protocol conformance fixtures

These extensions should preserve backward compatibility where feasible.

## 14. Design Statement

**Intent records what was requested. Conversion records what was evaluated. Plans record what was proposed. External receipts establish what was authorized and observed.**

Traceability must preserve these distinctions.
