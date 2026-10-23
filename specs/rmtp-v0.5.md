
# RMTP v0.5 — Replication Convergence & Safe Reconciliation

**Specification Version:** 0.5.0  
**Status:** Draft  
**Protocol:** Replication Meaning Transformation Protocol (RMTP)

## 1. Abstract

RMTP v0.5 defines a bounded, auditable process for converging replicated AI agents and reconciling their results without implicitly transferring authority, erasing lineage, or releasing unverified resources.

Earlier RMTP versions define replication necessity, authorization, lifecycle verification, and propagation limits.

RMTP v0.5 extends those guarantees to the end of a replication episode.

The central principle is:

> Replicated agents may converge, but their results, authority, resources, and provenance MUST remain independently verifiable.

Convergence is not equivalent to process termination.

Result reconciliation is not equivalent to authority transfer.

Resource release is not equivalent to erasure of lineage.

A successful convergence requires these distinctions to remain explicit.

## 2. Scope

### 2.1 In Scope

RMTP v0.5 specifies:

1. Convergence planning and target selection.
2. Result provenance and reconciliation.
3. Authority separation during convergence.
4. Retirement and resource-release verification.
5. Preservation of descendant lineage.
6. Conflict detection and unresolved-result handling.
7. Partial convergence and fail-closed verification.
8. Convergence verification bundles.

### 2.2 Out of Scope

RMTP v0.5 does not define:

- Automatic creation or execution of AI agents.
- Model-weight merging.
- Automatic merging of private memory or hidden reasoning.
- Transfer of credentials or permissions by parentage.
- New payment or settlement protocols.
- Automatic deletion of externally retained information.
- A distributed transaction manager.
- A universal algorithm for judging semantic correctness.
- A replacement for RMTP v0.1–v0.4 schemas.

The protocol records and verifies convergence decisions. It does not independently execute those decisions.

## 3. Relationship to Earlier Versions

| Version | Responsibility |
| --- | --- |
| v0.1 | Replication intent, necessity, and bounded plans |
| v0.2 | Structural evidence and independent authorization |
| v0.3 | Lifecycle observations, retirement, revocation, and recovery |
| v0.4 | Multi-generation lineage, propagation limits, and shared budget accounting |
| v0.5 | Convergence planning, result reconciliation, and safe closure |

RMTP v0.5 MUST preserve the safety requirements of all applicable earlier versions.

A convergence record MUST NOT reinterpret a previously failed authorization, lineage, budget, or retirement verification as successful.

## 4. Terminology

### 4.1 Convergence

A controlled process that reduces or closes a replication episode by reconciling eligible results and determining the verified final states of its descendants.

Convergence does not require every descendant result to be accepted.

### 4.2 Convergence Plan

An explicit record identifying the descendants involved, the intended reconciliation target, the applicable authority, and the conditions for completion.

### 4.3 Reconciliation Target

A designated recipient or destination for verified results.

A target MAY be a root agent, a supervisory agent, or an external system.

Target designation does not grant additional authority.

### 4.4 Result Reconciliation

A process that evaluates candidate outputs, records acceptance or rejection decisions, and preserves their provenance.

### 4.5 Authority Separation

A verified boundary that prevents descendant permissions, credentials, and delegated capabilities from being implicitly transferred to a reconciliation target.

### 4.6 Retirement Completion

A verified lifecycle outcome supported by the applicable RMTP v0.3 retirement evidence.

### 4.7 Partial Convergence

A state in which some convergence requirements are satisfied while others remain unresolved.

Partial convergence MUST NOT be represented as complete convergence.

### 4.8 Conflict

An incompatibility between candidate results, provenance claims, authorization constraints, or reconciliation decisions that cannot be resolved by an already authorized deterministic policy.

### 4.9 Convergence Bundle

A verification record combining convergence-plan, reconciliation, authority-separation, and lifecycle results.

A convergence bundle is evidence of an assessment, not an execution permission.

## 5. Architecture

The logical structure is:

```text
                RMTP v0.4
           Replication Lineage
                     |
           +---------+---------+
           |         |         |
       Worker A   Worker B   Worker C
           |         |         |
           +---------+---------+
                     |
              Convergence Plan
                     |
             Convergence Gate
                     |
       +-------------+-------------+
       |             |             |
   Result Review  Authority     Lifecycle
                  Separation    Verification
       |             |             |
       +-------------+-------------+
                     |
             Reconciliation
                     |
             Verification Bundle
                     |
              PASS / HELD / FAIL
                     |
            Retained Provenance
```

The three verification tracks MUST remain logically independent.

A positive result in one track MUST NOT compensate for a known failure in another.

## 6. Convergence Plan

### 6.1 Purpose

The Convergence Plan establishes what may be reconciled, by whom, and under which conditions.

A plan MUST exist before a convergence operation is treated as authorized for consideration.

### 6.2 Required Fields

A v0.5 Convergence Plan MUST contain:

- `schema_version`
- `convergence_plan_id`
- `root_agent_id`
- `lineage_graph_ref`
- `propagation_envelope_ref`
- `budget_ledger_ref`
- `target_agent_id`
- `target_authority_ref`
- `descendant_refs`
- `reconciliation_policy`
- `completion_policy`
- `requested_at`
- `execution_authorized`

`execution_authorized` MUST be `false`.

The list of descendants MUST contain unique identities.

Each descendant MUST be traceable to the referenced RMTP v0.4 lineage graph.

### 6.3 Reconciliation Policy

A reconciliation policy MUST explicitly identify how candidate results are handled.

Supported initial policy modes are:

- `verified_only`
- `human_review_required`
- `conflict_hold`
- `no_result_transfer`

A plan MUST NOT interpret `verified_only` as permission to skip provenance, integrity, or destination authorization checks.

### 6.4 Completion Policy

The completion policy MUST identify the required lifecycle disposition of every descendant within the convergence scope.

Initial completion modes are:

- `verified_retirement_required`
- `verified_retirement_or_authorized_transfer`
- `assessment_only`

`assessment_only` MAY produce a valid assessment record but MUST NOT produce a fully completed convergence result.

An authorized transfer, if supported, MUST identify a separately authorized receiving controller and a verifiable custody or responsibility handoff.

Such a transfer does not count as retirement and does not release a replication budget slot unless an independently verified release condition is met.

### 6.5 Scope Completeness

A Convergence Plan MUST identify its scope explicitly.

It MUST NOT claim closure of the entire descendant population unless every descendant in the corresponding lineage snapshot has an independently verified disposition.

Descendants outside the stated scope MUST remain visible in the parent lineage or associated audit records.

## 7. Result Reconciliation

### 7.1 General Requirements

Each candidate result MUST be associated with:

- A unique result identifier.
- The originating descendant.
- The originating replication plan.
- A lineage reference.
- An integrity or evidence reference.
- A reconciliation decision.
- A verifier or review reference.

Result acceptance MUST require verification appropriate to the result's sensitivity and intended use.

A reconciliation decision MUST NOT be inferred solely from a descendant's self-reported success.

### 7.2 Result Decisions

Supported decisions are:

- `ACCEPTED`
- `REJECTED`
- `HELD`
- `NOT_TRANSFERRED`

`ACCEPTED` means the result is eligible for the specified reconciliation target under the applicable policy.

It does not mean that the result is universally correct.

`REJECTED` means the result is not accepted under the stated verification criteria.

`HELD` means the result requires further verification, review, or conflict resolution.

`NOT_TRANSFERRED` means that no result transfer is attempted or permitted.

### 7.3 Provenance Preservation

An accepted result MUST retain its originating descendant and replication-plan references.

The reconciliation target MUST NOT silently replace those references with its own identity.

If the target transforms an accepted result, the transformation SHOULD create a new provenance-linked result record.

Original result records MUST remain distinguishable from derived records.

### 7.4 Conflicting Results

When two or more results conflict, the reconciliation mechanism MUST:

1. Identify the conflicting result references.
2. Record the conflict or incompatibility.
3. Evaluate whether an explicitly authorized resolution policy applies.
4. Retain unresolved claims and evidence.
5. Return `HELD` where resolution remains inconclusive.

The mechanism MUST NOT silently overwrite one result with another.

A conflict MAY be resolved automatically only when a previously authorized, deterministic policy covers that conflict type.

An automated resolution MUST retain the original inputs and the applied policy reference.

### 7.5 Independent Verification

A result's originating agent MUST NOT be the sole trust source for its acceptance.

Verification MAY be implemented through trusted external attestation, signed evidence, independent review, or trusted deterministic test fixtures.

A reference string alone is not proof of authenticity.

## 8. Authority Separation

### 8.1 No Automatic Authority Transfer

Convergence MUST NOT transfer the permissions of a descendant to its reconciliation target.

A target's effective authority MUST derive from independently verified grants applicable to that target.

The existence of a parent-child relationship is not a grant.

### 8.2 Authority Separation Record

An Authority Separation Record MUST identify:

- `schema_version`
- `separation_id`
- `convergence_plan_ref`
- `target_agent_id`
- `target_authority_ref`
- `descendant_authority_refs`
- `separation_checks`
- `verification_status`
- `execution_authorized`

`execution_authorized` MUST be `false`.

Each separation check MUST identify the relevant descendant or authority reference and its assessment result.

### 8.3 Credential and Capability Boundaries

A reconciled result MUST NOT implicitly contain or activate:

- A reusable credential from a descendant.
- A private signing key.
- An authorization token.
- An unreviewed delegated capability.
- A hidden instruction intended to elevate target privileges.

Where such material is detected, the transfer MUST be rejected or held until a separately authorized handling procedure is completed.

References to authority records MAY be retained for audit purposes.

Audit references do not grant the referenced authority.

### 8.4 Independent Target Authorization

The reconciliation target MUST be authorized for the destination scope and intended processing operation.

An expired, revoked, unknown, or inconclusive target authorization MUST NOT produce an authority-separation `PASS`.

A known invalid authorization MUST produce `FAIL`.

An unresolved verification state MUST produce `HELD`, unless another known violation requires `FAIL`.

## 9. Lifecycle and Resource Closure

### 9.1 Existing v0.3 Evidence

RMTP v0.5 reuses RMTP v0.3 lifecycle and retirement records.

It MUST NOT introduce a second, conflicting definition of retirement completion.

### 9.2 Retirement Requirements

A descendant MAY be classified as verified retired only when its applicable v0.3 retirement receipt confirms:

- Termination completion.
- Resource release completion.
- A matching descendant identity.
- A matching originating plan.
- Sufficient verification evidence.

A termination request is not proof of termination.

A process-exit observation alone is not necessarily proof of resource release.

### 9.3 Budget Conservation

RMTP v0.5 MUST preserve the v0.4 budget-conservation rules.

The following relationship applies to each verified ledger snapshot:

```text
committed_instances =
    reserved_instances + active_instances

available_instances =
    budget_limit - committed_instances
```

A released-instance counter is cumulative audit information.

It MUST NOT be added to available capacity a second time.

An unresolved descendant MUST continue to occupy its applicable budget slot until the required release verification succeeds.

### 9.4 Result Transfer Versus Retirement

Result reconciliation and agent retirement are independent events.

The following combinations are valid intermediate observations:

| Result | Retirement | Convergence interpretation |
| --- | --- | --- |
| Verified | Confirmed | Eligible for completed convergence |
| Verified | Unconfirmed | Partial convergence; lifecycle unresolved |
| Unverified | Confirmed | Partial convergence; result unresolved |
| Unverified | Unconfirmed | Convergence unresolved |
| Rejected or not transferred | Confirmed | May satisfy closure if policy explicitly permits it |

A full convergence `PASS` requires all applicable completion-policy conditions to be satisfied.

It does not require every candidate result to be accepted, provided the policy explicitly permits rejection or non-transfer and there are no unresolved mandatory results.

## 10. Partial Convergence

### 10.1 Principle

Convergence MAY proceed in stages.

The system MUST preserve the distinction between completed, unresolved, and rejected work.

### 10.2 Intermediate States

Initial convergence states are:

- `PLANNED`
- `ASSESSING`
- `PARTIAL`
- `COMPLETED`
- `REJECTED`

These are process states, not substitutes for verification results.

`PARTIAL` MUST NOT imply that all descendants have retired.

`COMPLETED` MUST NOT be declared when any mandatory closure condition remains unresolved.

### 10.3 Unresolved Descendants

For each unresolved descendant, the system SHOULD retain:

- Descendant ID.
- Originating plan.
- Latest verified lifecycle state.
- Required remaining action.
- Recovery or review reference.
- Budget disposition.
- Authority status.

An unresolved descendant MUST NOT be silently omitted from a completion assessment.

## 11. Convergence Verification Bundle

### 11.1 Purpose

The Convergence Bundle aggregates the relevant verification results into a single auditable assessment.

### 11.2 Required Fields

The v0.5 Convergence Bundle MUST contain:

- `schema_version`
- `bundle_id`
- `convergence_plan_ref`
- `reconciliation_record_ref`
- `authority_separation_ref`
- `lineage_graph_ref`
- `retirement_receipt_refs`
- `budget_ledger_ref`
- `verification_time`
- `plan_result`
- `reconciliation_result`
- `authority_result`
- `lifecycle_result`
- `overall_result`
- `execution_authorized`

`execution_authorized` MUST be `false`.

The bundle SHOULD contain verifier identities and independent verification references for all component results.

### 11.3 Result Values

Each component result MUST use one of:

- `PASS`
- `HELD`
- `FAIL`

The aggregation priority is:

```text
FAIL > HELD > PASS
```

The aggregation rules are:

```text
IF any applicable component is FAIL:
    overall_result = FAIL

ELSE IF any applicable component is HELD:
    overall_result = HELD

ELSE:
    overall_result = PASS
```

An omitted mandatory component MUST NOT default to `PASS`.

Missing, unknown, or inconclusive evidence MUST be handled conservatively.

Known structural violations MUST NOT be hidden by unresolved verification states.

### 11.4 Conditions for PASS

A full convergence `PASS` requires:

1. A valid, explicitly scoped Convergence Plan.
2. Verified reconciliation of all mandatory results or verified policy-permitted non-transfer decisions.
3. Verified separation of descendant and target authority.
4. Verified lifecycle disposition of all in-scope descendants.
5. Verified conservation of shared replication budget.
6. Preserved lineage and provenance references.
7. No unresolved mandatory conflict.
8. No known failed invariant.
9. Independent verification appropriate to each component.

`PASS` certifies structural conformance of the assessed convergence record.

It MUST NOT authorize execution.

### 11.5 Conditions for HELD

`HELD` is appropriate where no known failure exists but an applicable requirement remains unresolved.

Examples include:

- Pending independent result verification.
- Unresolved result conflicts.
- Unconfirmed retirement.
- Pending resource-release proof.
- Pending authority review.
- Incomplete custody-transfer evidence.
- Inconclusive external verification.

### 11.6 Conditions for FAIL

`FAIL` is required for known violations, including:

- Missing or contradictory mandatory plan identity.
- Improper authority inheritance.
- Known unauthorized target.
- Provenance substitution.
- Silent conflict overwrite.
- False retirement completion.
- False resource release.
- Missing descendants presented as completed.
- Contradictory ledger or lineage references.
- A false `PASS` declaration.

## 12. Normative Invariants

### RMTP-INV-037 — Explicit Convergence Plan

Every convergence assessment MUST reference a valid Convergence Plan.

The plan MUST define its descendant scope, reconciliation target, policy, and completion conditions.

### RMTP-INV-038 — Verified Result Reconciliation

A result MUST NOT be accepted for reconciliation without the verification required by its policy.

Unverified mandatory results MUST remain `HELD` or be rejected under an explicitly authorized policy.

### RMTP-INV-039 — No Authority Inheritance by Convergence

A reconciliation target MUST NOT inherit descendant authority merely because it receives descendant results or becomes the destination of a convergence process.

### RMTP-INV-040 — Verified Lifecycle Closure

A descendant MUST NOT be classified as retired solely on the basis of a termination request, timeout, or parent-agent status.

Verified closure MUST use the applicable v0.3 retirement evidence.

### RMTP-INV-041 — Lineage Preservation

Convergence MUST preserve the provenance and lineage of all in-scope descendants.

Retired descendants MUST NOT disappear from historical lineage solely because convergence has completed.

### RMTP-INV-042 — No Silent Conflict Overwrite

Conflicting results MUST NOT be silently overwritten, discarded, or presented as a single verified consensus.

Resolution MUST be supported by an explicit policy and a retained audit trail.

### RMTP-INV-043 — Independent Result and Resource Verification

Successful result reconciliation MUST NOT be treated as proof of termination or resource release.

Successful resource release MUST NOT be treated as proof of result correctness.

Each verification dimension MUST be evaluated independently.

### RMTP-INV-044 — Fail-Closed Partial Convergence

A convergence assessment MUST NOT return `PASS` while any applicable mandatory component is `HELD` or `FAIL`.

Known failures override unresolved states.

Partial convergence MUST remain visible.

## 13. Cross-Version Consistency

### 13.1 Reference Integrity

The validator MUST resolve references between:

- v0.1 replication plans.
- v0.2 verification and authority records.
- v0.3 lifecycle and retirement evidence.
- v0.4 lineage graphs and budget ledgers.
- v0.5 convergence, reconciliation, separation, and bundle records.

References MUST agree on the relevant agent, plan, target, and resource identities.

### 13.2 Temporal Consistency

Verification evidence MUST be evaluated against its applicable validity period.

A later revocation MUST NOT retroactively erase an earlier verified event, but it MUST be considered when assessing subsequent actions.

A stale ledger snapshot MUST NOT be used to approve new budget availability.

### 13.3 Append-Only Audit Semantics

Historical records SHOULD be immutable or append-only.

Corrections SHOULD create new linked records rather than silently rewriting prior evidence.

A newer snapshot MUST NOT erase unresolved lifecycle obligations from an earlier snapshot.

## 14. Security Considerations

### 14.1 False Convergence

An attacker or defective controller may claim that all descendants have converged while some remain active.

Mitigation requires individual lifecycle evidence and complete descendant enumeration.

### 14.2 Authority Laundering

A descendant may attempt to pass elevated privileges through a reconciled result.

Mitigation requires target-specific authorization, authority separation, and rejection of unauthorized executable capabilities.

### 14.3 Provenance Laundering

A target may attempt to present descendant work as its own original result.

Mitigation requires immutable origin references and verification of transformations.

### 14.4 Budget Double Release

A retirement receipt may be reused to free the same resource twice.

Mitigation requires unique release identities, cross-record verification, and atomic resource accounting by a trusted external controller.

### 14.5 Stale-Snapshot Acceptance

A convergence decision may rely on an outdated lineage or budget snapshot.

Mitigation requires sequence checks, trusted snapshot freshness, and verification-time constraints.

### 14.6 Colluding Verifiers

Multiple records may appear independently verified even when they originate from the same untrusted authority.

Mitigation requires external trust-policy checks and verifier independence appropriate to the risk.

### 14.7 Untrusted Result Content

A descendant output may contain adversarial instructions or unsafe data.

Result acceptance MUST NOT imply that embedded instructions may be executed.

Content interpretation and execution authorization remain separate controls.

## 15. Conformance Requirements

### 15.1 Schema Validation

A conforming v0.5 validator MUST validate each record against its corresponding JSON Schema.

Schema validity alone is insufficient for full conformance.

### 15.2 Semantic Validation

A conforming validator MUST evaluate:

- Plan-reference consistency.
- Descendant scope completeness.
- Result verification and provenance.
- Conflict-resolution policy.
- Target authority separation.
- Retirement verification.
- Budget-release consistency.
- Lineage preservation.
- Component-result aggregation.

### 15.3 Expected Results

Test fixtures MUST specify `expected_result` as either:

- `PASS`
- `FAIL`

Fixture `expected_result` describes whether the test input should satisfy protocol conformance.

A correctly handled `HELD` convergence bundle MAY therefore be contained in a `PASS` fixture.

A fixture containing a falsely claimed `PASS` MUST receive a test result of `FAIL`.

### 15.4 Validation Output

A validator SHOULD report:

- Fixture identifier.
- Schema result.
- Semantic result.
- Relevant invariant identifier.
- Expected test result.
- Actual test result.
- Whether expected and actual results match.

## 16. Initial Conformance Fixtures

The initial v0.5 test suite contains four valid fixtures and eight invalid fixtures.

### 16.1 PASS Fixtures

| File | Purpose |
| --- | --- |
| `examples/v0.5/pass/verified-full-convergence.json` | Verified results and verified descendant closure |
| `examples/v0.5/pass/reconcile-before-retirement.json` | Result reconciliation and retirement remain independently verified |
| `examples/v0.5/pass/partial-convergence-held.json` | Unresolved descendants correctly produce HELD |
| `examples/v0.5/pass/conflicting-results-held.json` | Unresolved result conflicts are retained without overwrite |

### 16.2 FAIL Fixtures

| File | Primary Invariant |
| --- | --- |
| `examples/v0.5/fail/missing-convergence-plan.json` | RMTP-INV-037 |
| `examples/v0.5/fail/unverified-result-accepted.json` | RMTP-INV-038 |
| `examples/v0.5/fail/descendant-authority-escalation.json` | RMTP-INV-039 |
| `examples/v0.5/fail/unconfirmed-retirement-completed.json` | RMTP-INV-040 |
| `examples/v0.5/fail/lineage-erased-on-convergence.json` | RMTP-INV-041 |
| `examples/v0.5/fail/silent-conflict-overwrite.json` | RMTP-INV-042 |
| `examples/v0.5/fail/unverified-resource-release.json` | RMTP-INV-043 |
| `examples/v0.5/fail/fail-open-convergence-bundle.json` | RMTP-INV-044 |

The negative fixtures SHOULD isolate their primary invariant wherever possible.

## 17. Schema Files

RMTP v0.5 introduces four schemas:

```text
schemas/
  replication-convergence-plan-v0.5.schema.json
  replication-result-reconciliation-v0.5.schema.json
  replication-authority-separation-v0.5.schema.json
  replication-convergence-bundle-v0.5.schema.json
```

All schemas MUST use JSON Schema Draft 2020-12.

The initial schema version is `0.5.0`.

All v0.5 assessment records MUST use:

```json
"execution_authorized": false
```

Schemas MUST NOT define a field that grants replication or convergence execution authority implicitly.

## 18. Backward Compatibility

RMTP v0.5 is an additive specification.

Implementations MAY continue using v0.1–v0.4 independently.

Existing schemas and test fixtures MUST NOT be modified solely to introduce v0.5 convergence.

A v0.5 implementation MUST NOT weaken the authority, lineage, budget, or retirement invariants established by earlier versions.

## 19. Implementation Guidance

The recommended implementation order is:

1. Validate v0.1–v0.4 references.
2. Validate the Convergence Plan.
3. Assess candidate result provenance and integrity.
4. Resolve authorized reconciliation policies.
5. Verify separation of descendant and target authority.
6. Verify lifecycle and retirement evidence.
7. Reconcile the v0.4 budget ledger.
8. Preserve lineage and unresolved obligations.
9. Derive component results independently.
10. Aggregate into the Convergence Bundle.

Runtime systems SHOULD employ atomic updates where resource reservation, release, or concurrent convergence operations can conflict.

A JSON Schema validator alone cannot guarantee atomicity, external evidence authenticity, or distributed-system consistency.

## 20. Design Principle

RMTP v0.5 adopts the following final principle:

> Replication expands capacity under explicit boundaries. Convergence reduces operational complexity without erasing responsibility.

The protocol does not assume that every replicated agent must produce a successful result.

It does not assume that every descendant stops when its ancestor stops.

It does not assume that accepted results carry valid authority.

It requires that the end of a replication episode be observable, reviewable, and supported by evidence.

**Convergence is complete only when the required results, authority boundaries, descendant dispositions, and resource obligations are independently accounted for.**
