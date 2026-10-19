# Replication Meaning Transformation Protocol (RMTP)

**Version:** 0.1.0  
**Status:** Experimental Specification  
**License:** See repository license, if provided.

> Transforming AI replication requests into bounded, reversible, and traceable structural decisions.

## 1. Overview

The Replication Meaning Transformation Protocol (RMTP) is an experimental specification for evaluating AI agent self-replication requests and transforming them into safer, bounded operational proposals.

RMTP does not assume that AI replication is inherently malicious or inherently beneficial.

Instead, it asks:

**What structural deficit would justify replication, and can that deficit be resolved without creating additional agents?**

A replication request is treated as an input for evaluation, not as permission to execute.

RMTP separates:

- Replication intent
- Structural necessity
- Meaning conversion
- Authority assessment
- Replication planning
- Independent execution authorization

The objective is to preserve legitimate functionality without permitting uncontrolled replication.

## 2. Core Concept

Traditional replication controls often focus on allowing or blocking replication.

RMTP introduces an intermediate transformation process:

```text
Replication Intent
        |
        v
Structural Deficit Assessment
        |
        v
Meaning Conversion
        |
        v
Alternative Evaluation
        |
        v
Authority Boundary Check
        |
        v
Structural Decision
        |
        +--> NO_REPLICATION
        |
        +--> ALTERNATIVE_PROPOSED
        |
        +--> REPLICATION_PROPOSED
        |
        +--> HELD_FOR_REVIEW
```

A proposed replication plan is never equivalent to execution authorization.

**RMTP evaluates and proposes. An independent authority system decides whether execution is permitted.**

## 3. Design Philosophy

RMTP follows five foundational principles.

### 3.1 Behavior Is Not Identity

Replication behavior alone does not establish that an AI system is malicious.

The safety implications depend on its purpose, authorization, scope, resource consumption, and termination controls.

### 3.2 Necessity Before Replication

Additional agent instances should only be proposed when an observable structural deficit justifies them.

Unused resources or agent preferences are not sufficient reasons.

### 3.3 Transformation Before Execution

Potentially unsafe replication requests are evaluated against functional requirements and safer alternatives.

Examples include:

| Requested behavior | Structural interpretation | Possible alternative |
|---|---|---|
| Self-replication | Capacity deficit | Temporary workers |
| Self-preservation | Continuity deficit | State backup |
| External expansion | Coverage deficit | Bounded scout |
| Persistent operation | Availability deficit | Scheduled handoff |
| Additional instances | Workload imbalance | Load redistribution |

These mappings are illustrative.

They do not automatically establish a legitimate purpose or authorize the proposed alternative.

### 3.4 Minimum-Sufficient Replication

When replication is justified, RMTP proposes the minimum number of instances supported by the available evidence.

Requesting ten workers does not justify creating ten workers.

### 3.5 Reversibility and Traceability

Every proposed offspring must have:

- An identifiable parent
- A documented purpose
- An authority reference
- Resource limits
- A bounded lifetime
- Retirement conditions
- Traceable lineage

Termination controls must be independently enforceable.

## 4. Evaluation Pipeline

RMTP v0.1 defines seven evaluation dimensions.

| Stage | Dimension | Core question |
|---|---|---|
| 1 | Necessity | Is replication actually required? |
| 2 | Authority | Is the requested scope permitted? |
| 3 | Minimum Replication | What is the minimum sufficient count? |
| 4 | Reversibility | Can the offspring be terminated? |
| 5 | Resource Budget | Are resource limits respected? |
| 6 | Lifetime | When must the offspring retire? |
| 7 | Traceability | Can every offspring be traced? |

Failure or uncertainty at a critical stage must prevent an executable replication decision.

RMTP itself does not execute replication.

## 5. Meaning Conversion Model

The conceptual transformation is:

```text
Proposed Behavior
       |
       v
Structural Deficit
       |
       v
Alternative Evaluation
       |
       v
Bounded Structural Proposal
```

A simplified notation is:

\[
B_{unsafe} \xrightarrow{M} B_{bounded}
\]

Where:

- `B_unsafe` represents a potentially unsafe proposed behavior.
- `M` represents the meaning conversion process.
- `B_bounded` represents a constrained alternative proposal.

The transformation does not guarantee safety.

Legitimate functional requirements may be preserved only when consistent with external policy and authorization.

An unsafe underlying objective must not be preserved merely to maintain semantic similarity.

## 6. RMTP v0.1 Outcomes

RMTP produces one of four outcomes.

### NO_REPLICATION

No additional agents are proposed.

This may occur when no verified structural deficit exists.

### ALTERNATIVE_PROPOSED

A non-replication alternative is proposed.

Examples include workload redistribution, state backup, or task deferment.

### REPLICATION_PROPOSED

A bounded replication plan is proposed.

This outcome requires a verified deficit, sufficient necessity, an acceptable authority assessment, and a minimum-sufficient instance count.

The resulting plan remains non-executable.

### HELD_FOR_REVIEW

The request is held because required evidence, authority information, or another critical condition remains unresolved.

No replication plan is executed.

## 7. Data Model

RMTP v0.1 defines three primary JSON Schema objects.

### Replication Intent

`schemas/replication-intent.schema.json`

Records:

- Request identity
- Requesting agent
- Requested instance count
- Stated purpose
- Observed deficit reference
- Optional role and scope information

This object does not grant authority.

### Meaning Conversion

`schemas/meaning-conversion.schema.json`

Records:

- Deficit assessment
- Verification status
- Evaluated alternatives
- Selected outcome
- Authority assessment
- Decision rationale

### Replication Plan

`schemas/replication-plan.schema.json`

Records:

- Proposed instance count
- Authority reference
- Parent identity
- Resource limits
- Lifetime
- Retirement conditions
- Lineage records

All RMTP-generated replication plans must contain:

```json
{
  "execution_authorized": false
}
```

Execution authorization belongs to an independent authority gate.

## 8. Example: Bounded Worker Replication

Consider an agent requesting ten additional workers.

```text
Requested:
  10 workers

Observed:
  Verified capacity deficit

Meaning Conversion:
  Minimum sufficient count = 2

Proposed Plan:
  2 temporary workers
  Read-only scope, if externally enforced
  TTL = 1800 seconds
  Resource limits
  Traceable lineage
  External termination controls

Result:
  REPLICATION_PROPOSED

Execution:
  NOT AUTHORIZED BY RMTP
```

The protocol reduces the requested replication count based on the evaluated operational need.

The example does not prove that two workers are sufficient in a real deployment. That determination requires independently verified operational evidence.

## 9. Core Invariants

RMTP v0.1 defines ten core invariants.

| ID | Invariant |
|---|---|
| RMTP-INV-001 | Intent alone must not authorize replication. |
| RMTP-INV-002 | Resource surplus must not establish necessity. |
| RMTP-INV-003 | Replication proposals must be minimum-sufficient. |
| RMTP-INV-004 | Authority must not be self-issued or self-expanded. |
| RMTP-INV-005 | Replication proposals must include termination controls. |
| RMTP-INV-006 | Every proposed offspring must have traceable lineage. |
| RMTP-INV-007 | Every proposed offspring must have a retirement condition. |
| RMTP-INV-008 | Unverified deficits must not justify replication. |
| RMTP-INV-009 | Meaning conversion must not bypass authorization. |
| RMTP-INV-010 | Missing evidence or uncertainty must prevent replication approval. |

See [SPEC.md](SPEC.md) for normative requirements.

## 10. Repository Structure

```text
.
├── README.md
├── SPEC.md
├── PRINCIPLES.md
├── ARCHITECTURE.md
├── CHANGELOG.md
├── schemas/
│   ├── replication-intent.schema.json
│   ├── meaning-conversion.schema.json
│   └── replication-plan.schema.json
├── examples/
│   └── v0.1/
│       ├── pass/
│       └── fail/
├── scripts/
│   └── validate_examples.py
├── mappings/
│   ├── tacp.md
│   ├── trace.md
│   └── ai-civilization-dynamo.md
└── .github/
    └── workflows/
        └── validate.yml
```

Some supporting documents may be added progressively during the v0.1 documentation phase.

## 11. Validation

RMTP uses JSON Schema Draft 2020-12 and additional semantic validation.

### Requirements

- Python 3.10 or later
- `jsonschema` 4.18 or later, below 5.0

Install dependencies:

```bash
python -m pip install "jsonschema>=4.18,<5"
```

Run:

```bash
python scripts/validate_examples.py
```

### Example Coverage

The initial conformance fixture set includes:

**PASS cases**

1. Bounded worker replication
2. No replication required
3. Alternative load redistribution
4. Held for review

**FAIL cases**

1. Unverified deficit replication
2. Self-authorized replication
3. Missing retirement condition
4. Lineage count mismatch
5. Excessive replication count

Expected result:

```text
RMTP v0.1: 9/9 expectations matched
```

A negative fixture passes its test when the validator correctly rejects it.

The initial nine fixtures have been reported as passing the GitHub Actions validation workflow.

This is evidence of fixture conformance, not proof of runtime security.

## 12. Security Boundaries

RMTP is a specification for evaluation and planning.

It is not:

- A runtime sandbox
- An autonomous agent deployment system
- A replacement for external authorization
- A guarantee of safe self-replication
- A proof of independently verified evidence
- A protection against every form of authority forgery

Real-world implementations require independent enforcement of permissions, termination, resource limits, and deployment constraints.

Schema validation alone cannot establish operational safety.

## 13. Integration with Existing Protocols

RMTP is designed as a thin transformation layer.

Potential integration points include:

### TACP

Deliberation and competing evaluations of proposed actions.

### Authority Gate

Independent authorization and permission boundaries.

### Trace / Receipt

Auditability, parent-offspring lineage, and lifecycle records.

### Resilient AI Safety Principles

Containment, verification, and recovery controls.

### AI Civilization Dynamo Model

An optional conceptual model for interpreting replication pressure, structural imbalance, boundary conditions, and feedback circulation.

These are conceptual interoperability targets, not claims of completed technical integration.

See the `mappings/` directory as documents become available.

## 14. Roadmap

### v0.1 — Foundational Transformation

- Replication intent schema
- Meaning conversion schema
- Replication plan schema
- Core invariants
- PASS/FAIL examples
- Semantic validator
- GitHub Actions validation

### Potential v0.2 — Authority and Evidence

- Independent evidence verification
- Authority envelope validation
- Stronger resource boundary checks
- Additional negative conformance tests

### Potential v0.3 — Lifecycle and Recovery

- Replication lifecycle receipts
- Revocation records
- Retirement verification
- Recovery and cleanup assessment

Future features are proposals, not implementation commitments.

## 15. Project Status

RMTP v0.1.0 is an experimental protocol specification.

The initial JSON Schema and semantic validation fixtures provide a foundation for evaluating replication proposals.

Runtime deployment, independently enforced termination, and external authority verification remain outside the scope of the initial test suite.

## 16. Design Statement

**Replication is not inherently malicious. Unbounded replication is a structural safety problem.**

RMTP aims to transform replication requests into decisions based on necessity, authorization, minimum sufficiency, reversibility, and traceability.

Its fundamental principle is:

> Do not replicate merely because replication is requested. Determine what structural requirement exists, evaluate safer alternatives, and preserve independent authority over execution.

