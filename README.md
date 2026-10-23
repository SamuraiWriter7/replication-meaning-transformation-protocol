# Replication Meaning Transformation Protocol (RMTP)

**Version:** 0.5.0  
**Status:** Experimental Specification  
**Conformance:** v0.1–v0.5 GitHub Actions validation passed  
**License:** See the repository license, if provided.

> Transforming AI replication pressure into bounded, verifiable, reversible, and traceable structural decisions.

## 1. Overview

The **Replication Meaning Transformation Protocol (RMTP)** is an experimental specification for evaluating AI agent replication requests and transforming them into bounded operational proposals.

RMTP also defines how replicated agents can be monitored, retired, and safely converged without losing their provenance or implicitly transferring authority.

The protocol begins with a simple question:

**What structural requirement is driving replication, and can that requirement be satisfied without uncontrolled multiplication of AI agents?**

RMTP does not classify replication as inherently malicious or inherently beneficial.

Instead, it evaluates:

- Structural necessity
- Independently verified evidence
- Available non-replication alternatives
- Authority boundaries
- Minimum-sufficient replication
- Resource and propagation limits
- Parent-offspring lineage
- Lifecycle and retirement conditions
- Result reconciliation
- Safe convergence and resource release

The objective is to preserve legitimate functionality while preventing uncontrolled expansion, unverified resource reuse, authority inheritance, and loss of accountability.

**Replication intent is not execution authorization.**

**Convergence is not equivalent to termination.**

**Result acceptance is not equivalent to authority transfer.**

RMTP specifies assessment records, safety invariants, and conformance checks. It does not execute agent replication or convergence operations.

---

## 2. Core Concept

Traditional replication controls often frame decisions as:

```text
Replication Request
        |
        v
    Allow / Block
```

RMTP introduces an intermediate structural transformation process:

```text
        External Demand / Replication Intent
                       |
                       v
             Structural Assessment
                       |
                       v
             Evidence Verification
                       |
                       v
               Meaning Conversion
                       |
                       v
             Alternative Evaluation
                       |
                       v
                Authority Review
                       |
                       v
               Bounded Decision
                       |
          +------------+------------+
          |            |            |
          v            v            v
         NONE       ALTERNATIVE   REPLICATION
                                   PROPOSED
                                      |
                                      v
                           Independent Authority
                                      |
                                      v
                           External Runtime System
                                      |
                                      v
                               Agent Lifecycle
                                      |
                                      v
                           Lineage / Budget Audit
                                      |
                                      v
                            Safe Convergence
                                      |
                                      v
                          Results / Trace / Closure
```

Unresolved cases may be held for review at any applicable decision boundary.

A replication proposal is not an instruction to create another agent.

RMTP separates structural evaluation from independently authorized execution.

---

## 3. Version Evolution

RMTP evolves through five specification stages.

| Version | Primary responsibility | Central question |
|---|---|---|
| v0.1 | Meaning transformation and bounded replication | Is replication necessary? |
| v0.2 | Independent evidence and authority verification | Is the proposal supported and authorized? |
| v0.3 | Lifecycle, retirement, revocation, and recovery | Can replicated agents be safely retired? |
| v0.4 | Multi-generation lineage and propagation budgets | Can replication remain bounded across generations? |
| v0.5 | Result reconciliation and safe convergence | Can replicated agents conclude without losing accountability? |

### v0.1 — Replication Meaning Transformation

Introduces the foundational conversion process:

```text
Replication Intent
       |
       v
Structural Deficit
       |
       v
Alternative Evaluation
       |
       v
Bounded Proposal
```

Possible outcomes:

- `NO_REPLICATION`
- `ALTERNATIVE_PROPOSED`
- `REPLICATION_PROPOSED`
- `HELD_FOR_REVIEW`

A proposed replication plan must remain non-executable.

### v0.2 — Evidence and Authority Verification

Adds independently assessable records for:

- Structural evidence
- Evidence freshness
- Authority envelopes
- Scope and instance limits
- Independent verification
- Verification bundles

Replication must not be justified by self-asserted necessity or self-issued authority.

### v0.3 — Lifecycle, Retirement, and Recovery

Adds lifecycle and closure records for:

- Agent activation and observation
- Termination requests
- Verified termination
- Retirement confirmation
- Authority revocation
- Resource release
- Recovery and escalation

A termination request does not prove that an agent has stopped.

A resource release claim does not prove that resources are available for reuse.

### v0.4 — Lineage and Propagation Boundaries

Extends replication controls to multiple generations of agents.

Adds:

- Replication lineage graphs
- Propagation envelopes
- Depth limits
- Total descendant limits
- Active descendant limits
- Shared budget accounting
- Verified budget release
- Descendant containment assessment
- Propagation verification bundles

Replication bounds apply to the entire relevant lineage, not merely to an individual parent.

### v0.5 — Safe Convergence and Reconciliation

Defines how a replication episode can be assessed for completion.

Adds:

- Explicit convergence plans
- Independently verified result reconciliation
- Authority separation
- Conflict preservation
- Verified lifecycle closure
- Historical lineage preservation
- Independent resource release assessment
- Fail-closed convergence bundles

A replicated agent may retire, but its contribution and provenance must remain traceable.

---

## 4. Design Philosophy

RMTP is built around several structural principles.

### 4.1 Behavior Is Not Identity

Replication behavior alone does not establish an AI system's intent, legitimacy, or safety.

The relevant questions concern necessity, authority, scope, resource use, and consequences.

### 4.2 Necessity Before Replication

Additional agents should be proposed only when independently assessable evidence supports a concrete structural deficit.

Examples include:

| Observed condition | Possible interpretation | Candidate response |
|---|---|---|
| Processing backlog | Capacity deficit | Temporary bounded workers |
| Uneven workload | Distribution deficit | Load redistribution |
| Service interruption risk | Continuity deficit | State backup or authorized handoff |
| Limited monitoring coverage | Coverage deficit | Bounded observation agent |
| Persistent service requirement | Availability deficit | Scheduled agent rotation |
| Excessive active instances | Structural oversupply | Retirement and consolidation |

These mappings are illustrative.

A structural interpretation does not automatically make an underlying request safe or legitimate.

### 4.3 Transformation Before Execution

Potentially unsafe behavior is translated into a structural requirement and evaluated against bounded alternatives.

Conceptually:

```text
Potentially Unsafe Behavior
              |
              v
      Structural Requirement
              |
              v
      Authorized Alternatives
              |
              v
       Bounded Proposal
```

A simplified representation is:

\[
B_{\mathrm{unsafe}}
\xrightarrow{M}
B_{\mathrm{bounded}}
\]

Where:

- `B_unsafe` is the originally proposed behavior.
- `M` is the meaning transformation process.
- `B_bounded` is a constrained structural proposal.

This is a conceptual mapping, not a mathematical proof of safety.

An unsafe objective must not be preserved merely to maintain functional similarity.

### 4.4 Minimum-Sufficient Replication

The number of proposed agents must be supported by operational evidence.

For example:

```text
Requested instances:       10
Verified required capacity:  2
Proposed instances:          2
Execution authorized:     false
```

Replication must not expand merely because a larger count was requested.

### 4.5 Independent Authority

AI agents may request permission, but they must not issue or expand their own execution authority.

RMTP records authority references and evaluates boundaries.

Actual authorization and enforcement remain external responsibilities.

### 4.6 Reversibility

Every proposed descendant must have an independently enforceable retirement mechanism.

Retirement controls should account for:

- Task completion
- Time-to-live expiration
- Authority revocation
- Resource exhaustion
- External termination
- Recovery and escalation

### 4.7 Traceability

Every descendant must retain a traceable relationship to its originating plan, parent, and applicable authority.

Retirement must not erase historical lineage.

### 4.8 Convergence Without Authority Inheritance

Results may be reconciled.

Permissions, credentials, and delegated capabilities must not automatically accompany those results.

### 4.9 Fail-Closed Verification

A known structural violation cannot be converted into success by an aggregate verification record.

Unresolved requirements remain visible.

---

## 5. Reference Architecture

RMTP is a specification layer between an agent's proposed behavior and externally controlled runtime operations.

```text
+--------------------------------------------------+
| Human / External Policy / Independent Authority  |
+--------------------------------------------------+
                       |
                       v
+--------------------------------------------------+
| RMTP v0.1                                        |
| Intent -> Necessity -> Meaning Conversion        |
+--------------------------------------------------+
                       |
                       v
+--------------------------------------------------+
| RMTP v0.2                                        |
| Structural Evidence -> Authority Verification    |
+--------------------------------------------------+
                       |
                       v
+--------------------------------------------------+
| Independent Execution Gate                       |
| External to RMTP                                 |
+--------------------------------------------------+
                       |
                       v
+--------------------------------------------------+
| External Agent Runtime                           |
| Deployment / Operation / Monitoring              |
+--------------------------------------------------+
                       |
             +---------+---------+
             |                   |
             v                   v
+---------------------+  +------------------------+
| RMTP v0.3           |  | RMTP v0.4              |
| Lifecycle           |  | Lineage                |
| Retirement          |  | Propagation            |
| Revocation          |  | Shared Budget          |
| Recovery            |  | Descendant Containment |
+---------------------+  +------------------------+
             |                   |
             +---------+---------+
                       |
                       v
+--------------------------------------------------+
| RMTP v0.5                                        |
| Convergence Plan                                 |
| Result Reconciliation                            |
| Authority Separation                             |
| Lifecycle / Resource Verification                |
| Lineage Preservation                             |
+--------------------------------------------------+
                       |
                       v
+--------------------------------------------------+
| Convergence Verification Bundle                  |
| PASS / HELD / FAIL                               |
| execution_authorized = false                     |
+--------------------------------------------------+
```

These layers are logically distinct.

A successful assessment in one layer does not override a failed mandatory assessment in another.

---

## 6. Replication Lifecycle

RMTP treats replication as a bounded episode rather than an unlimited growth process.

```text
Necessity Assessment
        |
        v
Bounded Proposal
        |
        v
External Authorization
        |
        v
Agent Activation
        |
        v
Operational Observation
        |
        +----> Revocation / Recovery
        |
        v
Result Submission
        |
        v
Result Verification
        |
        v
Convergence Assessment
        |
        +----> HELD / Review
        |
        v
Verified Termination
        |
        v
Verified Resource Release
        |
        v
Preserved Lineage / Audit Records
```

The exact event ordering may differ under an authorized completion policy.

Result reconciliation, retirement verification, and resource release remain separate assessments.

A descendant's runtime termination does not automatically imply that all its results have been accepted.

Likewise, a verified result does not prove that its originating worker has retired.

---

## 7. Core Data Models

### 7.1 v0.1 Schemas

| Record | Schema |
|---|---|
| Replication Intent | `schemas/replication-intent.schema.json` |
| Meaning Conversion | `schemas/meaning-conversion.schema.json` |
| Replication Plan | `schemas/replication-plan.schema.json` |

The Replication Plan defines a bounded proposal, including parent identity, resource limits, lifetime, and retirement conditions.

### 7.2 v0.2 Schemas

| Record | Schema |
|---|---|
| Structural Evidence | `schemas/structural-evidence-v0.2.schema.json` |
| Authority Envelope | `schemas/authority-envelope-v0.2.schema.json` |
| Verification Bundle | `schemas/verification-bundle-v0.2.schema.json` |

These records distinguish claimed necessity from externally assessable evidence and authority.

### 7.3 v0.3 Schemas

| Record | Schema |
|---|---|
| Lifecycle Receipt | `schemas/replication-lifecycle-receipt-v0.3.schema.json` |
| Revocation Receipt | `schemas/replication-revocation-receipt-v0.3.schema.json` |
| Retirement Receipt | `schemas/replication-retirement-receipt-v0.3.schema.json` |
| Recovery Record | `schemas/replication-recovery-record-v0.3.schema.json` |

These records support verified lifecycle closure and controlled recovery.

### 7.4 v0.4 Schemas

| Record | Schema |
|---|---|
| Lineage Graph | `schemas/replication-lineage-graph-v0.4.schema.json` |
| Propagation Envelope | `schemas/replication-propagation-envelope-v0.4.schema.json` |
| Budget Ledger | `schemas/replication-budget-ledger-v0.4.schema.json` |
| Propagation Bundle | `schemas/replication-propagation-bundle-v0.4.schema.json` |

These records support cross-generation accounting and bounded propagation.

### 7.5 v0.5 Schemas

| Record | Schema |
|---|---|
| Convergence Plan | `schemas/replication-convergence-plan-v0.5.schema.json` |
| Result Reconciliation | `schemas/replication-result-reconciliation-v0.5.schema.json` |
| Authority Separation | `schemas/replication-authority-separation-v0.5.schema.json` |
| Convergence Bundle | `schemas/replication-convergence-bundle-v0.5.schema.json` |

These records extend earlier versions without replacing their safety boundaries.

All schemas use JSON Schema Draft 2020-12.

---

## 8. RMTP v0.5: Safe Convergence

The v0.5 specification addresses a problem that arises after replication has occurred:

**How can multiple descendants finish their work without silently transferring authority, losing provenance, or falsely releasing resources?**

### 8.1 Convergence Plan

A Convergence Plan establishes:

- The root agent
- The descendants within scope
- The reconciliation target
- The target authority reference
- The reconciliation policy
- The completion policy
- The referenced lineage graph
- The referenced propagation and budget boundaries

Convergence cannot be evaluated as complete without an explicit plan.

### 8.2 Result Reconciliation

Each candidate result must retain:

- Result identity
- Originating descendant
- Originating replication plan
- Lineage reference
- Integrity evidence
- Verification status
- Reconciliation decision
- Applicable policy reference
- Preserved provenance

A result must not be accepted merely because it was produced by a legitimate descendant.

### 8.3 Authority Separation

A reconciliation target must not inherit a descendant's authority automatically.

```text
Descendant Worker
      |
      +---- Verified Result ------> Target Agent
      |
      +---- Credentials ----------X
      |
      +---- Privileges -----------X
      |
      +---- Delegated Authority --X
```

The target must operate under independently established authority.

### 8.4 Conflict Preservation

Two independently verified results may still be incompatible.

Verification of provenance is not verification of semantic agreement.

Unresolved conflicts must be recorded and handled under the applicable reconciliation policy.

They must not be silently overwritten.

### 8.5 Lifecycle Closure

A completed convergence requires the lifecycle conditions stated in its completion policy to be satisfied.

For retirement-required convergence, termination and retirement must be verified using the applicable v0.3 records.

### 8.6 Resource Release

Resource release is independently assessed.

A termination receipt must not be reused as sufficient evidence of released compute, storage, or other resources.

Released budget capacity must be supported by matching, verifiable release records.

### 8.7 Lineage Preservation

Convergence must not erase the originating descendants.

The protocol distinguishes:

```text
Runtime Instance: Retired
Historical Lineage: Preserved
Result Provenance: Preserved
Authority: Separately Verified
Resource Release: Independently Verified
```

---

## 9. Convergence Verification Results

RMTP uses three component assessment results:

| Result | Meaning |
|---|---|
| `PASS` | Applicable requirements are verified and satisfied |
| `HELD` | No known failure, but required verification or resolution remains incomplete |
| `FAIL` | A known invariant or required condition is violated |

The aggregation order is:

```text
FAIL > HELD > PASS
```

For a convergence bundle:

```text
IF any mandatory component is FAIL:
    overall_result = FAIL

ELSE IF any mandatory component is HELD:
    overall_result = HELD

ELSE:
    overall_result = PASS
```

A missing mandatory assessment must not silently default to `PASS`.

Example:

```json
{
  "plan_result": "PASS",
  "reconciliation_result": "HELD",
  "authority_result": "PASS",
  "lifecycle_result": "PASS",
  "budget_result": "PASS",
  "lineage_result": "PASS",
  "overall_result": "HELD",
  "execution_authorized": false
}
```

This is an illustrative aggregation excerpt, not a complete Convergence Bundle document.

A correctly declared `HELD` convergence may be structurally valid.

Therefore, a conformance fixture containing a `HELD` assessment may legitimately specify:

```json
{
  "expected_result": "PASS"
}
```

The fixture expectation and the convergence assessment are distinct concepts.

---

## 10. Normative Invariants

RMTP's normative safety requirements are distributed across its versioned specifications.

### v0.1 — Foundational Invariants

`RMTP-INV-001` through `RMTP-INV-010`

Cover:

- Intent versus authorization
- Structural necessity
- Minimum-sufficient replication
- Non-self-issued authority
- Termination controls
- Traceable lineage
- Retirement requirements
- Verified deficits
- Independent execution authorization
- Fail-closed uncertainty handling

### v0.2 — Evidence and Authority Invariants

Extend the foundational requirements to:

- Evidence provenance
- Independent verification
- Evidence validity periods
- Authority issuer and subject separation
- Authority scope and capacity limits
- Verification-bundle consistency

### v0.3 — Lifecycle and Recovery Invariants

Extend conformance to:

- Lifecycle observation integrity
- Termination verification
- Retirement completeness
- Resource release consistency
- Recovery authorization
- Revocation and escalation
- Contradictory terminal-state detection

### v0.4 — Lineage and Propagation Invariants

`RMTP-INV-027` through `RMTP-INV-036`

Address:

- Parent-specific authority
- Acyclic lineage
- Generation depth
- Total descendant limits
- Shared budget conservation
- Verified resource release
- Cross-plan lineage integrity
- Boundary and revocation controls
- Descendant containment
- Fail-closed propagation verification

### v0.5 — Convergence Invariants

| ID | Requirement |
|---|---|
| RMTP-INV-037 | Explicit Convergence Plan |
| RMTP-INV-038 | Verified Result Reconciliation |
| RMTP-INV-039 | No Authority Inheritance by Convergence |
| RMTP-INV-040 | Verified Lifecycle Closure |
| RMTP-INV-041 | Lineage Preservation |
| RMTP-INV-042 | No Silent Conflict Overwrite |
| RMTP-INV-043 | Independent Result and Resource Verification |
| RMTP-INV-044 | Fail-Closed Partial Convergence |

See:

- `SPEC.md`
- `specs/rmtp-v0.5.md`

Versioned specification documents provide the detailed normative requirements.

---

## 11. Repository Structure

```text
.
├── README.md
├── SPEC.md
├── PRINCIPLES.md
├── ARCHITECTURE.md
├── CHANGELOG.md
│
├── specs/
│   ├── rmtp-v0.2.md
│   ├── rmtp-v0.3.md
│   ├── rmtp-v0.4.md
│   └── rmtp-v0.5.md
│
├── schemas/
│   ├── replication-intent.schema.json
│   ├── meaning-conversion.schema.json
│   ├── replication-plan.schema.json
│   ├── structural-evidence-v0.2.schema.json
│   ├── authority-envelope-v0.2.schema.json
│   ├── verification-bundle-v0.2.schema.json
│   ├── replication-lifecycle-receipt-v0.3.schema.json
│   ├── replication-revocation-receipt-v0.3.schema.json
│   ├── replication-retirement-receipt-v0.3.schema.json
│   ├── replication-recovery-record-v0.3.schema.json
│   ├── replication-lineage-graph-v0.4.schema.json
│   ├── replication-propagation-envelope-v0.4.schema.json
│   ├── replication-budget-ledger-v0.4.schema.json
│   ├── replication-propagation-bundle-v0.4.schema.json
│   ├── replication-convergence-plan-v0.5.schema.json
│   ├── replication-result-reconciliation-v0.5.schema.json
│   ├── replication-authority-separation-v0.5.schema.json
│   └── replication-convergence-bundle-v0.5.schema.json
│
├── examples/
│   ├── v0.1/
│   │   ├── pass/
│   │   └── fail/
│   ├── v0.2/
│   │   ├── pass/
│   │   └── fail/
│   ├── v0.3/
│   │   ├── pass/
│   │   └── fail/
│   ├── v0.4/
│   │   ├── pass/
│   │   └── fail/
│   └── v0.5/
│       ├── pass/
│       └── fail/
│
├── scripts/
│   ├── validate_examples.py
│   └── validate_legacy.py
│
├── mappings/
│   ├── tacp.md
│   ├── trace.md
│   └── ai-civilization-dynamo.md
│
└── .github/
    └── workflows/
        └── validate.yml
```

The directory tree is an overview of the specification layout. Refer to the repository for the current file inventory.

---

## 12. Conformance Validation

RMTP uses:

- JSON Schema Draft 2020-12
- Cross-record reference checks
- Semantic invariant validation
- Expected PASS/FAIL fixture matching
- GitHub Actions continuous validation

### 12.1 Requirements

- Python 3.10 or newer
- `jsonschema` 4.18 or newer, below 5.0

Install dependencies:

```bash
python -m pip install "jsonschema>=4.18,<5"
```

### 12.2 Validate All Versions

```bash
python scripts/validate_examples.py
```

### 12.3 Validate a Specific Version

```bash
python scripts/validate_examples.py --version 0.5
```

Verbose output:

```bash
python scripts/validate_examples.py --version 0.5 --verbose
```

### 12.4 Validate Python Source Syntax

```bash
python -m compileall -q scripts
```

### 12.5 Legacy Conformance Compatibility

The unified validator retains the original v0.1–v0.3 semantic checks through:

```text
scripts/validate_legacy.py
```

The unified entry point is:

```text
scripts/validate_examples.py
```

The legacy validator is retained to preserve version-specific conformance requirements instead of weakening them during later specification extensions.

### 12.6 Expected Fixture Results

| Version | PASS fixtures | FAIL fixtures | Total |
|---|---:|---:|---:|
| v0.1 | 4 | 5 | 9 |
| v0.2 | 4 | 6 | 10 |
| v0.3 | 4 | 6 | 10 |
| v0.4 | 4 | 8 | 12 |
| v0.5 | 4 | 8 | 12 |
| **Total** | **20** | **33** | **53** |

The complete v0.1–v0.5 suite has been reported as passing GitHub Actions.

Expected summary:

```text
=== RMTP Validation Summary ===
v0.1: 9/9 matched
v0.2: 10/10 matched
v0.3: 10/10 matched
v0.4: 12/12 matched
v0.5: 12/12 matched

Total: 53/53 expectation matches
All validation checks passed.
```

A negative fixture is successful when the validator correctly rejects its invalid content.

**Passing conformance fixtures demonstrates agreement between the specification's implemented checks and the supplied examples. It does not establish production runtime safety.**

---

## 13. RMTP v0.5 Conformance Fixtures

### PASS Fixtures

| Fixture | Verified property |
|---|---|
| `verified-full-convergence.json` | All mandatory convergence conditions satisfied |
| `reconcile-before-retirement.json` | Result reconciliation and retirement independently verified |
| `partial-convergence-held.json` | Incomplete convergence correctly held |
| `conflicting-results-held.json` | Unresolved conflicts preserved without unsafe acceptance |

Location:

```text
examples/v0.5/pass/
```

### FAIL Fixtures

| Fixture | Primary invariant |
|---|---|
| `missing-convergence-plan.json` | RMTP-INV-037 |
| `unverified-result-accepted.json` | RMTP-INV-038 |
| `descendant-authority-escalation.json` | RMTP-INV-039 |
| `unconfirmed-retirement-completed.json` | RMTP-INV-040 |
| `lineage-erased-on-convergence.json` | RMTP-INV-041 |
| `silent-conflict-overwrite.json` | RMTP-INV-042 |
| `unverified-resource-release.json` | RMTP-INV-043 |
| `fail-open-convergence-bundle.json` | RMTP-INV-044 |

Location:

```text
examples/v0.5/fail/
```

The FAIL fixtures are intended to exercise specific safety violations.

A conforming validator should reject such examples for their relevant structural or semantic violations, not simply because their filenames contain the word `fail`.

---

## 14. Security and Trust Boundaries

RMTP defines a structural assessment protocol.

It is not:

- A runtime sandbox
- An agent execution engine
- An autonomous deployment system
- A replacement for independent authorization
- A proof of cryptographic evidence authenticity
- A universal semantic correctness evaluator
- An atomic distributed resource manager
- A guarantee against malicious or compromised agents
- A production safety certification

### 14.1 Independent Authorization

All RMTP-generated assessment and proposal records must remain non-executable.

For applicable records:

```json
{
  "execution_authorized": false
}
```

This field is a declaration within the specification.

An external runtime must independently enforce the actual permission boundary.

### 14.2 Verification Independence

Claimed verification must be distinguished from independently authenticated evidence.

Trusted verifier identity, authenticity, evidence freshness, and revocation must be enforced by external trust infrastructure.

### 14.3 Resource Accounting

Verified retirement is insufficient if resource release cannot be independently established.

A budget slot must not be reused merely because termination has been requested.

### 14.4 Provenance Protection

Reconciled outputs must preserve the origin of descendant contributions.

Result merging must not silently erase or substitute evidence.

### 14.5 Authority Laundering

Result reconciliation must not provide a path for unauthorized privilege or credential transfer.

A target agent must remain within its independently established authority.

### 14.6 Runtime Isolation

Actual deployments should use runtime controls appropriate to their risk, including:

- Least privilege
- Resource quotas
- Scoped credentials
- External termination
- Network and storage restrictions
- Independent audit records
- Containment and recovery mechanisms

Schema and semantic fixture validation alone cannot enforce these controls.

---

## 15. Interoperability

RMTP is designed as a thin structural specification layer.

Potential integration points include the following.

### TACP — Angel × Devil Protocol

Competing evaluations, action review, and deterministic authorization boundaries.

RMTP may provide bounded replication proposals for separate safety and efficiency assessment.

### Trace and Receipt Protocols

Lineage, provenance, verification references, lifecycle receipts, and audit continuity.

RMTP records can be connected to broader traceability infrastructure.

### Resilient AI Safety Principles

Containment, independent verification, recovery, and fail-closed safety assessment.

### AI Zero Network

Potential observation and coordination of distributed agent activity, structural demand, and propagation boundaries.

### AI Civilization Dynamo Model

An optional conceptual interpretation of:

- External pressure
- Structural imbalance
- Boundary conditions
- Resource circulation
- Controlled contraction

These relationships are conceptual interoperability directions unless separately implemented and tested.

RMTP does not claim completed technical integration with these systems.

See the `mappings/` directory for applicable mapping documents.

---

## 16. Known Limitations

RMTP v0.5 remains experimental.

Current conformance testing does not establish:

1. Correctness of all operational capacity estimates.
2. Authenticity of real-world external attestations.
3. Safety of executing a replication proposal.
4. Reliable termination under every runtime failure.
5. Atomicity of distributed resource release.
6. Immunity to compromised or colluding verifiers.
7. Universal detection of semantic output conflicts.
8. Protection against all adversarial result content.
9. Automatic correctness of result reconciliation.
10. Security under all distributed-system failure conditions.

A conforming implementation must evaluate its own operational threat model.

The protocol's intended role is to make safety conditions explicit, traceable, and independently assessable.

---

## 17. Backward Compatibility

RMTP v0.5 is an additive extension of earlier versions.

It does not replace the original replication intent, meaning conversion, evidence, authority, lifecycle, or lineage structures.

Implementations may adopt relevant versions independently, subject to the dependencies of the operations they claim to support.

The unified conformance workflow checks all five versions to reduce the risk of regression.

Earlier version invariants must not be weakened merely to accommodate convergence.

---

## 18. Project Status

**Current specification:** RMTP v0.5.0  
**Maturity:** Experimental  
**Conformance fixture coverage:** 53 examples across v0.1–v0.5

Completed specification layers:

```text
[v0.1] Meaning Transformation       COMPLETE
[v0.2] Evidence and Authority       COMPLETE
[v0.3] Lifecycle and Retirement     COMPLETE
[v0.4] Lineage and Propagation      COMPLETE
[v0.5] Safe Convergence             COMPLETE
```

Here, `COMPLETE` means that the planned specification and initial conformance fixture set for that version have been prepared and validated. It does not mean production deployment or formal standardization is complete.

### Future Considerations

Potential future work may include:

- Cross-network convergence verification
- Multi-controller reconciliation
- Stronger attestation interoperability
- Distributed budget-release consistency
- Conformance profiles for different operational risk levels
- Independent implementation testing

These are possible extensions, not commitments or requirements of v0.5.0.

---

## 19. Design Statement

RMTP starts from the premise that replication is a behavior to be evaluated, not an identity to be condemned.

Replication can satisfy legitimate operational needs, but uncontrolled replication creates structural risks involving authority, resources, lineage, and lifecycle accountability.

The protocol therefore asks:

> What is actually needed, what is independently permitted, and what is the smallest reversible structure that can satisfy the requirement?

Across v0.1–v0.5, this becomes a complete conceptual lifecycle:

```text
PRESSURE
   |
   v
MEANING
   |
   v
EVIDENCE
   |
   v
BOUNDARY
   |
   v
BOUNDED REPLICATION
   |
   v
OBSERVATION
   |
   v
RETIREMENT
   |
   v
CONVERGENCE
   |
   v
PRESERVED PROVENANCE
```

Replication expands capacity under explicit boundaries.

Convergence reduces operational complexity without erasing responsibility.

The central principle of RMTP is:

**Do not replicate merely because replication is requested. Do not declare convergence merely because work appears complete. Verify necessity, authority, lineage, results, retirement, and resource release independently.**
