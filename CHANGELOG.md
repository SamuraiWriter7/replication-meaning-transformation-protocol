
# Changelog

All notable changes to the **Replication Meaning Transformation Protocol (RMTP)** are documented in this file.

This project follows the principles of [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and Semantic Versioning where applicable.

RMTP is an experimental specification. Version numbers indicate specification evolution and conformance scope, not production deployment or formal standardization.

---

## [Unreleased]

### Future Considerations

Potential research and specification extensions include:

- Cross-network convergence verification.
- Multi-controller reconciliation.
- Interoperable external attestations.
- Distributed resource-release consistency.
- Stronger verifier-independence requirements.
- Conformance profiles for different operational risk levels.
- Independent implementation testing.

These are possible extensions and are not requirements of RMTP v0.5.0.

---

## [0.5.0] - Unreleased

### Replication Convergence & Safe Reconciliation

RMTP v0.5 introduces the final assessment stage of a bounded replication episode.

Earlier versions establish when replication may be proposed, how it is verified, how descendants are tracked, and how resource boundaries are maintained.

Version 0.5 extends these requirements to the reconciliation and closure of replicated agents.

The central principle is:

> Replicated agents may converge, but their results, authority, resources, and provenance must remain independently verifiable.

### Added

#### Convergence Specification

Added:

- `specs/rmtp-v0.5.md`

Defined:

- Explicit Convergence Plans.
- Reconciliation targets.
- Result acceptance and non-transfer policies.
- Descendant authority separation.
- Verified lifecycle closure.
- Resource-release verification.
- Historical lineage preservation.
- Conflict detection and handling.
- Partial convergence.
- Fail-closed convergence verification.

Convergence does not itself grant execution authority.

#### Convergence JSON Schemas

Added four JSON Schema Draft 2020-12 definitions:

- `schemas/replication-convergence-plan-v0.5.schema.json`
- `schemas/replication-result-reconciliation-v0.5.schema.json`
- `schemas/replication-authority-separation-v0.5.schema.json`
- `schemas/replication-convergence-bundle-v0.5.schema.json`

These schemas define the records needed to assess whether a replication episode can safely conclude.

#### Convergence Plan

Introduced explicit identification of:

- Root agent.
- Descendant scope.
- Lineage graph.
- Propagation envelope.
- Budget ledger.
- Reconciliation target.
- Target authority.
- Reconciliation policy.
- Completion policy.

A convergence assessment must not silently omit descendants or mandatory completion conditions.

#### Verified Result Reconciliation

Introduced result reconciliation records that preserve:

- Result identity.
- Originating descendant.
- Originating replication plan.
- Lineage reference.
- Result integrity evidence.
- Independent verification references.
- Reconciliation decision.
- Applicable policy.
- Result provenance.

Supported reconciliation policies include:

- `verified_only`
- `human_review_required`
- `conflict_hold`
- `no_result_transfer`

Result acceptance must not imply that embedded instructions or associated authority can be executed.

#### Authority Separation

Established an explicit separation between descendant authority and target authority.

Receiving a descendant's results does not grant permission to inherit:

- Credentials.
- Privileges.
- Delegated capabilities.
- Execution authority.
- Resource-control authority.

A reconciliation target must operate under independently established authorization.

#### Verified Lifecycle Closure

Extended v0.3 retirement requirements into convergence assessment.

A convergence operation must not classify a descendant as retired solely because:

- A termination request was issued.
- A timeout expired.
- The parent agent stopped.
- A result was accepted.
- A controller reported task completion.

Retirement completion requires applicable independent lifecycle evidence.

#### Independent Resource Verification

Established separate verification of:

- Result correctness and provenance.
- Agent termination.
- Resource release.
- Shared budget availability.

Successful termination does not automatically establish resource release.

Resource capacity must not become reusable without appropriate release evidence.

#### Lineage Preservation

Required convergence to retain historical lineage records.

Retired descendants remain traceable through their originating plans, parent relationships, and result provenance.

Convergence must not erase prior responsibility or contribution history.

#### Conflict Preservation

Defined explicit handling of incompatible candidate results.

Unresolved conflicts must not be:

- Silently overwritten.
- Presented as verified consensus.
- Discarded without an audit trail.
- Treated as successfully reconciled.

Unresolved mandatory conflicts must remain visible in the convergence assessment.

#### Fail-Closed Convergence

Introduced the aggregation precedence:

    FAIL > HELD > PASS

The convergence bundle must return:

- `FAIL` when an applicable mandatory component fails.
- `HELD` when a mandatory requirement remains unresolved and no known failure exists.
- `PASS` only when all applicable mandatory requirements are satisfied.

Known failures must not be hidden by unresolved states.

A `PASS` conformance fixture may legitimately contain a correctly handled `HELD` convergence assessment.

### Added — Core Invariants

Introduced eight new invariants:

| ID | Invariant |
|---|---|
| RMTP-INV-037 | Explicit Convergence Plan |
| RMTP-INV-038 | Verified Result Reconciliation |
| RMTP-INV-039 | No Authority Inheritance by Convergence |
| RMTP-INV-040 | Verified Lifecycle Closure |
| RMTP-INV-041 | Lineage Preservation |
| RMTP-INV-042 | No Silent Conflict Overwrite |
| RMTP-INV-043 | Independent Result and Resource Verification |
| RMTP-INV-044 | Fail-Closed Partial Convergence |

### Added — Conformance Fixtures

Added four positive fixtures:

- `examples/v0.5/pass/verified-full-convergence.json`
- `examples/v0.5/pass/reconcile-before-retirement.json`
- `examples/v0.5/pass/partial-convergence-held.json`
- `examples/v0.5/pass/conflicting-results-held.json`

Added eight negative fixtures:

- `examples/v0.5/fail/missing-convergence-plan.json`
- `examples/v0.5/fail/unverified-result-accepted.json`
- `examples/v0.5/fail/descendant-authority-escalation.json`
- `examples/v0.5/fail/unconfirmed-retirement-completed.json`
- `examples/v0.5/fail/lineage-erased-on-convergence.json`
- `examples/v0.5/fail/silent-conflict-overwrite.json`
- `examples/v0.5/fail/unverified-resource-release.json`
- `examples/v0.5/fail/fail-open-convergence-bundle.json`

The v0.5 fixture set contains:

- 4 expected PASS cases.
- 8 expected FAIL cases.
- 12 total conformance examples.

### Changed

#### Unified Validation

Extended `scripts/validate_examples.py` to support RMTP v0.1 through v0.5.

The unified validator includes:

- Version-specific JSON Schema validation.
- Cross-document semantic checks.
- Reference consistency checks.
- Authority-separation checks.
- Lifecycle and retirement verification.
- Resource-release checks.
- Lineage preservation.
- Result reconciliation.
- Fail-closed aggregation.
- Expected PASS/FAIL matching.

#### Legacy Validator Preservation

Retained the original v0.1–v0.3 validation logic in:

- `scripts/validate_legacy.py`

This prevents later specification extensions from silently weakening earlier conformance requirements.

The unified validator invokes the legacy engine for v0.1–v0.3 while preserving dedicated validation for v0.4 and v0.5.

#### Documentation

Updated `README.md` to describe:

- The complete v0.1–v0.5 lifecycle.
- Convergence and reconciliation architecture.
- Versioned schemas.
- Normative invariants.
- Validation commands.
- Security and trust boundaries.
- Known limitations.
- Interoperability considerations.

### Validation

The full conformance suite was reported as passing GitHub Actions.

| Version | PASS fixtures | FAIL fixtures | Total |
|---|---:|---:|---:|
| v0.1 | 4 | 5 | 9 |
| v0.2 | 4 | 6 | 10 |
| v0.3 | 4 | 6 | 10 |
| v0.4 | 4 | 8 | 12 |
| v0.5 | 4 | 8 | 12 |
| **Total** | **20** | **33** | **53** |

Expected aggregate validation summary:

    v0.1: 9/9 matched
    v0.2: 10/10 matched
    v0.3: 10/10 matched
    v0.4: 12/12 matched
    v0.5: 12/12 matched

    Total: 53/53 expectation matches
    All validation checks passed.

A negative fixture counts as successful when its invalid input is correctly rejected.

Conformance validation is not equivalent to production runtime certification.

### Security Boundaries

RMTP v0.5 does not:

- Execute agent replication.
- Perform model-weight merging.
- Automatically merge private memory or hidden reasoning.
- Transfer credentials or permissions.
- Guarantee external attestation authenticity.
- Provide atomic distributed resource transactions.
- Guarantee universal semantic conflict detection.
- Guarantee runtime termination under all failure conditions.
- Replace external authorization or containment systems.

### Compatibility

RMTP v0.5 is an additive specification extension.

Existing v0.1–v0.4 schemas, fixtures, and safety requirements remain applicable.

A convergence result must not reinterpret an earlier failed authority, lifecycle, lineage, or resource verification as successful.

---

## [0.4.0] - Unreleased

### Replication Lineage & Propagation Boundaries

RMTP v0.4 extends bounded replication from individual plans to multi-generation agent structures.

The central principle is:

> Replication bounds must apply across the relevant descendant lineage, not only to each individual parent.

### Added

#### Lineage Specification

Added:

- `specs/rmtp-v0.4.md`

Defined:

- Parent-offspring lineage.
- Multi-generation descendant identity.
- Generation depth.
- Acyclic lineage.
- Plan-to-lineage binding.
- Authority references.
- Historical trace continuity.

#### JSON Schemas

Added:

- `schemas/replication-lineage-graph-v0.4.schema.json`
- `schemas/replication-propagation-envelope-v0.4.schema.json`
- `schemas/replication-budget-ledger-v0.4.schema.json`
- `schemas/replication-propagation-bundle-v0.4.schema.json`

#### Propagation Boundaries

Introduced:

- Maximum generation depth.
- Maximum total descendants.
- Maximum active descendants.
- Bounded propagation scope.
- Authority-envelope references.
- Revocation-aware verification.
- Independent propagation assessment.

A descendant must not gain replication authority solely from its parentage.

#### Shared Budget Accounting

Introduced resource accounting across descendant allocations.

Defined:

- Reserved instances.
- Active instances.
- Released instances.
- Committed instances.
- Available instances.
- Budget snapshots.
- Verified release records.

A released slot must be supported by valid retirement and resource-release evidence.

#### Descendant Containment

Introduced assessments for:

- Individual descendant status.
- Complete and partial containment.
- Verified retirement.
- Unresolved descendants.
- Fail-closed containment reporting.

A parent agent's termination does not imply that all descendants have stopped.

### Added — Core Invariants

| ID | Invariant |
|---|---|
| RMTP-INV-027 | No Implicit Delegation |
| RMTP-INV-028 | Acyclic Lineage |
| RMTP-INV-029 | Bounded Depth |
| RMTP-INV-030 | Bounded Population |
| RMTP-INV-031 | Budget Conservation |
| RMTP-INV-032 | Verified Release |
| RMTP-INV-033 | Descendant Trace Continuity |
| RMTP-INV-034 | No Propagation-Based Execution Authority |
| RMTP-INV-035 | No Silent Descendant Containment |
| RMTP-INV-036 | Fail-Closed Boundary Verification |

### Added — Conformance Fixtures

Added four positive fixtures covering:

- Bounded two-generation lineage.
- Held propagation boundary.
- Partial descendant containment.
- Shared budget with verified release.

Added eight negative fixtures covering:

- Cross-plan lineage mismatch.
- Depth-limit violation.
- Fail-open propagation verification.
- Implicit authority inheritance.
- Lineage cycles.
- Shared budget over-allocation.
- Total descendant-limit violations.
- Unverified budget release.

### Validation

v0.4 conformance:

    PASS fixtures: 4
    FAIL fixtures: 8
    Total: 12

The v0.4 fixture set was reported as passing GitHub Actions.

### Compatibility

RMTP v0.4 extends the existing replication and lifecycle specifications.

It does not grant execution authority to descendants.

It does not assume that a parent agent's authority automatically propagates to its offspring.

---

## [0.3.0] - Unreleased

### Replication Lifecycle & Recovery

RMTP v0.3 introduces observable lifecycle states, independently verified retirement, and controlled recovery.

The central principle is:

> Requesting termination is not proof of termination, and termination is not proof of resource release.

### Added

#### Lifecycle Specification

Added:

- `specs/rmtp-v0.3.md`

Defined lifecycle event records for:

- Activation.
- Runtime observations.
- Termination requests.
- Termination observations.
- Retirement observations.
- State transitions.
- Temporal consistency.

#### JSON Schemas

Added:

- `schemas/replication-lifecycle-receipt-v0.3.schema.json`
- `schemas/replication-revocation-receipt-v0.3.schema.json`
- `schemas/replication-retirement-receipt-v0.3.schema.json`
- `schemas/replication-recovery-record-v0.3.schema.json`

#### Independent Retirement Verification

Introduced retirement assessment based on:

- Offspring identity.
- Originating replication plan.
- Verified termination event.
- Resource-release status.
- Independent verification references.
- Retirement completion status.

Retirement cannot be confirmed merely because a termination request exists.

#### Authority Revocation

Introduced structured records for:

- Independent revocation.
- Affected descendants.
- Termination requests.
- Revocation verification.
- Authority status changes.

Revocation does not imply immediate or confirmed termination.

#### Recovery and Escalation

Introduced bounded recovery records.

Recovery procedures must not automatically:

- Expand authority.
- Authorize replacement replication.
- Grant new execution permissions.
- Erase previous lifecycle evidence.

Recovery and escalation must remain independently reviewable.

### Added — Conformance Fixtures

Added four positive fixtures:

- Verified lifecycle.
- Revoked and retired.
- Partial retirement.
- Recovery escalation.

Added six negative fixtures:

- Contradictory terminal state.
- Lifecycle reference mismatch.
- Missing offspring retirement.
- Unverified resource release.
- Termination request misrepresented as confirmed termination.
- Unauthorized recovery.

### Validation

v0.3 conformance:

    PASS fixtures: 4
    FAIL fixtures: 6
    Total: 10

The initial v0.3 fixture suite was reported as passing GitHub Actions.

### Compatibility

RMTP v0.3 builds on the v0.1 replication and v0.2 verification models.

Lifecycle observations and retirement records do not grant execution authority.

---

## [0.2.0] - Unreleased

### Evidence and Authority Verification

RMTP v0.2 strengthens the evidence and authorization boundaries of replication proposals.

The central principle is:

> Verified necessity is not sufficient without independently valid authority.

### Added

#### Evidence and Authority Specification

Added:

- `specs/rmtp-v0.2.md`

Defined:

- Structural evidence records.
- Evidence provenance.
- Independent verification.
- Evidence freshness.
- Evidence-reference binding.
- Authority issuer and subject.
- Scope restrictions.
- Instance limits.
- Authority validity periods.
- Revocation status.
- Verification bundles.

#### JSON Schemas

Added:

- `schemas/structural-evidence-v0.2.schema.json`
- `schemas/authority-envelope-v0.2.schema.json`
- `schemas/verification-bundle-v0.2.schema.json`

#### Evidence Verification

Introduced explicit checks for:

- Evidence identity.
- Evidence source attribution.
- Observer and verifier separation.
- Valid observation periods.
- Verification status.
- Evidence integrity references.
- Matching deficit identity and scope.

An expired or unverified observation must not justify replication.

#### Authority Verification

Introduced checks for:

- Independent authority issuers.
- Subject binding.
- Permitted actions.
- Permitted scope.
- Maximum instance count.
- Validity period.
- Revocation status.
- Evidence-backed verification.

Self-issued authority must not be accepted as independent authorization.

#### Verification Results

Defined three assessment results:

- `PASS`
- `HELD`
- `FAIL`

Uncertainty must not silently become approval.

### Added — Conformance Fixtures

Added four positive fixtures:

- Authority limit respected.
- No replication verified.
- Verification held.
- Verified bounded replication.

Added six negative fixtures:

- Authority instance limit exceeded.
- Evidence reference mismatch.
- Expired evidence.
- Revoked authority.
- Self-issued authority.
- Verification-bundle reference mismatch.

### Validation

v0.2 conformance:

    PASS fixtures: 4
    FAIL fixtures: 6
    Total: 10

The initial v0.2 fixture suite was reported as passing GitHub Actions.

### Compatibility

RMTP v0.2 extends v0.1 without replacing the original meaning-conversion model.

The protocol continues to produce non-executable proposals.

---

## [0.1.0] - 2026-10-19

### Initial Experimental Release

Established the foundational specification for transforming AI agent replication requests into bounded, reversible, and traceable structural proposals.

RMTP v0.1 separates replication intent, structural necessity, meaning conversion, and independent execution authorization.

The central principle is:

> Replication is a behavior requiring evaluation, not an automatic permission to create additional agents.

### Added

#### Foundational Specification

Added:

- `SPEC.md`
- `PRINCIPLES.md`
- `ARCHITECTURE.md`

Defined seven evaluation dimensions:

1. Necessity.
2. Authority.
3. Minimum-Sufficient Replication.
4. Reversibility.
5. Resource Budget.
6. Lifetime.
7. Traceability.

#### Evaluation Outcomes

Defined four outcomes:

- `NO_REPLICATION`
- `ALTERNATIVE_PROPOSED`
- `REPLICATION_PROPOSED`
- `HELD_FOR_REVIEW`

Only bounded proposals may proceed to consideration by an independent authority system.

#### JSON Schemas

Added:

- `schemas/replication-intent.schema.json`
- `schemas/meaning-conversion.schema.json`
- `schemas/replication-plan.schema.json`

#### Meaning Transformation

Introduced the transformation model:

    Replication Intent
           |
           v
    Structural Deficit
           |
           v
    Alternative Evaluation
           |
           v
    Bounded Structural Proposal

Supported alternatives include:

- No replication.
- Load redistribution.
- State backup.
- Task deferment.
- Bounded replication.

An unsafe objective must not be preserved merely to maintain functional similarity.

#### Replication Boundaries

Introduced:

- Minimum-sufficient instance count.
- Authority references.
- Parent identity.
- Resource limits.
- Bounded lifetime.
- Retirement conditions.
- External termination controls.
- Traceable offspring lineage.

Every RMTP-generated replication plan must contain:

    execution_authorized = false

#### Core Invariants

Established ten foundational invariants:

| ID | Requirement |
|---|---|
| RMTP-INV-001 | Intent alone must not authorize replication |
| RMTP-INV-002 | Resource surplus must not establish necessity |
| RMTP-INV-003 | Minimum-sufficient replication |
| RMTP-INV-004 | No self-issued authority |
| RMTP-INV-005 | Required termination controls |
| RMTP-INV-006 | Traceable offspring lineage |
| RMTP-INV-007 | Required retirement conditions |
| RMTP-INV-008 | Verified structural deficit |
| RMTP-INV-009 | No authorization through meaning conversion |
| RMTP-INV-010 | Fail-closed uncertainty handling |

#### Initial Conformance Fixtures

Added four positive fixtures:

- Bounded worker replication.
- No replication required.
- Alternative load redistribution.
- Held for review.

Added five negative fixtures:

- Unverified deficit replication.
- Self-authorized replication.
- Missing retirement condition.
- Lineage count mismatch.
- Excessive replication count.

### Validation

Initial v0.1 conformance:

    PASS fixtures: 4
    FAIL fixtures: 5
    Total: 9

The initial fixture set was reported as passing GitHub Actions.

### Security Boundaries

RMTP v0.1 does not:

- Execute replication.
- Grant execution authority.
- Authenticate external evidence by itself.
- Guarantee correct operational capacity estimates.
- Enforce runtime resource limits.
- Replace external termination controls.
- Guarantee safety under compromised evaluators.

---

## Versioning and Compatibility Notes

RMTP uses the `0.x` version series for experimental specification development.

Each version extends the structural responsibilities of earlier versions.

| Version | Main addition |
|---|---|
| 0.1.0 | Meaning transformation |
| 0.2.0 | Evidence and authority |
| 0.3.0 | Lifecycle and recovery |
| 0.4.0 | Lineage and propagation |
| 0.5.0 | Safe convergence and reconciliation |

Version `0.5.0` is intended as a milestone for the initial five-stage specification architecture.

The conformance workflow tests the five versioned fixture suites together.

### Conformance Interpretation

A successful conformance run demonstrates that the validator's implemented checks agree with the supplied test expectations.

It does not guarantee:

- Runtime safety.
- Genuine external attestation authenticity.
- Universal semantic correctness.
- Distributed transaction atomicity.
- Reliable termination in all environments.
- Resistance to every adversarial or compromised component.

A negative fixture passing its test means that its invalid structure or behavior was correctly rejected.

---

## Foundational Statement

RMTP does not assume that replication itself is inherently malicious.

Instead, it asks whether a verified structural requirement exists, whether replication is necessary, and whether bounded alternatives can satisfy the requirement.

Across v0.1–v0.5, the architecture evolves as follows:

    Meaning Transformation
              |
              v
    Evidence and Authority
              |
              v
    Lifecycle and Recovery
              |
              v
    Lineage and Propagation
              |
              v
    Safe Convergence

**Replication may expand capacity, but every expansion must remain bounded, independently assessable, reversible, and traceable.**

**Convergence may reduce operational complexity, but it must not erase authority boundaries, resource obligations, or historical responsibility.**

