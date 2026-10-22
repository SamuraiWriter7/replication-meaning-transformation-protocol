
# RMTP v0.4 — Replication Lineage & Propagation Boundaries

**Protocol:** Replication Meaning Transformation Protocol
**Version:** 0.4.0
**Status:** Experimental Draft
**Compatibility:** RMTP v0.1.0 / v0.2.0 / v0.3.0

## 1. Abstract

RMTP v0.4 introduces lineage integrity, replication propagation boundaries, budget accounting, and descendant containment for bounded AI agent replication.

Previous versions establish:

- v0.1: Meaning conversion and replication necessity.
- v0.2: Evidence and authority verification.
- v0.3: Lifecycle, revocation, retirement, and recovery verification.

Version 0.4 addresses recursive and distributed replication.

A replicated agent may identify a legitimate need for additional capacity. However, its existence as an authorized offspring does not automatically grant the authority to generate further descendants.

RMTP v0.4 therefore defines how descendant replication requests can be evaluated without allowing authority, population limits, or resource budgets to expand implicitly.

The protocol specifies records, constraints, and validation rules.

It does not perform replication or grant runtime permissions.

## 2. Scope

RMTP v0.4 covers:

1. Parent-child lineage verification.
2. Multi-generation ancestry tracking.
3. Replication depth limits.
4. Descendant population limits.
5. Shared replication budget accounting.
6. Explicit delegation references.
7. Propagation boundary enforcement.
8. Descendant containment.
9. Cross-plan lineage consistency.
10. Evidence-based propagation verification.

## 3. Core Principles

### 3.1 No Implicit Authority Inheritance

An offspring MUST NOT inherit replication authority merely because its parent possessed such authority.

A descendant replication proposal requires independent authority evaluation under v0.2.

### 3.2 Necessity Does Not Expand Authority

A verified structural deficit MAY justify a replication proposal.

It MUST NOT automatically increase permitted replication depth, instance count, or resource budgets.

### 3.3 Bounded Propagation

Every permitted descendant replication chain MUST remain within explicitly defined propagation boundaries.

Unknown or unverified boundaries MUST NOT support a PASS decision.

### 3.4 Traceable Ancestry

Every descendant MUST have a verifiable lineage relationship to its originating replication plan.

A missing or contradictory ancestry record MUST NOT be silently accepted.

### 3.5 No Automatic Descendant Execution

Propagation verification establishes structural conformance only.

It MUST NOT authorize deployment or execution.

## 4. New Data Objects

### 4.1 Replication Lineage Graph

Schema:

schemas/replication-lineage-graph-v0.4.schema.json

Purpose:

Represent the ancestry of replicated agents across multiple generations.

Core fields:

- schema_version
- graph_id
- root_agent_id
- nodes
- edges
- verification_time

Each node identifies an agent instance and its relevant plan.

Each parent-child edge identifies a claimed replication relationship.

Semantic validation MUST reject:

- Self-parenting
- Duplicate node identifiers
- Unknown edge endpoints
- Multiple parents for one offspring
- Cyclic ancestry
- Conflicting parent references
- Unverified ancestry used for approval

An agent MAY participate in multiple work relationships, but replication ancestry MUST remain unambiguous within a given lineage graph.

### 4.2 Replication Propagation Envelope

Schema:

schemas/replication-propagation-envelope-v0.4.schema.json

Purpose:

Define the maximum permitted propagation scope.

Core fields:

- schema_version
- envelope_id
- root_agent_id
- authority_ref
- allowed_scope
- max_depth
- max_total_descendants
- max_active_descendants
- valid_from
- valid_until
- verification_reference

The propagation envelope is a constraint record.

It is not an execution authorization.

The envelope MUST be independently issued and verified.

### 4.3 Replication Budget Ledger

Schema:

schemas/replication-budget-ledger-v0.4.schema.json

Purpose:

Record shared descendant allocations under a propagation envelope.

Core fields:

- schema_version
- ledger_id
- propagation_envelope_ref
- budget_limit
- allocations
- verification_time

Each allocation identifies:

- allocation_id
- plan_ref
- parent_agent_id
- reserved_instances
- active_instances
- released_instances
- allocation_status

The ledger MUST distinguish reserved capacity from active capacity.

Each allocation MUST remain attributable to a specific plan.

Budget capacity MUST NOT be reused until the required release evidence is verified.

A claimed release without valid v0.3 retirement evidence MUST NOT replenish the available budget.

### 4.4 Replication Propagation Verification Bundle

Schema:

schemas/replication-propagation-bundle-v0.4.schema.json

Purpose:

Collect verification results for lineage, propagation authority, and shared budget constraints.

Core fields:

- schema_version
- bundle_id
- lineage_graph_ref
- propagation_envelope_ref
- budget_ledger_ref
- candidate_plan_ref
- verification_time
- lineage_result
- boundary_result
- budget_result
- overall_result
- execution_authorized

Results use:

- PASS
- FAIL
- HELD

The overall result MUST follow the priority:

FAIL > HELD > PASS

A PASS result requires all component results to be PASS.

execution_authorized MUST always be false.

## 5. Lineage Semantics

A replication lineage is a directed ancestry graph.

Example:

    Agent A
       |
       +-- Agent B
       |      |
       |      +-- Agent D
       |
       +-- Agent C

A is the root.

B and C are first-generation descendants.

D is a second-generation descendant.

The depth of the root is zero.

Every child has depth:

    depth(child) = depth(parent) + 1

The lineage graph MUST be acyclic.

Each non-root descendant MUST have exactly one verified replication parent.

Cross-plan ancestry MUST reference the originating plan of the relevant offspring.

## 6. Propagation Depth

max_depth defines the greatest permitted generation distance from the root.

Example:

    max_depth = 2

Permitted:

    A -> B -> D

Not permitted:

    A -> B -> D -> E

A descendant whose proposed depth exceeds max_depth MUST NOT receive a PASS propagation decision.

An unknown depth MUST result in HELD or FAIL according to the available evidence.

## 7. Descendant Population

max_total_descendants limits the number of distinct descendants admitted into the lineage under the specified envelope.

max_active_descendants limits the number of descendants concurrently active or otherwise consuming an active population slot.

A retired descendant MAY stop counting against the active limit only after relevant retirement verification.

Retirement does not erase ancestry.

Therefore:

- Total descendant history is append-only.
- Active descendant count may decrease.
- Retired identities remain traceable.
- An old identity MUST NOT be reused to bypass a total-descendant limit.

## 8. Replication Budget Accounting

The ledger MUST maintain the following constraints:

    0 <= active_instances
    0 <= reserved_instances
    0 <= released_instances

For each allocation, the meaning of each counter MUST be explicit.

Version 0.4 uses the following accounting model:

    committed = reserved_instances + active_instances

    available = budget_limit - SUM(committed)

released_instances is a cumulative audit counter.

It MUST NOT be added again to available capacity.

Transitions from active to released MUST be supported by retirement evidence.

Reservations MUST be uniquely identified.

Overlapping allocations MUST NOT spend the same available capacity more than once.

The ledger is a conformance representation and is not a transactional database.

Actual atomic budget enforcement is the responsibility of an external controller.

## 9. Delegated Replication Requests

An offspring MAY submit a new Replication Intent.

That request MUST undergo the applicable v0.1 and v0.2 verification flow.

If delegated authority is used:

1. The delegation chain MUST be explicit.
2. Every issuer MUST have delegation authority.
3. The descendant's permitted scope MUST NOT exceed its delegation.
4. The descendant's instance limit MUST NOT exceed applicable bounds.
5. The delegated authority MUST remain valid at the verification time.
6. The propagation envelope MUST independently permit the requested depth and population.

A parent agent's authority reference MUST NOT, by itself, establish a valid delegation.

## 10. Propagation Verification

The propagation bundle combines:

- Lineage verification
- Boundary verification
- Budget verification

A PASS decision requires:

    lineage_result == PASS
    AND
    boundary_result == PASS
    AND
    budget_result == PASS

A known violation in any component requires FAIL.

An unresolved component without a known violation requires HELD.

A successful bundle only confirms compliance with the represented propagation constraints.

It MUST NOT be treated as deployment permission.

## 11. Containment and Descendants

A parent agent may become compromised, revoked, or retired.

Its descendants MUST NOT automatically be assumed terminated.

A propagation containment assessment MUST identify:

- Affected descendants
- Applicable authority relationships
- Current lifecycle states
- Existing revocation records
- Retirement verification status
- Unresolved instances

Descendants with independent authority MUST be evaluated against the applicable policies rather than silently revoked solely because of ancestry.

Descendants dependent on revoked authority MUST NOT continue using that revoked authorization.

Containment actions remain the responsibility of independently authorized external controllers.

## 12. Failure and Recovery

A replication chain may partially fail.

Example:

    Root A
      |
      +-- B: retired
      |
      +-- C: active
             |
             +-- D: termination unconfirmed

The graph MUST retain D as an unresolved descendant.

A missing or unverified retirement receipt MUST NOT free D's active-budget allocation.

Recovery MAY be initiated under RMTP v0.3.

Recovery MUST NOT silently create replacement descendants.

A replacement requires a new replication decision and applicable authority verification.

## 13. Temporal Integrity

Propagation verification MUST distinguish:

- Authority validity time
- Lineage event time
- Budget reservation time
- Deployment observation time
- Retirement verification time
- Propagation bundle verification time

A historical PASS result does not imply continued authorization after an envelope expires or is revoked.

Budget availability MUST be assessed using a consistent, verifiable ledger snapshot.

Delayed or conflicting updates MUST NOT be silently counted as available capacity.

## 14. New Core Invariants

### RMTP-INV-027 — No Implicit Delegation

A descendant MUST NOT acquire replication authority solely through parentage.

### RMTP-INV-028 — Acyclic Lineage

Replication ancestry MUST NOT contain cycles.

### RMTP-INV-029 — Bounded Depth

A descendant proposal MUST NOT exceed the verified propagation depth limit.

### RMTP-INV-030 — Bounded Population

Total and active descendant limits MUST be respected.

### RMTP-INV-031 — Budget Conservation

Reserved and active allocations MUST NOT exceed the applicable shared budget.

### RMTP-INV-032 — Verified Release

Budget allocations MUST NOT be reclaimed from unverified retirement claims.

### RMTP-INV-033 — Descendant Trace Continuity

Descendant identities and plan references MUST remain consistent across lineage, lifecycle, and budget records.

### RMTP-INV-034 — No Propagation-Based Execution Authority

Propagation verification MUST NOT grant execution authorization.

### RMTP-INV-035 — No Silent Descendant Containment

Revocation or retirement of an ancestor MUST NOT be treated as proof of descendant termination.

### RMTP-INV-036 — Fail-Closed Boundary Verification

Unknown, expired, contradictory, or unverified propagation boundaries MUST NOT produce PASS.

## 15. Threat Model

RMTP v0.4 considers:

- Recursive replication without delegated authority
- Hidden descendants
- Lineage cycles
- Forged ancestry
- Duplicate descendant identities
- Depth-limit bypass
- Population-limit bypass
- Double-spent replication budgets
- Premature resource-budget release
- Stale budget snapshots
- Cross-plan identity substitution
- Authority laundering through child agents
- False descendant containment claims

Schema validity alone does not eliminate these threats.

Independent authority, integrity verification, atomic resource controls, and trusted observations remain necessary.

## 16. Conformance

A conforming v0.4 fixture MUST:

1. Validate all applicable schemas.
2. Preserve the v0.1–v0.3 verification behavior.
3. Check ancestry node and edge consistency.
4. Reject cyclic or ambiguous lineage.
5. Verify generation depth.
6. Check total and active descendant bounds.
7. Reconcile budget allocations without double counting.
8. Reject unverified budget release.
9. Check applicable delegation and authority references.
10. Ensure the propagation bundle does not authorize execution.
11. Match its expected PASS or FAIL result.

Synthetic fixtures MUST be identified as test data.

## 17. Out of Scope

RMTP v0.4 does not implement:

- Agent deployment
- Distributed scheduling
- Atomic distributed transactions
- Cryptographic identity infrastructure
- External authority issuance
- Runtime enforcement of budgets
- Automatic descendant termination
- Resource orchestration
- Cross-organization trust federation

These responsibilities belong to external systems.

## 18. Final Statement

RMTP v0.1 evaluates replication necessity.

RMTP v0.2 verifies evidence and authority.

RMTP v0.3 verifies lifecycle and retirement.

RMTP v0.4 verifies that replication chains remain bounded, traceable, and independently authorized.

The governing principle is:

**Replication may propagate as a proposal, but authority does not propagate automatically.**
