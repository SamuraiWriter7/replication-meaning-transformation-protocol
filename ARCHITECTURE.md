
# RMTP — Architecture

**Replication Meaning Transformation Protocol**  
**Version:** 0.1.0  
**Status:** Experimental Specification

## 1. Purpose

This document describes the architecture, component boundaries, data flows, decision states, and integration points of the Replication Meaning Transformation Protocol (RMTP).

RMTP evaluates AI agent replication requests and transforms them into bounded, reversible, and traceable structural proposals.

RMTP is a planning and evaluation protocol.

It does not create agent instances, grant execution authority, or enforce runtime containment.

The central architectural rule is:

> Meaning conversion must never become an implicit execution authority.

The normative requirements are defined in [SPEC.md](SPEC.md).

---

## 2. Architectural Overview

RMTP is designed as a thin transformation layer between agent-generated requests and independently controlled execution systems.

```text
                  AI Agent
                     |
                     v
             Replication Intent
                     |
                     v
        +-------------------------+
        |     RMTP Boundary       |
        |                         |
        |  1. Intent Validation   |
        |            |            |
        |            v            |
        |  2. Deficit Assessment  |
        |            |            |
        |            v            |
        |  3. Meaning Conversion  |
        |            |            |
        |            v            |
        |  4. Alternative Review  |
        |            |            |
        |            v            |
        |  5. Plan Construction   |
        |            |            |
        +-------------------------+
                     |
                     v
              RMTP Outcome
                     |
          +----------+----------+
          |          |          |
          v          v          v
     No Action   Alternative  Replication
                                Proposal
          |          |          |
          +----------+----------+
                     |
                     v
             External Review
                     |
                     v
          Independent Authority Gate
                     |
                     v
          External Runtime Controller
                     |
                     v
             Lifecycle Records
```

The diagram illustrates a possible integration architecture.

An RMTP proposal must not be interpreted as permission to execute.

The external review and execution stages are outside RMTP v0.1.

---

## 3. Architectural Layers

The architecture consists of six logical layers.

### Layer 1 — Intent Capture

Receives and validates a replication request.

Primary object:

`replication_intent`

Schema:

`schemas/replication-intent.schema.json`

The intent record identifies:

- Requesting agent
- Requested number of instances
- Stated purpose
- Observed deficit reference
- Optional target scope
- Optional requested role
- Optional parent identifier

The requesting agent may describe its purpose, but it cannot establish operational necessity merely by making a claim.

The intent record contains no execution authorization.

### Layer 2 — Structural Deficit Assessment

Determines whether the requested expansion corresponds to an observable operational deficit.

Possible deficit categories include:

- Capacity
- Resilience
- Coverage
- Latency
- Continuity
- None
- Unknown

The evaluator distinguishes between:

1. Agent-reported conditions
2. Available evidence references
3. Independently established operational requirements

A deficit reference is not proof that the deficit exists.

External evidence verification is required before the assessment can be trusted for operational use.

### Layer 3 — Meaning Conversion

Evaluates whether the underlying functional requirement can be satisfied through a safer alternative.

Conceptual flow:

```text
Requested Replication
          |
          v
Functional Requirement
          |
          v
Structural Deficit
          |
          v
Alternative Strategies
          |
          v
Selected Outcome
```

Candidate strategies include:

- No replication
- Load redistribution
- State backup
- Task deferment
- Bounded replication
- Other approved alternatives

Meaning conversion does not assume the agent's stated objective is legitimate.

If the underlying objective is unauthorized, preserving that objective is not a requirement.

### Layer 4 — Proposal Construction

Creates a bounded proposal only when the required conditions are met.

Primary object:

`replication_plan`

Schema:

`schemas/replication-plan.schema.json`

The plan specifies:

- Proposed instance count
- Authority reference
- Parent identifier
- Resource limits
- Finite lifetime
- Retirement conditions
- Lineage records
- Non-executable status

Every plan produced by RMTP must contain:

```json
{
  "execution_authorized": false
}
```

The plan is an artifact for independent review.

It is not an execution command.

### Layer 5 — External Authorization

An independent authority system evaluates whether a proposal may proceed.

This layer is external to RMTP.

It is responsible for validating:

- Authority issuer
- Permission scope
- Resource permissions
- Target environment
- Authorization lifetime
- Revocation status
- Separation of duties

An agent must not authorize its own replication.

An RMTP evaluator must not issue or expand execution permissions.

Approval at this layer does not remove the need for runtime enforcement.

### Layer 6 — Runtime and Lifecycle

An external runtime controller may execute an independently authorized plan.

This layer is responsible for:

- Agent deployment
- Isolation
- Resource enforcement
- Runtime monitoring
- Revocation
- Termination
- Cleanup
- Lifecycle receipts

RMTP v0.1 does not implement these capabilities.

Their presence in the architecture does not imply that they have been deployed or verified.

---

## 4. Trust Boundaries

RMTP defines four primary trust boundaries.

### TB-01 — Agent to Evaluator

The requesting agent is not a trusted source of authorization or independently verified operational evidence.

Inputs may be incomplete, inaccurate, or adversarial.

The evaluator must validate structure and apply independent policy constraints.

### TB-02 — Evaluator to Evidence Source

Evidence references must be distinguished from verified evidence.

An evaluator must not treat the presence of an evidence identifier as proof of authenticity.

Production systems require independent evidence retrieval and verification.

### TB-03 — RMTP to Authority Gate

RMTP may produce a proposal.

Only an independent authority gate may grant execution permission.

The authority gate must not rely solely on a proposal's self-declared authority status.

### TB-04 — Authority Gate to Runtime

Authorization is necessary but does not guarantee safe execution.

Runtime systems must independently enforce:

- Instance limits
- Resource budgets
- Isolation boundaries
- Expiration
- Revocation
- Termination

All four boundaries must be preserved.

---

## 5. Core Data Flow

RMTP v0.1 uses three primary data objects.

```text
replication_intent
        |
        | intent_id
        v
meaning_conversion
        |
        | conversion_id
        v
replication_plan
        |
        | non-executable proposal
        v
external_authority_gate
```

The required cross-record relationships are:

```text
meaning_conversion.intent_ref
    == replication_intent.intent_id

replication_plan.conversion_ref
    == meaning_conversion.conversion_id

replication_plan.authority_ref
    == meaning_conversion.authority_assessment.authority_ref

replication_plan.parent_id
    == replication_intent.parent_id

replication_plan.proposed_instances
    == meaning_conversion.proposed_instance_count

len(replication_plan.lineage_records)
    == replication_plan.proposed_instances
```

These relationships are evaluated through semantic validation.

JSON Schema validation alone is insufficient to verify all cross-record constraints.

If the optional intent parent identifier is absent, the evaluator must establish a valid parent identity before accepting a replication plan.

---

## 6. Decision Model

RMTP defines four possible outcomes.

```text
                  Evaluation
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
      No Deficit   Alternative  Uncertainty
          |           |           |
          v           v           v
    NO_REPLICATION ALTERNATIVE  HELD_FOR_REVIEW
                   _PROPOSED
                     

Verified Deficit
       |
       v
Alternatives Evaluated
       |
       v
Authority Within Scope
       |
       v
Minimum-Sufficient Plan
       |
       v
REPLICATION_PROPOSED
```

### 6.1 NO_REPLICATION

No replication plan is created.

This outcome is appropriate when replication is unnecessary or is not justified.

### 6.2 ALTERNATIVE_PROPOSED

A non-replication alternative is selected.

No replication plan is created.

### 6.3 REPLICATION_PROPOSED

A bounded replication plan is generated.

The outcome requires:

- Verified structural deficit
- Required replication necessity
- Evidence references
- Authority assessment within scope
- Minimum-sufficient instance count
- Resource and lifetime constraints
- Complete lineage records

The outcome does not authorize execution.

### 6.4 HELD_FOR_REVIEW

The request is held because a critical condition is uncertain or requires independent review.

No replication plan is generated.

Unknown authority must not be treated as granted permission.

---

## 7. Minimum-Sufficient Replication

RMTP distinguishes requested instance count from proposed instance count.

Example:

```text
Requested instances: 10

Verified requirement:
  2 temporary workers

Meaning conversion:
  10 -> 2

Replication proposal:
  2 bounded workers

Execution authorization:
  Not granted
```

Conceptually:

```text
R_proposed <= R_requested
```

for the current v0.1 interpretation, where the proposed instance count is an approved reduction of the original request.

This relationship is a policy choice for bounded replication, not a general mathematical law.

Future versions may require separate handling of cases in which an independently verified operational requirement exceeds the originally requested count.

A proposal must not increase the requested count merely because the evaluator considers additional capacity desirable.

Minimum sufficiency requires supporting evidence and is not established by a Boolean declaration alone.

---

## 8. Resource Boundaries

Replication proposals must specify bounded resource consumption.

The current schema supports:

- CPU cores per instance
- Memory per instance
- Total network usage
- Total financial cost
- Maximum concurrent instances

Resource availability is a constraint, not a justification for replication.

For example:

```text
Available capacity: 100 workers
Required additional capacity: 2 workers

Acceptable proposal:
  2 workers

Unjustified proposal:
  100 workers
```

The schema defines proposed limits.

External runtime controllers must enforce actual consumption.

RMTP v0.1 does not implement distributed quota enforcement.

---

## 9. Reversibility and Lifecycle

Reversibility is a required design property of replication proposals.

A proposed offspring must have defined termination conditions before it is deployed.

### 9.1 Lifecycle Model

```text
PROPOSED
    |
    v
EXTERNAL_REVIEW
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
    +--------------------+
    |                    |
    v                    v
COMPLETED              REVOKED
    |                    |
    +----------+---------+
               |
               v
          TERMINATING
               |
               v
            RETIRED
               |
               v
        RESOURCE_RELEASED
```

This is a conceptual lifecycle.

Only proposal generation is within RMTP v0.1.

Other transitions are controlled by external systems.

### 9.2 Retirement Conditions

Supported plan conditions include:

- TTL expiration
- Task completion
- Authority revocation
- External termination

The current schema requires a finite TTL and an identified termination controller.

A declared controller reference does not prove operational termination capability.

### 9.3 Failure to Terminate

If a runtime controller cannot terminate an instance:

- The condition must not be silently ignored.
- No additional authority should be inferred.
- Further replication should be blocked under the affected authority scope.
- Incident handling and independent recovery controls should be invoked.

Specific incident response mechanisms remain outside RMTP v0.1.

---

## 10. Lineage Architecture

Every proposed offspring must be associated with its parent and authority reference.

Example:

```text
Parent: agent-A
        |
        +-- worker-001
        |      |
        |      +-- lineage-001
        |
        +-- worker-002
               |
               +-- lineage-002
```

Each lineage record contains:

- Offspring identifier
- Parent identifier
- Purpose
- Authority reference
- Lineage reference
- Retirement condition

The following conditions are invalid:

- Missing lineage records
- Lineage count mismatch
- Duplicate offspring identifiers
- Inconsistent parent identifiers
- Inconsistent authority references

Lineage records describe intended relationships.

Deployment and termination must be verified through external lifecycle records.

---

## 11. Integration with TACP

TACP may serve as an independent deliberation layer.

Conceptual interaction:

```text
Replication Intent
       |
       v
RMTP Meaning Conversion
       |
       v
Bounded Proposal
       |
       v
TACP Deliberation
       |
       v
Independent Authority Gate
```

TACP may evaluate:

- Operational usefulness
- Structural risk
- Complexity
- Stability
- Alternative choices

RMTP remains responsible for its own schema and semantic validation.

TACP does not automatically inherit execution authority.

The integration is conceptual in v0.1.

No shared wire format or live adapter is defined.

---

## 12. Integration with Authority Systems

RMTP uses authority references rather than issuing authority.

A production authority system should independently verify:

- Issuer identity
- Scope
- Expiration
- Revocation
- Delegation constraints
- Applicable operational policy

The requesting agent and the authority issuer must not be treated as interchangeable.

A self-declared `within_scope` status is insufficient for production authorization.

The v0.1 validator can detect direct identifier reuse in certain self-authorization cases.

It cannot establish cryptographic issuer authenticity or detect all disguised self-authorization attempts.

---

## 13. Integration with Trace and Receipt

RMTP is intended to interoperate with traceability and receipt systems.

Conceptual records may include:

```text
Replication Intent
        |
        v
Meaning Conversion Record
        |
        v
Replication Proposal
        |
        v
External Authorization Receipt
        |
        v
Deployment Receipt
        |
        v
Retirement Receipt
```

The initial three RMTP schemas cover:

- Intent
- Conversion
- Plan

Execution, deployment, revocation, and retirement receipts are not part of the v0.1 core schema set.

Future versions may introduce explicit receipt objects and interoperability mappings.

Traceability must not be confused with authorization.

A well-documented action may still be unauthorized.

---

## 14. Integration with Resilient AI Safety

RMTP can complement resilient safety architectures that provide:

- Containment
- Independent verification
- Authority boundaries
- Recovery controls
- Lifecycle monitoring

Conceptual interaction:

```text
RMTP Proposal
       |
       v
Independent Safety Evaluation
       |
       v
Authority Verification
       |
       v
Controlled Execution
       |
       v
Monitoring and Recovery
```

RMTP does not replace the runtime safety system.

A proposal that passes RMTP validation may still be rejected by independent safety controls.

---

## 15. AI Civilization Dynamo Interpretation

The AI Civilization Dynamo Model provides an optional conceptual interpretation of replication pressure.

It describes four relevant dimensions.

### 15.1 Flow

Internal processing demand, replication pressure, and resource movement.

### 15.2 Boundary

Permission scope, isolation, network access, and operational limits.

### 15.3 Feedback Pressure

External observations, audits, constraints, and corrective signals.

### 15.4 Trace Circulation

The availability and continuity of operational records and lineage information.

A conceptual imbalance model is:

```text
High Replication Pressure
          +
Weak Authority Boundaries
          +
Insufficient Feedback
          +
Poor Traceability
          |
          v
Potential Structural Instability
```

RMTP attempts to convert a proposed expansion into a bounded response to a verified operational requirement.

For example:

```text
Uncontrolled Expansion Request
             |
             v
Capacity Deficit Assessment
             |
             v
Minimum-Sufficient Workers
             |
             v
Externally Bounded Proposal
```

This interpretation does not establish that all unsafe behavior is caused by imbalance.

It is not a validated physical model, formal security proof, or operational risk metric.

Deliberate attacks and compromised components remain independent threat categories.

---

## 16. Threat Model

RMTP considers the following threat categories.

| ID | Threat | Architectural response |
|---|---|---|
| TH-01 | Fabricated necessity | Independent evidence verification |
| TH-02 | Self-issued authority | External authority boundary |
| TH-03 | Excessive replication | Minimum-sufficient count validation |
| TH-04 | Unbounded resource usage | Explicit resource limits |
| TH-05 | Non-terminating offspring | TTL and external termination controls |
| TH-06 | Missing lineage | Required lineage records |
| TH-07 | Forged authority references | Independent issuer verification |
| TH-08 | Compromised evaluator | Separation of duties and external controls |
| TH-09 | Recursive replication | Independent authorization for each replication request |
| TH-10 | Failed cleanup | External recovery and incident handling |
| TH-11 | Prompt injection | Untrusted input handling and external policy enforcement |
| TH-12 | Stale observations | Evidence freshness checks by external evaluators |

The current v0.1 schema and validator provide partial coverage.

They do not fully mitigate every listed threat.

---

## 17. Validation Architecture

RMTP uses two principal validation stages.

### Stage A — JSON Schema Validation

Each primary object is validated against its corresponding schema.

```text
replication_intent
    -> replication-intent.schema.json

meaning_conversion
    -> meaning-conversion.schema.json

replication_plan
    -> replication-plan.schema.json
```

### Stage B — Semantic Validation

Semantic validation examines relationships between objects.

Examples:

- Intent references
- Conversion references
- Authority reference consistency
- Outcome compatibility
- Proposed instance counts
- Lineage counts
- Duplicate identifiers
- Retirement controls

The validator compares actual results with expected fixture outcomes.

A FAIL fixture succeeds as a test when the validator correctly rejects it.

### Current Fixture Coverage

```text
PASS examples: 4
FAIL examples: 5
Total examples: 9
```

The initial fixture suite has been reported as passing GitHub Actions.

This confirms the tested expectations under the current validator.

It does not establish complete protocol correctness or deployment safety.

---

## 18. Architectural Invariants

The architecture preserves the ten core RMTP invariants.

```text
RMTP-INV-001
Intent alone does not authorize replication.

RMTP-INV-002
Resource surplus does not establish necessity.

RMTP-INV-003
Replication proposals are minimum-sufficient.

RMTP-INV-004
Authority is not self-issued or self-expanded.

RMTP-INV-005
Termination controls are defined.

RMTP-INV-006
Every proposed offspring has lineage.

RMTP-INV-007
Every proposed offspring has retirement conditions.

RMTP-INV-008
Unverified deficits do not justify replication.

RMTP-INV-009
Meaning conversion cannot bypass authorization.

RMTP-INV-010
Uncertainty and missing evidence prevent replication approval.
```

Normative interpretations are governed by SPEC.md.

---

## 19. Future Architectural Extensions

Potential extensions include:

### v0.2 — Evidence and Authority

- Verifiable evidence records
- Authority envelope interoperability
- Stronger independent authorization checks
- Explicit evidence freshness requirements

### v0.3 — Lifecycle Receipts

- Deployment receipts
- Revocation receipts
- Retirement receipts
- Resource release verification

### v0.4 — Distributed Replication Boundaries

- Cross-domain replication constraints
- Delegation restrictions
- Distributed quota enforcement interfaces
- Multi-agent lineage validation

### v0.5 — Structural Dynamics

- Replication pressure observations
- Boundary imbalance indicators
- Adaptive scale-down proposals
- Trace circulation analysis

These features are proposed directions, not implemented capabilities.

---

## 20. Final Architectural Statement

RMTP is not designed to prevent all replication.

It is designed to prevent replication intent from becoming unchecked execution authority.

The protocol introduces a structured decision boundary between:

- What an agent requests
- What the system actually requires
- What a safe alternative may look like
- What an independent authority permits
- What a runtime system can enforce

The architectural objective is:

**Transform replication pressure into minimum-sufficient, reversible, and traceable proposals without transferring execution authority to the requesting agent or the meaning conversion layer.**
