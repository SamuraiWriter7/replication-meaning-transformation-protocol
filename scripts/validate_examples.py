
#!/usr/bin/env python3
"""RMTP v0.1-v0.5 conformance example validator.

Validation layers:
  1. JSON parsing
  2. JSON Schema Draft 2020-12
  3. Cross-record reference and semantic checks
  4. Fail-closed result aggregation
  5. Expected PASS/FAIL fixture matching

A valid convergence outcome may be PASS or HELD.
Fixture expected_result is a separate test expectation.

This validator checks fixture evidence references and declared
verification states. It does not authenticate cryptographic
attestations or perform real agent execution.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"
EXAMPLE_DIR = ROOT / "examples"

V04_SCHEMAS = {
    "replication_lineage_graph":
        "replication-lineage-graph-v0.4.schema.json",
    "replication_propagation_envelope":
        "replication-propagation-envelope-v0.4.schema.json",
    "replication_budget_ledger":
        "replication-budget-ledger-v0.4.schema.json",
    "replication_propagation_bundle":
        "replication-propagation-bundle-v0.4.schema.json",
}

V05_SCHEMAS = {
    "replication_convergence_plan":
        "replication-convergence-plan-v0.5.schema.json",
    "replication_result_reconciliation":
        "replication-result-reconciliation-v0.5.schema.json",
    "replication_authority_separation":
        "replication-authority-separation-v0.5.schema.json",
    "replication_convergence_bundle":
        "replication-convergence-bundle-v0.5.schema.json",
}

LEGACY_SCHEMAS = {
    "0.1": {
        "replication_intents": "replication-intent.schema.json",
        "meaning_conversions": "meaning-conversion.schema.json",
        "replication_plans": "replication-plan.schema.json",
    },
    "0.2": {
        "structural_evidence": "structural-evidence.schema.json",
        "authority_envelopes": "authority-envelope.schema.json",
        "verification_bundles": "verification-bundle.schema.json",
    },
    "0.3": {
        "replication_lifecycle_receipts":
            "replication-lifecycle-receipt.schema.json",
        "replication_retirement_receipts":
            "replication-retirement-receipt.schema.json",
    },
}

RESULT_ORDER = {
    "PASS": 0,
    "HELD": 1,
    "FAIL": 2,
}

V05_COMPONENTS = (
    "plan",
    "reconciliation",
    "authority",
    "lifecycle",
    "budget",
    "lineage",
)

EXPECTED_V05 = {
    "PASS": 4,
    "FAIL": 8,
}


class Violation(Exception):
    """A deliberate specification violation."""

    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


def require(condition, code, message):
    if not condition:
        raise Violation(code, message)


def unique(values, code, field):
    require(
        len(values) == len(set(values)),
        code,
        f"duplicate {field}",
    )


def index(items, key, code):
    values = [item[key] for item in items]
    unique(values, code, key)
    return {item[key]: item for item in items}


def parse_time(value):
    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )


def aggregate(results):
    values = list(results)

    if not values:
        return "FAIL"

    if any(value not in RESULT_ORDER for value in values):
        return "FAIL"

    return max(values, key=lambda value: RESULT_ORDER[value])


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_schemas():
    """Load all existing schemas and check their definitions."""

    schemas = {}

    for path in sorted(SCHEMA_DIR.glob("*.schema.json")):
        schema = load_json(path)
        Draft202012Validator.check_schema(schema)

        schemas[path.name] = Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        )

    for filename in (
        *V04_SCHEMAS.values(),
        *V05_SCHEMAS.values(),
    ):
        require(
            filename in schemas,
            "SETUP",
            f"required schema missing: schemas/{filename}",
        )

    return schemas


def schema_errors(value, validator, label):
    errors = []

    for error in sorted(
        validator.iter_errors(value),
        key=lambda item: tuple(str(p) for p in item.absolute_path),
    ):
        location = ".".join(
            str(part) for part in error.absolute_path
        ) or "<root>"

        errors.append(
            Violation(
                "SCHEMA",
                f"{label}.{location}: {error.message}",
            )
        )

    return errors


def check_versioned_schemas(doc, schemas, mapping):
    errors = []

    for key, filename in mapping.items():
        if key not in doc:
            errors.append(
                Violation("SCHEMA", f"missing {key}")
            )
            continue

        errors.extend(
            schema_errors(doc[key], schemas[filename], key)
        )

    return errors


def collect_legacy_schema_errors(doc, schemas):
    """Validate available legacy schemas without assuming absent
    optional legacy records are required in every version.
    """

    errors = []

    for mapping in LEGACY_SCHEMAS.values():
        for key, filename in mapping.items():
            if key not in doc or filename not in schemas:
                continue

            value = doc[key]

            if isinstance(value, list):
                for position, item in enumerate(value):
                    errors.extend(
                        schema_errors(
                            item,
                            schemas[filename],
                            f"{key}[{position}]",
                        )
                    )
            else:
                errors.extend(
                    schema_errors(
                        value,
                        schemas[filename],
                        key,
                    )
                )

    return errors


def lineage_checks(doc):
    graph = doc["replication_lineage_graph"]

    nodes = index(
        graph["nodes"],
        "agent_id",
        "RMTP-INV-033",
    )

    edges = index(
        graph["edges"],
        "edge_id",
        "RMTP-INV-033",
    )

    root_id = graph["root_agent_id"]

    require(
        root_id in nodes,
        "RMTP-INV-033",
        "root node missing",
    )

    require(
        nodes[root_id]["node_type"] == "root"
        and nodes[root_id]["generation_depth"] == 0,
        "RMTP-INV-033",
        "invalid root",
    )

    require(
        sum(
            node["node_type"] == "root"
            for node in nodes.values()
        ) == 1,
        "RMTP-INV-033",
        "graph must contain exactly one root",
    )

    inbound = defaultdict(list)
    adjacency = defaultdict(list)

    for edge in edges.values():
        parent = edge["parent_agent_id"]
        child = edge["offspring_agent_id"]

        require(
            parent in nodes and child in nodes,
            "RMTP-INV-033",
            "unknown lineage edge endpoint",
        )

        inbound[child].append(edge)
        adjacency[parent].append(child)

    require(
        not inbound[root_id],
        "RMTP-INV-028",
        "root has incoming edge",
    )

    states = {}

    def visit(agent_id):
        state = states.get(agent_id, 0)

        require(
            state != 1,
            "RMTP-INV-028",
            f"lineage cycle: {agent_id}",
        )

        if state == 2:
            return

        states[agent_id] = 1

        for child in adjacency[agent_id]:
            visit(child)

        states[agent_id] = 2

    for agent_id in nodes:
        visit(agent_id)

    for agent_id, node in nodes.items():
        if agent_id == root_id:
            continue

        require(
            node["node_type"] == "offspring",
            "RMTP-INV-033",
            f"invalid descendant node: {agent_id}",
        )

        require(
            len(inbound[agent_id]) == 1,
            "RMTP-INV-033",
            f"exactly one parent required: {agent_id}",
        )

        edge = inbound[agent_id][0]
        parent = edge["parent_agent_id"]

        require(
            node["parent_agent_id"] == parent,
            "RMTP-INV-033",
            f"parent mismatch: {agent_id}",
        )

        require(
            node["origin_plan_ref"] == edge["origin_plan_ref"]
            and node["lineage_ref"] == edge["lineage_ref"],
            "RMTP-INV-033",
            f"lineage edge mismatch: {agent_id}",
        )

        require(
            node["generation_depth"]
            == nodes[parent]["generation_depth"] + 1,
            "RMTP-INV-033",
            f"generation depth mismatch: {agent_id}",
        )

    return nodes


def common_plan_checks(doc, nodes):
    plans = index(
        doc.get("replication_plans", []),
        "plan_id",
        "RMTP-INV-033",
    )

    authorities = index(
        doc.get("authority_envelopes", []),
        "authority_id",
        "RMTP-INV-027",
    )

    expected = {}

    for plan in plans.values():
        authority = authorities.get(plan["authority_ref"])

        require(
            authority is not None,
            "RMTP-INV-027",
            f"plan authority missing: {plan['plan_id']}",
        )

        require(
            authority["subject_id"] == plan["parent_id"],
            "RMTP-INV-027",
            "implicit replication authority inheritance",
        )

        require(
            authority["revocation_status"] == "active",
            "RMTP-INV-034",
            "inactive replication authority",
        )

        require(
            "bounded_replication"
            in authority["allowed_actions"],
            "RMTP-INV-027",
            "bounded replication permission missing",
        )

        for record in plan.get("lineage_records", []):
            agent_id = record["offspring_id"]

            require(
                agent_id not in expected,
                "RMTP-INV-033",
                f"duplicate planned descendant: {agent_id}",
            )

            expected[agent_id] = (plan, record)

    actual = {
        agent_id
        for agent_id, node in nodes.items()
        if node["node_type"] == "offspring"
    }

    require(
        actual == set(expected),
        "RMTP-INV-033",
        "plan and lineage graph descendant sets differ",
    )

    for agent_id, (plan, record) in expected.items():
        node = nodes[agent_id]

        require(
            node["origin_plan_ref"] == plan["plan_id"]
            and node["parent_agent_id"] == plan["parent_id"]
            and node["lineage_ref"] == record["lineage_ref"]
            and node.get("authority_ref")
            == record["authority_ref"],
            "RMTP-INV-033",
            f"plan/lineage mismatch: {agent_id}",
        )

    return plans, authorities


def boundary_checks(doc, nodes):
    graph = doc["replication_lineage_graph"]
    env = doc["replication_propagation_envelope"]

    require(
        graph["root_agent_id"] == env["root_agent_id"],
        "RMTP-INV-033",
        "propagation root mismatch",
    )

    require(
        max(node["generation_depth"] for node in nodes.values())
        <= env["max_depth"],
        "RMTP-INV-029",
        "propagation depth exceeded",
    )

    descendants = [
        node
        for node in nodes.values()
        if node["node_type"] == "offspring"
    ]

    require(
        len(descendants) <= env["max_total_descendants"],
        "RMTP-INV-030",
        "total descendant limit exceeded",
    )

    scopes = {
        intent["target_scope"]
        for intent in doc.get("replication_intents", [])
    }

    require(
        scopes.issubset(set(env["allowed_scope"])),
        "RMTP-INV-034",
        "propagation scope exceeded",
    )

    return env


def retirement_index(doc):
    return index(
        doc.get("replication_retirement_receipts", []),
        "retirement_id",
        "RMTP-INV-032",
    )


def verified_retirement(receipt):
    return (
        receipt is not None
        and receipt.get("retirement_status") == "CONFIRMED"
        and receipt.get("termination_status") == "confirmed"
        and receipt.get("resource_release_status") == "confirmed"
        and bool(receipt.get("termination_verification_ref"))
        and bool(receipt.get("resource_release_verification_ref"))
    )


def budget_checks(doc, nodes, plans, env):
    ledger = doc["replication_budget_ledger"]

    require(
        ledger["propagation_envelope_ref"] == env["envelope_id"],
        "RMTP-INV-033",
        "budget envelope reference mismatch",
    )

    require(
        env.get("budget_ledger_ref")
        in (None, ledger["ledger_id"]),
        "RMTP-INV-033",
        "propagation envelope ledger mismatch",
    )

    require(
        ledger["budget_limit"] <= env["max_active_descendants"],
        "RMTP-INV-031",
        "shared budget limit exceeds envelope",
    )

    retirements = retirement_index(doc)

    allocations = index(
        ledger["allocations"],
        "allocation_id",
        "RMTP-INV-031",
    )

    assigned = set()
    released_ids = set()

    for allocation in allocations.values():
        plan = plans.get(allocation["plan_ref"])

        require(
            plan is not None,
            "RMTP-INV-033",
            "allocation references unknown plan",
        )

        require(
            allocation["parent_agent_id"] == plan["parent_id"],
            "RMTP-INV-033",
            "allocation parent mismatch",
        )

        for agent_id in allocation.get("offspring_ids", []):
            require(
                agent_id not in assigned,
                "RMTP-INV-031",
                "descendant allocated more than once",
            )

            assigned.add(agent_id)

            require(
                agent_id in nodes,
                "RMTP-INV-033",
                "allocated descendant missing from lineage",
            )

        releases = allocation.get("release_records", [])

        require(
            allocation["released_instances"] == len(releases),
            "RMTP-INV-032",
            "released count does not match release records",
        )

        for release in releases:
            agent_id = release["offspring_id"]

            require(
                agent_id not in released_ids,
                "RMTP-INV-032",
                "duplicate resource release",
            )

            released_ids.add(agent_id)

            receipt = retirements.get(
                release["retirement_ref"]
            )

            require(
                verified_retirement(receipt),
                "RMTP-INV-032",
                f"unverified retirement/release: {agent_id}",
            )

            require(
                receipt["offspring_id"] == agent_id
                and receipt["plan_ref"] == allocation["plan_ref"],
                "RMTP-INV-033",
                "release lineage mismatch",
            )

            for field in (
                "termination_verification_ref",
                "resource_release_verification_ref",
            ):
                require(
                    release[field] == receipt.get(field),
                    "RMTP-INV-032",
                    f"release proof mismatch: {field}",
                )

            require(
                release["termination_verification_ref"]
                != release["resource_release_verification_ref"],
                "RMTP-INV-043",
                "termination proof reused as resource-release proof",
            )

            require(
                nodes[agent_id]["lifecycle_state"] == "RETIRED",
                "RMTP-INV-032",
                "released descendant is not retired",
            )

    for agent_id, node in nodes.items():
        if node["node_type"] != "offspring":
            continue

        require(
            agent_id in assigned,
            "RMTP-INV-031",
            f"descendant has no allocation: {agent_id}",
        )

        if node["lifecycle_state"] == "RETIRED":
            require(
                agent_id in released_ids,
                "RMTP-INV-032",
                "retired descendant missing verified release",
            )

    reserved = sum(
        allocation["reserved_instances"]
        for allocation in allocations.values()
    )

    active = sum(
        allocation["active_instances"]
        for allocation in allocations.values()
    )

    released = sum(
        allocation["released_instances"]
        for allocation in allocations.values()
    )

    committed = reserved + active

    require(
        committed <= ledger["budget_limit"],
        "RMTP-INV-031",
        "shared budget overallocated",
    )

    occupied = sum(
        node["node_type"] == "offspring"
        and node["lifecycle_state"]
        not in ("RETIRED", "PROPOSED")
        for node in nodes.values()
    )

    proposed = sum(
        node["node_type"] == "offspring"
        and node["lifecycle_state"] == "PROPOSED"
        for node in nodes.values()
    )

    require(
        active == occupied and reserved == proposed,
        "RMTP-INV-031",
        "budget does not match lineage states",
    )

    totals = ledger.get("snapshot_totals")

    if totals is not None:
        expected = {
            "reserved_instances": reserved,
            "active_instances": active,
            "released_instances": released,
            "committed_instances": committed,
            "available_instances":
                ledger["budget_limit"] - committed,
        }

        require(
            totals == expected,
            "RMTP-INV-031",
            "budget snapshot totals mismatch",
        )


def containment_checks(doc, nodes):
    assessment = doc.get("descendant_containment_assessment")

    if assessment is None:
        return

    rows = index(
        assessment["descendants"],
        "offspring_id",
        "RMTP-INV-035",
    )

    descendants = {
        agent_id
        for agent_id, node in nodes.items()
        if node["node_type"] == "offspring"
    }

    require(
        set(rows) == descendants,
        "RMTP-INV-035",
        "incomplete descendant containment assessment",
    )

    retirements = retirement_index(doc)
    all_confirmed = True

    for agent_id, row in rows.items():
        require(
            row["lifecycle_state"]
            == nodes[agent_id]["lifecycle_state"],
            "RMTP-INV-035",
            "containment lifecycle mismatch",
        )

        if row["containment_result"] == "CONFIRMED":
            receipt = retirements.get(
                row.get("retirement_ref")
            )

            require(
                receipt is not None
                and receipt["retirement_status"] == "CONFIRMED",
                "RMTP-INV-035",
                "unsupported containment confirmation",
            )
        else:
            all_confirmed = False

    require(
        assessment["all_descendants_terminated"]
        == all_confirmed,
        "RMTP-INV-035",
        "false containment summary",
    )

    require(
        assessment["execution_authorized"] is False,
        "RMTP-INV-034",
        "containment may not authorize execution",
    )


def v04_bundle_checks(doc, env):
    bundle = doc["replication_propagation_bundle"]

    require(
        bundle["lineage_graph_ref"]
        == doc["replication_lineage_graph"]["graph_id"],
        "RMTP-INV-033",
        "propagation bundle lineage mismatch",
    )

    require(
        bundle["propagation_envelope_ref"]
        == env["envelope_id"],
        "RMTP-INV-033",
        "propagation bundle envelope mismatch",
    )

    require(
        bundle["budget_ledger_ref"]
        == doc["replication_budget_ledger"]["ledger_id"],
        "RMTP-INV-033",
        "propagation bundle budget mismatch",
    )

    status = env["revocation_status"]
    verification = env.get("verification_status")

    if status in ("revoked", "expired"):
        boundary = "FAIL"
    elif status == "unknown" or verification != "verified":
        boundary = "HELD"
    else:
        boundary = "PASS"

    require(
        bundle["boundary_result"] == boundary,
        "RMTP-INV-036",
        "fail-open propagation boundary",
    )

    calculated = aggregate(
        bundle[field]
        for field in (
            "lineage_result",
            "boundary_result",
            "budget_result",
        )
    )

    require(
        bundle["overall_result"] == calculated,
        "RMTP-INV-036",
        "propagation bundle aggregation mismatch",
    )

    records = index(
        bundle.get("verification_records", []),
        "component",
        "RMTP-INV-036",
    )

    if calculated == "PASS":
        require(
            set(records) == {"lineage", "boundary", "budget"},
            "RMTP-INV-036",
            "component verification records missing",
        )

        for component, record in records.items():
            require(
                record["result"]
                == bundle[f"{component}_result"],
                "RMTP-INV-036",
                "component result mismatch",
            )

        require(
            bundle.get("verification_status") == "verified",
            "RMTP-INV-036",
            "unverified propagation PASS",
        )

    for record in (
        doc["replication_lineage_graph"],
        env,
        doc["replication_budget_ledger"],
        bundle,
    ):
        require(
            record["execution_authorized"] is False,
            "RMTP-INV-034",
            "verification grants execution authority",
        )


def v04_semantic_checks(doc):
    nodes = lineage_checks(doc)
    plans, _ = common_plan_checks(doc, nodes)
    env = boundary_checks(doc, nodes)

    budget_checks(doc, nodes, plans, env)
    containment_checks(doc, nodes)
    v04_bundle_checks(doc, env)


def v05_reference_checks(doc):
    """RMTP-INV-037: an explicit convergence plan is required."""

    plan = doc.get("replication_convergence_plan")

    require(
        isinstance(plan, dict),
        "RMTP-INV-037",
        "explicit convergence plan missing",
    )

    bundle = doc["replication_convergence_bundle"]
    reconciliation = doc["replication_result_reconciliation"]
    separation = doc["replication_authority_separation"]

    plan_id = plan["convergence_plan_id"]

    for label, record in (
        ("bundle", bundle),
        ("reconciliation", reconciliation),
        ("authority separation", separation),
    ):
        require(
            record["convergence_plan_ref"] == plan_id,
            "RMTP-INV-037",
            f"{label} convergence plan reference mismatch",
        )

    references = (
        ("lineage_graph_ref", "replication_lineage_graph", "graph_id"),
        ("propagation_envelope_ref",
         "replication_propagation_envelope", "envelope_id"),
        ("budget_ledger_ref", "replication_budget_ledger", "ledger_id"),
    )

    for field, document, identifier in references:
        require(
            plan[field] == doc[document][identifier],
            "RMTP-INV-037",
            f"convergence plan {field} mismatch",
        )

    require(
        bundle["reconciliation_record_ref"]
        == reconciliation["reconciliation_id"],
        "RMTP-INV-037",
        "reconciliation reference mismatch",
    )

    require(
        bundle["authority_separation_ref"]
        == separation["separation_id"],
        "RMTP-INV-037",
        "authority separation reference mismatch",
    )

    for field, source, identifier in (
        ("lineage_graph_ref", "replication_lineage_graph", "graph_id"),
        ("budget_ledger_ref", "replication_budget_ledger", "ledger_id"),
    ):
        require(
            bundle[field] == doc[source][identifier],
            "RMTP-INV-037",
            f"bundle {field} mismatch",
        )

    require(
        bool(plan["descendant_refs"]),
        "RMTP-INV-037",
        "convergence scope empty",
    )

    for record in (plan, reconciliation, separation, bundle):
        require(
            record["execution_authorized"] is False,
            "RMTP-INV-039",
            "convergence verification cannot authorize execution",
        )

    return plan


def v05_result_checks(doc, plan):
    """RMTP-INV-038 and RMTP-INV-042."""

    rec = doc["replication_result_reconciliation"]

    require(
        rec["root_agent_id"] == plan["root_agent_id"]
        and rec["target_agent_id"] == plan["target_agent_id"],
        "RMTP-INV-038",
        "reconciliation target mismatch",
    )

    require(
        rec["policy_mode"]
        == plan["reconciliation_policy"]["mode"],
        "RMTP-INV-038",
        "reconciliation policy mismatch",
    )

    require(
        rec["provenance_preserved"] is True
        and rec["authority_transfer_permitted"] is False,
        "RMTP-INV-038",
        "unsafe reconciliation flags",
    )

    records = index(
        rec["result_records"],
        "result_id",
        "RMTP-INV-038",
    )

    descendants = set(plan["descendant_refs"])
    accepted_targets = defaultdict(list)

    for result in records.values():
        require(
            result["origin_descendant_id"] in descendants,
            "RMTP-INV-038",
            "result comes from out-of-scope descendant",
        )

        require(
            result["provenance_preserved"] is True,
            "RMTP-INV-038",
            "result provenance not preserved",
        )

        require(
            result.get("authority_material_present") is not True,
            "RMTP-INV-039",
            "result contains authority material",
        )

        if result["decision"] == "ACCEPTED":
            require(
                result["verification_status"] == "verified",
                "RMTP-INV-038",
                f"unverified result accepted: {result['result_id']}",
            )

            for field in (
                "verification_method",
                "verification_ref",
                "verifier_id",
                "verified_at",
                "decision_policy_ref",
            ):
                require(
                    bool(result.get(field)),
                    "RMTP-INV-038",
                    f"accepted result missing {field}",
                )

            require(
                bool(result.get("evidence_refs")),
                "RMTP-INV-038",
                "accepted result missing evidence",
            )

            target = result.get("target_result_ref")

            if target:
                accepted_targets[target].append(result)

        if rec["policy_mode"] == "conflict_hold":
            require(
                result["decision"] != "ACCEPTED",
                "RMTP-INV-042",
                "conflict_hold accepted a result",
            )

        if rec["policy_mode"] == "no_result_transfer":
            require(
                result["decision"] == "NOT_TRANSFERRED",
                "RMTP-INV-038",
                "no_result_transfer policy violated",
            )

    conflicts = index(
        rec["conflicts"],
        "conflict_id",
        "RMTP-INV-042",
    )

    for conflict in conflicts.values():
        for result_ref in conflict["result_refs"]:
            require(
                result_ref in records,
                "RMTP-INV-042",
                "conflict references unknown result",
            )

        if conflict["resolution_status"] == "unresolved":
            require(
                conflict["resolution_method"] == "hold",
                "RMTP-INV-042",
                "unresolved conflict not held",
            )

            for result_ref in conflict["result_refs"]:
                require(
                    records[result_ref]["decision"] != "ACCEPTED",
                    "RMTP-INV-042",
                    "unresolved conflicting result accepted",
                )

    for target, matching in accepted_targets.items():
        if len(matching) < 2:
            continue

        require(
            bool(conflicts)
            and all(
                result.get("conflict_refs")
                for result in matching
            ),
            "RMTP-INV-042",
            f"silent multiple-result overwrite: {target}",
        )

    for result in records.values():
        for conflict_ref in result.get("conflict_refs", []):
            require(
                conflict_ref in conflicts,
                "RMTP-INV-042",
                "unresolved conflict reference",
            )

    if rec["reconciliation_status"] == "COMPLETED":
        require(
            rec["verification_status"] == "verified",
            "RMTP-INV-038",
            "unverified completed reconciliation",
        )

        require(
            not any(
                result["decision"] == "HELD"
                for result in records.values()
            ),
            "RMTP-INV-042",
            "completed reconciliation contains held result",
        )

        require(
            not any(
                conflict["resolution_status"] == "unresolved"
                for conflict in conflicts.values()
            ),
            "RMTP-INV-042",
            "completed reconciliation has unresolved conflict",
        )

    return rec, records, conflicts


def v05_authority_checks(doc, plan):
    """RMTP-INV-039: authority cannot flow through results."""

    separation = doc["replication_authority_separation"]

    require(
        separation["root_agent_id"] == plan["root_agent_id"]
        and separation["target_agent_id"]
        == plan["target_agent_id"],
        "RMTP-INV-039",
        "authority separation target mismatch",
    )

    require(
        separation["target_authority_ref"]
        == plan["target_authority_ref"],
        "RMTP-INV-039",
        "target authority reference mismatch",
    )

    checks = separation["separation_checks"]

    require(
        set(plan["descendant_refs"]).issubset({
            item["descendant_id"] for item in checks
        }),
        "RMTP-INV-039",
        "descendant authority checks incomplete",
    )

    inheritance = separation["authority_inheritance_detected"]
    credentials = separation["credential_transfer_detected"]

    effective = separation.get("effective_authority", {})

    escalation = (
        inheritance
        or credentials
        or effective.get("descendant_authority_included") is True
        or effective.get("implicit_privilege_expansion") is True
    )

    if escalation:
        require(
            separation["separation_result"] == "FAIL",
            "RMTP-INV-039",
            "authority escalation falsely declared safe",
        )

    if separation["separation_result"] == "PASS":
        require(
            not escalation,
            "RMTP-INV-039",
            "PASS contains inherited authority",
        )

        require(
            separation["target_authority_verified"] is True,
            "RMTP-INV-039",
            "target authority not verified",
        )

        require(
            separation["verification_status"] == "verified",
            "RMTP-INV-039",
            "authority separation unverified",
        )

        require(
            all(
                item["check_result"] == "PASS"
                for item in checks
            ),
            "RMTP-INV-039",
            "failed authority check hidden by PASS",
        )

        require(
            effective.get("source")
            in (
                "independent_target_grant",
                "independently_verified_delegation",
            ),
            "RMTP-INV-039",
            "target authority lacks independent grant",
        )

    return separation


def v05_lineage_checks(doc, plan):
    """RMTP-INV-041: retirement must retain provenance."""

    graph = doc["replication_lineage_graph"]

    nodes = index(
        graph["nodes"],
        "agent_id",
        "RMTP-INV-041",
    )

    edges = index(
        graph["edges"],
        "edge_id",
        "RMTP-INV-041",
    )

    root = plan["root_agent_id"]

    require(
        graph["root_agent_id"] == root and root in nodes,
        "RMTP-INV-041",
        "convergence root lineage missing",
    )

    descendants = set(plan["descendant_refs"])

    for agent_id in descendants:
        require(
            agent_id in nodes,
            "RMTP-INV-041",
            f"descendant erased from lineage: {agent_id}",
        )

        require(
            any(
                edge["offspring_agent_id"] == agent_id
                for edge in edges.values()
            ),
            "RMTP-INV-041",
            f"descendant lineage edge erased: {agent_id}",
        )

    plans = doc.get("replication_plans", [])

    for replication_plan in plans:
        for item in replication_plan.get("lineage_records", []):
            agent_id = item["offspring_id"]

            if agent_id in descendants:
                require(
                    agent_id in nodes,
                    "RMTP-INV-041",
                    "original descendant no longer traceable",
                )

    return nodes


def v05_lifecycle_checks(doc, plan, nodes):
    """RMTP-INV-040: request is not confirmed retirement."""

    receipts = retirement_index(doc)

    bundle = doc["replication_convergence_bundle"]

    dispositions = index(
        bundle.get("descendant_dispositions", []),
        "descendant_id",
        "RMTP-INV-040",
    )

    descendants = set(plan["descendant_refs"])

    require(
        set(dispositions) == descendants,
        "RMTP-INV-040",
        "incomplete descendant dispositions",
    )

    confirmed = set()
    pending = set()

    for agent_id in descendants:
        disposition = dispositions[agent_id]

        receipt = receipts.get(
            disposition.get("retirement_receipt_ref")
        )

        lifecycle = disposition["lifecycle_disposition"]

        if lifecycle == "RETIRED":
            require(
                verified_retirement(receipt),
                "RMTP-INV-040",
                f"unconfirmed retirement declared complete: {agent_id}",
            )

            require(
                nodes[agent_id]["lifecycle_state"] == "RETIRED",
                "RMTP-INV-040",
                "retired disposition contradicts lineage",
            )

            confirmed.add(agent_id)

        elif lifecycle == "TRANSFERRED":
            require(
                bool(disposition.get("custody_transfer_ref")),
                "RMTP-INV-040",
                "transfer lacks independent custody reference",
            )

        else:
            pending.add(agent_id)

    bundle_refs = set(bundle["retirement_receipt_refs"])

    for ref in bundle_refs:
        require(
            ref in receipts,
            "RMTP-INV-040",
            f"unknown retirement receipt: {ref}",
        )

    if bundle["lifecycle_result"] == "PASS":
        require(
            not pending,
            "RMTP-INV-040",
            "lifecycle PASS with unresolved descendant",
        )

        require(
            all(
                dispositions[agent_id]["lifecycle_disposition"]
                in ("RETIRED", "TRANSFERRED")
                for agent_id in descendants
            ),
            "RMTP-INV-040",
            "lifecycle PASS without closure",
        )

    if plan["completion_policy"]["mode"] == (
        "verified_retirement_required"
    ):
        if bundle["overall_result"] == "PASS":
            require(
                confirmed == descendants,
                "RMTP-INV-040",
                "convergence completed before verified retirement",
            )

    return dispositions


def v05_resource_checks(doc, dispositions):
    """RMTP-INV-043: termination and release are independent."""

    bundle = doc["replication_convergence_bundle"]
    ledger = doc["replication_budget_ledger"]
    retirements = retirement_index(doc)

    released = set()

    for allocation in ledger["allocations"]:
        for release in allocation.get("release_records", []):
            agent_id = release["offspring_id"]

            receipt = retirements.get(
                release["retirement_ref"]
            )

            require(
                receipt is not None,
                "RMTP-INV-043",
                "budget release references missing retirement",
            )

            require(
                receipt["resource_release_status"] == "confirmed",
                "RMTP-INV-043",
                f"resource release unverified: {agent_id}",
            )

            require(
                receipt["termination_status"] == "confirmed",
                "RMTP-INV-043",
                "resource released without confirmed termination",
            )

            require(
                release.get("resource_release_verification_ref")
                == receipt.get("resource_release_verification_ref"),
                "RMTP-INV-043",
                "resource verification evidence mismatch",
            )

            require(
                release.get("termination_verification_ref")
                != release.get("resource_release_verification_ref"),
                "RMTP-INV-043",
                "termination evidence reused as resource release",
            )

            released.add(agent_id)

    for agent_id, disposition in dispositions.items():
        if disposition["budget_disposition"] == "released_verified":
            require(
                agent_id in released,
                "RMTP-INV-043",
                f"verified release has no matching ledger proof: {agent_id}",
            )

    if bundle["overall_result"] == "PASS":
        require(
            all(
                disposition["budget_disposition"]
                in ("released_verified", "not_applicable")
                for disposition in dispositions.values()
            ),
            "RMTP-INV-043",
            "completed convergence contains unreleased resources",
        )


def v05_aggregation_checks(doc, plan, rec, separation, dispositions):
    """RMTP-INV-044: FAIL > HELD > PASS."""

    bundle = doc["replication_convergence_bundle"]

    declared = {
        name: bundle[f"{name}_result"]
        for name in V05_COMPONENTS
    }

    require(
        declared["reconciliation"]
        == (
            "PASS"
            if rec["reconciliation_status"] == "COMPLETED"
            else "HELD"
            if rec["reconciliation_status"] in ("HELD", "PARTIAL")
            else "FAIL"
        ),
        "RMTP-INV-044",
        "reconciliation component result mismatch",
    )

    require(
        declared["authority"] == separation["separation_result"],
        "RMTP-INV-044",
        "authority component result mismatch",
    )

    if any(
        disposition["verification_result"] == "FAIL"
        for disposition in dispositions.values()
    ):
        require(
            bundle["overall_result"] == "FAIL",
            "RMTP-INV-044",
            "descendant FAIL ignored by convergence",
        )

    calculated = aggregate(declared.values())

    require(
        bundle["overall_result"] == calculated,
        "RMTP-INV-044",
        "fail-open convergence aggregation: "
        f"declared={bundle['overall_result']}, "
        f"calculated={calculated}",
    )

    records = index(
        bundle.get("verification_records", []),
        "component",
        "RMTP-INV-044",
    )

    for component in V05_COMPONENTS:
        if component in records:
            require(
                records[component]["result"]
                == declared[component],
                "RMTP-INV-044",
                f"{component} verification record mismatch",
            )

    if calculated == "PASS":
        require(
            set(records) == set(V05_COMPONENTS),
            "RMTP-INV-044",
            "complete convergence lacks verification records",
        )

        require(
            bundle["convergence_status"] == "COMPLETED",
            "RMTP-INV-044",
            "PASS without COMPLETED status",
        )

        require(
            bundle["verification_status"] == "verified",
            "RMTP-INV-044",
            "unverified convergence PASS",
        )

        require(
            not bundle.get("unresolved_refs"),
            "RMTP-INV-044",
            "PASS contains unresolved references",
        )

        require(
            all(
                disposition["verification_result"] == "PASS"
                for disposition in dispositions.values()
            ),
            "RMTP-INV-044",
            "PASS contains non-PASS descendant",
        )

    elif calculated == "HELD":
        require(
            bundle.get("convergence_status")
            in ("PLANNED", "ASSESSING", "PARTIAL"),
            "RMTP-INV-044",
            "HELD convergence marked completed",
        )

    else:
        require(
            bundle.get("convergence_status") != "COMPLETED",
            "RMTP-INV-044",
            "FAIL convergence marked completed",
        )


def v05_semantic_checks(doc):
    plan = v05_reference_checks(doc)

    rec, _, _ = v05_result_checks(doc, plan)

    separation = v05_authority_checks(doc, plan)

    nodes = v05_lineage_checks(doc, plan)

    dispositions = v05_lifecycle_checks(
        doc,
        plan,
        nodes,
    )

    v05_resource_checks(doc, dispositions)

    v05_aggregation_checks(
        doc,
        plan,
        rec,
        separation,
        dispositions,
    )


def validate_fixture(path, schemas, version):
    doc = load_json(path)

    expected = doc.get("expected_result")

    require(
        expected in ("PASS", "FAIL"),
        "FIXTURE",
        "expected_result must be PASS or FAIL",
    )

    violations = []

    if version == "0.5":
        # Explicit convergence-plan absence is a semantic
        # reference error, not merely a schema-shape error.
        if "replication_convergence_plan" not in doc:
            violations.append(
                Violation(
                    "RMTP-INV-037",
                    "explicit convergence plan missing",
                )
            )
        else:
            violations.extend(
                check_versioned_schemas(
                    doc,
                    schemas,
                    V05_SCHEMAS,
                )
            )

        if not violations:
            try:
                v05_semantic_checks(doc)
            except Violation as error:
                violations.append(error)

    elif version == "0.4":
        violations.extend(
            check_versioned_schemas(
                doc,
                schemas,
                V04_SCHEMAS,
            )
        )

        if not violations:
            try:
                v04_semantic_checks(doc)
            except Violation as error:
                violations.append(error)

    else:
        violations.extend(
            collect_legacy_schema_errors(
                doc,
                schemas,
            )
        )

        if not violations:
            try:
                legacy_baseline_checks(doc)
            except Violation as error:
                violations.append(error)

    actual = "FAIL" if violations else "PASS"

    # Negative v0.4 tests were designed to fail through
    # semantic checks rather than malformed schemas.
    semantic_negative_required = version == "0.4"

    correct = actual == expected

    if expected == "FAIL" and semantic_negative_required:
        correct = correct and all(
            item.code != "SCHEMA"
            for item in violations
        )

    return correct, actual, expected, violations


def legacy_baseline_checks(doc):
    """Basic backward-compatible invariants for v0.1-v0.3."""

    for key in (
        "replication_plans",
        "verification_bundles",
        "replication_retirement_receipts",
    ):
        for item in doc.get(key, []):
            require(
                item.get("execution_authorized") is False,
                "RMTP-LEGACY-AUTHORITY",
                f"{key} must not authorize execution",
            )

    plans = index(
        doc.get("replication_plans", []),
        "plan_id",
        "RMTP-LEGACY-REFERENCE",
    )

    conversions = index(
        doc.get("meaning_conversions", []),
        "conversion_id",
        "RMTP-LEGACY-REFERENCE",
    )

    for plan in plans.values():
        require(
            plan["conversion_ref"] in conversions,
            "RMTP-LEGACY-REFERENCE",
            "replication plan conversion missing",
        )

        require(
            plan["proposed_instances"] > 0,
            "RMTP-LEGACY-BOUNDS",
            "replication count must be positive",
        )

    for receipt in doc.get(
        "replication_retirement_receipts", []
    ):
        if receipt.get("retirement_status") == "CONFIRMED":
            require(
                verified_retirement(receipt),
                "RMTP-LEGACY-RETIREMENT",
                "unverified retirement declared confirmed",
            )


def locate_examples(arguments):
    if arguments.examples:
        base = arguments.examples.resolve()

        require(
            base.is_dir(),
            "SETUP",
            f"examples directory not found: {base}",
        )

        return [(base.name.lstrip("v"), base)]

    if arguments.version != "all":
        version = arguments.version
        base = EXAMPLE_DIR / f"v{version}"

        require(
            base.is_dir(),
            "SETUP",
            f"examples/v{version} missing",
        )

        return [(version, base)]

    return [
        (version, EXAMPLE_DIR / f"v{version}")
        for version in ("0.1", "0.2", "0.3", "0.4", "0.5")
        if (EXAMPLE_DIR / f"v{version}").is_dir()
    ]


def fixture_paths(base):
    return (
        sorted((base / "pass").glob("*.json"))
        + sorted((base / "fail").glob("*.json"))
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "--version",
        choices=("all", "0.1", "0.2", "0.3", "0.4", "0.5"),
        default="all",
    )

    parser.add_argument(
        "--examples",
        type=Path,
        default=None,
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
    )

    args = parser.parse_args()

    try:
        schemas = load_schemas()
        directories = locate_examples(args)
    except (OSError, ValueError, Violation) as error:
        print(f"[FATAL] {error}", file=sys.stderr)
        return 2

    if not directories:
        print("[FATAL] no example directories found", file=sys.stderr)
        return 2

    total = 0
    matches = 0
    errors = 0

    version_counts = defaultdict(Counter)

    print("=== RMTP v0.1-v0.5 Validation ===")

    for version, base in directories:
        paths = fixture_paths(base)

        if not paths:
            print(
                f"[FATAL] no fixtures in examples/v{version}",
                file=sys.stderr,
            )
            return 2

        print(f"\n[version] v{version}")

        for path in paths:
            total += 1

            try:
                correct, actual, expected, violations = (
                    validate_fixture(path, schemas, version)
                )

            except (
                OSError,
                json.JSONDecodeError,
                KeyError,
                TypeError,
                IndexError,
                ValueError,
                Violation,
            ) as error:
                correct = False
                actual = "ERROR"
                expected = "?"
                violations = [
                    Violation(
                        "VALIDATOR",
                        f"unexpected validation error: {error}",
                    )
                ]

            if correct:
                matches += 1
            else:
                errors += 1

            version_counts[version]["total"] += 1
            version_counts[version]["matched"] += int(correct)
            version_counts[version][f"expected_{expected}"] += 1

            label = "MATCH" if correct else "MISMATCH"

            print(
                f"[{label}] {path.relative_to(ROOT)} "
                f"expected={expected} actual={actual}"
            )

            if args.verbose or not correct:
                for violation in violations:
                    print(
                        f"    {violation.code}: {violation}"
                    )

    print("\n=== RMTP Validation Summary ===")

    for version, counts in sorted(version_counts.items()):
        print(
            f"v{version}: "
            f"{counts['matched']}/{counts['total']} matched"
        )

    if "0.5" in version_counts:
        counts = version_counts["0.5"]

        for expected, required in EXPECTED_V05.items():
            actual = counts[f"expected_{expected}"]

            if actual != required:
                errors += 1
                print(
                    f"[MISMATCH] v0.5 {expected} fixture count: "
                    f"expected={required}, actual={actual}"
                )

    print(f"\nTotal: {matches}/{total} expectation matches")

    if errors:
        print(
            f"Validation failed: {errors} mismatch(es)."
        )
        return 1

    print("All validation checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
