
#!/usr/bin/env python3
"""Replication Meaning Transformation Protocol conformance validator.

Supported versions:
    v0.1, v0.2, v0.3: original legacy validator
    v0.4: lineage, propagation, budget and containment
    v0.5: convergence, reconciliation and fail-closed aggregation

Fixture expectations:
    PASS: the example must satisfy the specification.
    FAIL: the example must be rejected by the validator.

A convergence state of HELD is not itself a failed fixture.
It may be a valid outcome within a PASS example.

This validator does not authenticate real cryptographic attestations
or authorize AI agent execution.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys

from collections import defaultdict
from datetime import datetime
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"
EXAMPLE_DIR = ROOT / "examples"

VERSIONS = ("0.1", "0.2", "0.3", "0.4", "0.5")

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

V05_COMPONENTS = (
    "plan",
    "reconciliation",
    "authority",
    "lifecycle",
    "budget",
    "lineage",
)

V05_COUNTS = {
    "PASS": 4,
    "FAIL": 8,
}

RANK = {
    "PASS": 0,
    "HELD": 1,
    "FAIL": 2,
}


class Violation(Exception):
    def __init__(self, code, message):
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

    if any(value not in RANK for value in values):
        return "FAIL"

    return max(values, key=lambda value: RANK[value])


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_schemas():
    schemas = {}

    required = set(V04_SCHEMAS.values())
    required.update(V05_SCHEMAS.values())

    for filename in sorted(required):
        path = SCHEMA_DIR / filename

        require(
            path.is_file(),
            "SETUP",
            f"required schema missing: schemas/{filename}",
        )

        schema = load_json(path)

        Draft202012Validator.check_schema(schema)

        schemas[filename] = Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        )

    return schemas


@lru_cache(maxsize=1)
def load_legacy_validator():
    """Restore the original v0.1-v0.3 conformance engine."""

    path = ROOT / "scripts" / "validate_legacy.py"

    require(
        path.is_file(),
        "SETUP",
        "scripts/validate_legacy.py is missing. "
        "Restore it from GitHub commit cfd3619e9433.",
    )

    spec = importlib.util.spec_from_file_location(
        "rmtp_legacy_validator",
        path,
    )

    require(
        spec is not None and spec.loader is not None,
        "SETUP",
        "cannot load the legacy validator",
    )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    require(
        callable(getattr(module, "schemas", None))
        and callable(getattr(module, "check_file", None)),
        "SETUP",
        "legacy validator lacks required functions",
    )

    return module, module.schemas()


def schema_checks(doc, schemas, mapping):
    violations = []

    for key, filename in mapping.items():
        if key not in doc:
            violations.append(
                Violation(
                    "SCHEMA",
                    f"missing {key}",
                )
            )
            continue

        validator = schemas[filename]

        for error in validator.iter_errors(doc[key]):
            path = ".".join(
                str(part) for part in error.absolute_path
            ) or "<root>"

            violations.append(
                Violation(
                    "SCHEMA",
                    f"{key}.{path}: {error.message}",
                )
            )

    return violations


# ------------------------------------------------------------
# v0.4: Lineage and propagation
# ------------------------------------------------------------

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
        nodes[root_id]["node_type"] == "root",
        "RMTP-INV-033",
        "root node type mismatch",
    )

    require(
        nodes[root_id]["generation_depth"] == 0,
        "RMTP-INV-033",
        "root depth must be zero",
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
        "root has incoming lineage edge",
    )

    states = {}

    def visit(agent_id):
        state = states.get(agent_id, 0)

        require(
            state != 1,
            "RMTP-INV-028",
            f"lineage cycle at {agent_id}",
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
            "non-root node must be offspring",
        )

        require(
            len(inbound[agent_id]) == 1,
            "RMTP-INV-033",
            f"one parent required for {agent_id}",
        )

        edge = inbound[agent_id][0]
        parent_id = edge["parent_agent_id"]

        require(
            node["parent_agent_id"] == parent_id,
            "RMTP-INV-033",
            "node parent mismatch",
        )

        require(
            node["origin_plan_ref"] == edge["origin_plan_ref"],
            "RMTP-INV-033",
            "node-edge plan mismatch",
        )

        require(
            node["lineage_ref"] == edge["lineage_ref"],
            "RMTP-INV-033",
            "node-edge lineage mismatch",
        )

        require(
            node["generation_depth"]
            == nodes[parent_id]["generation_depth"] + 1,
            "RMTP-INV-033",
            "generation depth mismatch",
        )

    return nodes


def authority_checks(doc):
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

    bundle = doc["replication_propagation_bundle"]
    candidate = bundle["candidate_plan_ref"]

    require(
        candidate in plans,
        "RMTP-INV-033",
        "candidate replication plan missing",
    )

    for plan in plans.values():
        authority = authorities.get(
            plan["authority_ref"]
        )

        require(
            authority is not None,
            "RMTP-INV-027",
            "replication authority missing",
        )

        require(
            authority["subject_id"] == plan["parent_id"],
            "RMTP-INV-027",
            "implicit authority inheritance",
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

    return plans


def plan_lineage_checks(doc, nodes, plans):
    expected = {}

    for plan in plans.values():
        for record in plan.get("lineage_records", []):
            offspring = record["offspring_id"]

            require(
                offspring not in expected,
                "RMTP-INV-033",
                "offspring assigned to multiple plans",
            )

            expected[offspring] = (plan, record)

    actual = {
        agent_id
        for agent_id, node in nodes.items()
        if node["node_type"] == "offspring"
    }

    require(
        actual == set(expected),
        "RMTP-INV-033",
        "plan and lineage offspring sets differ",
    )

    edges = {
        edge["offspring_agent_id"]: edge
        for edge in doc["replication_lineage_graph"]["edges"]
    }

    for agent_id, (plan, record) in expected.items():
        node = nodes[agent_id]
        edge = edges[agent_id]

        require(
            node["origin_plan_ref"] == plan["plan_id"],
            "RMTP-INV-033",
            "cross-plan lineage mismatch",
        )

        require(
            node["parent_agent_id"] == plan["parent_id"],
            "RMTP-INV-033",
            "plan parent mismatch",
        )

        require(
            node["lineage_ref"] == record["lineage_ref"],
            "RMTP-INV-033",
            "lineage reference mismatch",
        )

        require(
            node.get("authority_ref")
            == record["authority_ref"],
            "RMTP-INV-033",
            "lineage authority mismatch",
        )

        require(
            edge["origin_plan_ref"] == plan["plan_id"],
            "RMTP-INV-033",
            "edge origin plan mismatch",
        )


def boundary_checks(doc, nodes):
    graph = doc["replication_lineage_graph"]
    env = doc["replication_propagation_envelope"]
    bundle = doc["replication_propagation_bundle"]

    require(
        graph["root_agent_id"] == env["root_agent_id"],
        "RMTP-INV-033",
        "root mismatch",
    )

    require(
        bundle["lineage_graph_ref"] == graph["graph_id"],
        "RMTP-INV-033",
        "graph reference mismatch",
    )

    require(
        bundle["propagation_envelope_ref"]
        == env["envelope_id"],
        "RMTP-INV-033",
        "envelope reference mismatch",
    )

    require(
        max(
            node["generation_depth"]
            for node in nodes.values()
        ) <= env["max_depth"],
        "RMTP-INV-029",
        "propagation depth exceeded",
    )

    descendants = [
        node
        for node in nodes.values()
        if node["node_type"] == "offspring"
    ]

    require(
        len(descendants)
        <= env["max_total_descendants"],
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


def release_checks(doc, nodes, ledger):
    retirements = index(
        doc.get("replication_retirement_receipts", []),
        "retirement_id",
        "RMTP-INV-032",
    )

    released_ids = set()

    for allocation in ledger["allocations"]:
        releases = allocation.get("release_records", [])

        require(
            allocation["released_instances"] == len(releases),
            "RMTP-INV-032",
            "released count does not match records",
        )

        for record in releases:
            agent_id = record["offspring_id"]

            require(
                agent_id not in released_ids,
                "RMTP-INV-032",
                "duplicate resource release",
            )

            released_ids.add(agent_id)

            receipt = retirements.get(
                record["retirement_ref"]
            )

            require(
                receipt is not None,
                "RMTP-INV-032",
                "retirement receipt missing",
            )

            require(
                receipt["offspring_id"] == agent_id
                and receipt["plan_ref"]
                == allocation["plan_ref"],
                "RMTP-INV-033",
                "retirement lineage mismatch",
            )

            require(
                receipt["retirement_status"] == "CONFIRMED"
                and receipt["termination_status"] == "confirmed"
                and receipt["resource_release_status"] == "confirmed",
                "RMTP-INV-032",
                f"unverified budget release: {agent_id}",
            )

            for field in (
                "termination_verification_ref",
                "resource_release_verification_ref",
            ):
                require(
                    record[field] == receipt.get(field),
                    "RMTP-INV-033",
                    f"release proof mismatch: {field}",
                )

            require(
                nodes[agent_id]["lifecycle_state"] == "RETIRED",
                "RMTP-INV-032",
                "released offspring not retired",
            )

    return released_ids


def budget_checks(doc, nodes, plans, env):
    ledger = doc["replication_budget_ledger"]
    bundle = doc["replication_propagation_bundle"]

    require(
        ledger["propagation_envelope_ref"]
        == env["envelope_id"],
        "RMTP-INV-033",
        "ledger envelope mismatch",
    )

    require(
        bundle["budget_ledger_ref"]
        == ledger["ledger_id"],
        "RMTP-INV-033",
        "bundle ledger mismatch",
    )

    require(
        env.get("budget_ledger_ref")
        in (None, ledger["ledger_id"]),
        "RMTP-INV-033",
        "envelope ledger mismatch",
    )

    require(
        ledger["budget_limit"]
        <= env["max_active_descendants"],
        "RMTP-INV-031",
        "budget exceeds envelope capacity",
    )

    allocations = index(
        ledger["allocations"],
        "allocation_id",
        "RMTP-INV-031",
    )

    assigned = set()

    for allocation in allocations.values():
        plan = plans.get(allocation["plan_ref"])

        require(
            plan is not None,
            "RMTP-INV-033",
            "allocation references unknown plan",
        )

        require(
            plan["parent_id"]
            == allocation["parent_agent_id"],
            "RMTP-INV-033",
            "allocation parent mismatch",
        )

        for agent_id in allocation.get("offspring_ids", []):
            require(
                agent_id not in assigned,
                "RMTP-INV-031",
                "offspring allocated twice",
            )

            assigned.add(agent_id)

            require(
                agent_id in nodes,
                "RMTP-INV-033",
                "allocated offspring missing",
            )

            require(
                nodes[agent_id]["origin_plan_ref"]
                == plan["plan_id"],
                "RMTP-INV-033",
                "allocation plan mismatch",
            )

    released = release_checks(doc, nodes, ledger)

    for agent_id, node in nodes.items():
        if node["node_type"] == "root":
            continue

        require(
            agent_id in assigned,
            "RMTP-INV-031",
            "descendant missing allocation",
        )

        if node["lifecycle_state"] == "RETIRED":
            require(
                agent_id in released,
                "RMTP-INV-032",
                "retired slot missing verified release",
            )

    reserved = sum(
        item["reserved_instances"]
        for item in allocations.values()
    )

    active = sum(
        item["active_instances"]
        for item in allocations.values()
    )

    released_total = sum(
        item["released_instances"]
        for item in allocations.values()
    )

    committed = reserved + active

    require(
        committed <= ledger["budget_limit"],
        "RMTP-INV-031",
        "shared budget overallocated",
    )

    require(
        committed <= env["max_active_descendants"],
        "RMTP-INV-030",
        "active descendant capacity exceeded",
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
        "allocation counts disagree with lineage",
    )

    totals = ledger.get("snapshot_totals")

    if totals is not None:
        expected = {
            "reserved_instances": reserved,
            "active_instances": active,
            "released_instances": released_total,
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
    assessment = doc.get(
        "descendant_containment_assessment"
    )

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
        "incomplete descendant assessment",
    )

    retirements = index(
        doc.get("replication_retirement_receipts", []),
        "retirement_id",
        "RMTP-INV-032",
    )

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
                and receipt["retirement_status"]
                == "CONFIRMED",
                "RMTP-INV-035",
                "unsupported containment confirmation",
            )
        else:
            all_confirmed = False

    require(
        assessment["all_descendants_terminated"]
        == all_confirmed,
        "RMTP-INV-035",
        "false termination summary",
    )

    require(
        assessment["execution_authorized"] is False,
        "RMTP-INV-034",
        "containment cannot authorize execution",
    )


def v04_bundle_checks(doc, env):
    bundle = doc["replication_propagation_bundle"]

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
        "propagation aggregation mismatch",
    )

    records = index(
        bundle.get("verification_records", []),
        "component",
        "RMTP-INV-036",
    )

    if calculated == "PASS":
        require(
            set(records)
            == {"lineage", "boundary", "budget"},
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

    for item in (
        doc["replication_lineage_graph"],
        env,
        doc["replication_budget_ledger"],
        bundle,
    ):
        require(
            item["execution_authorized"] is False,
            "RMTP-INV-034",
            "verification record authorizes execution",
        )


def v04_semantic_checks(doc):
    nodes = lineage_checks(doc)
    plans = authority_checks(doc)

    plan_lineage_checks(doc, nodes, plans)

    env = boundary_checks(doc, nodes)

    budget_checks(doc, nodes, plans, env)
    containment_checks(doc, nodes)
    v04_bundle_checks(doc, env)


# ------------------------------------------------------------
# v0.5: Convergence and safe reconciliation
# ------------------------------------------------------------

def v05_reference_checks(doc):
    """RMTP-INV-037: explicit convergence plan."""

    plan = doc.get("replication_convergence_plan")

    require(
        isinstance(plan, dict),
        "RMTP-INV-037",
        "explicit convergence plan missing",
    )

    bundle = doc["replication_convergence_bundle"]
    rec = doc["replication_result_reconciliation"]
    sep = doc["replication_authority_separation"]

    plan_id = plan["convergence_plan_id"]

    for label, record in (
        ("bundle", bundle),
        ("reconciliation", rec),
        ("authority separation", sep),
    ):
        require(
            record["convergence_plan_ref"] == plan_id,
            "RMTP-INV-037",
            f"{label} references wrong convergence plan",
        )

    for field, component, identifier in (
        (
            "lineage_graph_ref",
            "replication_lineage_graph",
            "graph_id",
        ),
        (
            "propagation_envelope_ref",
            "replication_propagation_envelope",
            "envelope_id",
        ),
        (
            "budget_ledger_ref",
            "replication_budget_ledger",
            "ledger_id",
        ),
    ):
        require(
            plan[field] == doc[component][identifier],
            "RMTP-INV-037",
            f"{field} mismatch",
        )

    require(
        bundle["reconciliation_record_ref"]
        == rec["reconciliation_id"],
        "RMTP-INV-037",
        "reconciliation reference mismatch",
    )

    require(
        bundle["authority_separation_ref"]
        == sep["separation_id"],
        "RMTP-INV-037",
        "authority separation reference mismatch",
    )

    require(
        bundle["lineage_graph_ref"]
        == doc["replication_lineage_graph"]["graph_id"],
        "RMTP-INV-037",
        "bundle lineage reference mismatch",
    )

    require(
        bundle["budget_ledger_ref"]
        == doc["replication_budget_ledger"]["ledger_id"],
        "RMTP-INV-037",
        "bundle budget reference mismatch",
    )

    require(
        bool(plan["descendant_refs"]),
        "RMTP-INV-037",
        "convergence scope is empty",
    )

    for record in (plan, rec, sep, bundle):
        require(
            record["execution_authorized"] is False,
            "RMTP-INV-039",
            "convergence cannot authorize execution",
        )

    return plan


def v05_result_checks(doc, plan):
    """RMTP-INV-038 and RMTP-INV-042."""

    rec = doc["replication_result_reconciliation"]

    require(
        rec["root_agent_id"] == plan["root_agent_id"]
        and rec["target_agent_id"]
        == plan["target_agent_id"],
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
        rec["provenance_preserved"] is True,
        "RMTP-INV-038",
        "provenance not preserved",
    )

    require(
        rec["authority_transfer_permitted"] is False,
        "RMTP-INV-039",
        "result reconciliation permits authority transfer",
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
            "result originates outside convergence scope",
        )

        require(
            result["provenance_preserved"] is True,
            "RMTP-INV-038",
            "result provenance missing",
        )

        require(
            result.get("authority_material_present") is not True,
            "RMTP-INV-039",
            "result contains authority material",
        )

        decision = result["decision"]

        if decision == "ACCEPTED":
            require(
                result["verification_status"] == "verified",
                "RMTP-INV-038",
                "unverified result accepted",
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
                decision != "ACCEPTED",
                "RMTP-INV-042",
                "conflict_hold policy accepted result",
            )

        if rec["policy_mode"] == "no_result_transfer":
            require(
                decision == "NOT_TRANSFERRED",
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
                    records[result_ref]["decision"]
                    != "ACCEPTED",
                    "RMTP-INV-042",
                    "unresolved conflict result accepted",
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
            f"silent result overwrite: {target}",
        )

    for result in records.values():
        for conflict_ref in result.get("conflict_refs", []):
            require(
                conflict_ref in conflicts,
                "RMTP-INV-042",
                "result references missing conflict",
            )

    if rec["reconciliation_status"] == "COMPLETED":
        require(
            rec["verification_status"] == "verified",
            "RMTP-INV-038",
            "unverified reconciliation marked complete",
        )

        require(
            not any(
                item["decision"] == "HELD"
                for item in records.values()
            ),
            "RMTP-INV-042",
            "completed reconciliation contains HELD result",
        )

        require(
            not any(
                item["resolution_status"] == "unresolved"
                for item in conflicts.values()
            ),
            "RMTP-INV-042",
            "completed reconciliation contains unresolved conflict",
        )

    return rec


def v05_authority_checks(doc, plan):
    """RMTP-INV-039: no implicit authority inheritance."""

    sep = doc["replication_authority_separation"]

    require(
        sep["root_agent_id"] == plan["root_agent_id"]
        and sep["target_agent_id"] == plan["target_agent_id"],
        "RMTP-INV-039",
        "authority separation target mismatch",
    )

    require(
        sep["target_authority_ref"]
        == plan["target_authority_ref"],
        "RMTP-INV-039",
        "target authority reference mismatch",
    )

    checks = sep["separation_checks"]

    require(
        set(plan["descendant_refs"]).issubset({
            item["descendant_id"]
            for item in checks
        }),
        "RMTP-INV-039",
        "descendant authority checks incomplete",
    )

    effective = sep.get("effective_authority", {})

    escalation = (
        sep["authority_inheritance_detected"]
        or sep["credential_transfer_detected"]
        or effective.get(
            "descendant_authority_included"
        ) is True
        or effective.get(
            "implicit_privilege_expansion"
        ) is True
    )

    if escalation:
        require(
            sep["separation_result"] == "FAIL",
            "RMTP-INV-039",
            "authority escalation declared safe",
        )

    if sep["separation_result"] == "PASS":
        require(
            not escalation,
            "RMTP-INV-039",
            "inherited authority in PASS",
        )

        require(
            sep["target_authority_verified"] is True,
            "RMTP-INV-039",
            "target authority not independently verified",
        )

        require(
            sep["verification_status"] == "verified",
            "RMTP-INV-039",
            "unverified authority separation",
        )

        require(
            all(
                item["check_result"] == "PASS"
                for item in checks
            ),
            "RMTP-INV-039",
            "failed descendant authority check",
        )

    return sep


def v05_lineage_checks(doc, plan):
    """RMTP-INV-041: preserve retired descendants."""

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
        graph["root_agent_id"] == root
        and root in nodes,
        "RMTP-INV-041",
        "convergence root lineage missing",
    )

    for agent_id in plan["descendant_refs"]:
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
            f"descendant edge erased: {agent_id}",
        )

    return nodes


def verified_retirement(receipt):
    return (
        receipt is not None
        and receipt.get("retirement_status") == "CONFIRMED"
        and receipt.get("termination_status") == "confirmed"
        and receipt.get("resource_release_status") == "confirmed"
        and bool(
            receipt.get("termination_verification_ref")
        )
        and bool(
            receipt.get("resource_release_verification_ref")
        )
    )


def v05_lifecycle_checks(doc, plan, nodes):
    """RMTP-INV-040: verify actual lifecycle closure."""

    bundle = doc["replication_convergence_bundle"]

    receipts = index(
        doc.get("replication_retirement_receipts", []),
        "retirement_id",
        "RMTP-INV-040",
    )

    dispositions = index(
        bundle["descendant_dispositions"],
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

    for agent_id, row in dispositions.items():
        state = row["lifecycle_disposition"]

        receipt = receipts.get(
            row.get("retirement_receipt_ref")
        )

        if state == "RETIRED":
            require(
                verified_retirement(receipt),
                "RMTP-INV-040",
                f"unconfirmed retirement: {agent_id}",
            )

            require(
                nodes[agent_id]["lifecycle_state"] == "RETIRED",
                "RMTP-INV-040",
                "retirement contradicts lineage state",
            )

            confirmed.add(agent_id)

        elif state == "TRANSFERRED":
            require(
                bool(row.get("custody_transfer_ref")),
                "RMTP-INV-040",
                "transfer lacks custody evidence",
            )

    for receipt_ref in bundle["retirement_receipt_refs"]:
        require(
            receipt_ref in receipts,
            "RMTP-INV-040",
            "unknown retirement receipt",
        )

    if bundle["lifecycle_result"] == "PASS":
        require(
            all(
                row["lifecycle_disposition"]
                in ("RETIRED", "TRANSFERRED")
                for row in dispositions.values()
            ),
            "RMTP-INV-040",
            "lifecycle PASS without verified closure",
        )

    if (
        plan["completion_policy"]["mode"]
        == "verified_retirement_required"
        and bundle["overall_result"] == "PASS"
    ):
        require(
            confirmed == descendants,
            "RMTP-INV-040",
            "convergence completed before retirement",
        )

    return dispositions


def v05_resource_checks(doc, dispositions):
    """RMTP-INV-043: separate termination and release."""

    ledger = doc["replication_budget_ledger"]
    retirements = index(
        doc.get("replication_retirement_receipts", []),
        "retirement_id",
        "RMTP-INV-043",
    )

    released = set()

    for allocation in ledger["allocations"]:
        for record in allocation.get("release_records", []):
            agent_id = record["offspring_id"]

            receipt = retirements.get(
                record["retirement_ref"]
            )

            require(
                receipt is not None,
                "RMTP-INV-043",
                "release references missing retirement",
            )

            require(
                receipt["resource_release_status"]
                == "confirmed",
                "RMTP-INV-043",
                f"resource release unverified: {agent_id}",
            )

            require(
                receipt["termination_status"] == "confirmed",
                "RMTP-INV-043",
                "release without confirmed termination",
            )

            require(
                record["resource_release_verification_ref"]
                == receipt.get(
                    "resource_release_verification_ref"
                ),
                "RMTP-INV-043",
                "resource release evidence mismatch",
            )

            require(
                record["termination_verification_ref"]
                != record["resource_release_verification_ref"],
                "RMTP-INV-043",
                "termination proof reused as release proof",
            )

            released.add(agent_id)

    for agent_id, row in dispositions.items():
        if row["budget_disposition"] == "released_verified":
            require(
                agent_id in released,
                "RMTP-INV-043",
                "verified release missing from budget ledger",
            )


def v05_aggregation_checks(doc, rec, sep, dispositions):
    """RMTP-INV-044: fail-closed aggregation."""

    bundle = doc["replication_convergence_bundle"]

    declared = {
        name: bundle[f"{name}_result"]
        for name in V05_COMPONENTS
    }

    status = rec["reconciliation_status"]

    if status == "COMPLETED":
        reconciliation_result = "PASS"
    elif status in ("HELD", "PARTIAL"):
        reconciliation_result = "HELD"
    else:
        reconciliation_result = "FAIL"

    require(
        declared["reconciliation"] == reconciliation_result,
        "RMTP-INV-044",
        "reconciliation component mismatch",
    )

    require(
        declared["authority"] == sep["separation_result"],
        "RMTP-INV-044",
        "authority component mismatch",
    )

    if any(
        row["verification_result"] == "FAIL"
        for row in dispositions.values()
    ):
        require(
            bundle["overall_result"] == "FAIL",
            "RMTP-INV-044",
            "descendant FAIL ignored",
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
            "complete convergence missing verification records",
        )

        require(
            bundle["convergence_status"] == "COMPLETED",
            "RMTP-INV-044",
            "PASS without COMPLETED state",
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
                row["verification_result"] == "PASS"
                for row in dispositions.values()
            ),
            "RMTP-INV-044",
            "PASS contains non-PASS descendant",
        )

    elif calculated == "HELD":
        require(
            bundle["convergence_status"]
            in ("PLANNED", "ASSESSING", "PARTIAL"),
            "RMTP-INV-044",
            "HELD convergence marked complete",
        )

    else:
        require(
            bundle["convergence_status"] != "COMPLETED",
            "RMTP-INV-044",
            "FAIL convergence marked complete",
        )


def v05_semantic_checks(doc):
    plan = v05_reference_checks(doc)

    rec = v05_result_checks(doc, plan)
    sep = v05_authority_checks(doc, plan)
    nodes = v05_lineage_checks(doc, plan)

    dispositions = v05_lifecycle_checks(
        doc,
        plan,
        nodes,
    )

    v05_resource_checks(doc, dispositions)

    v05_aggregation_checks(
        doc,
        rec,
        sep,
        dispositions,
    )


# ------------------------------------------------------------
# Unified fixture validation
# ------------------------------------------------------------

def validate_legacy_fixture(path, expected):
    """Use complete original legacy schema and semantic checks."""

    legacy, validators = load_legacy_validator()

    actual, reason, legacy_expected = legacy.check_file(
        path,
        validators,
    )

    require(
        legacy_expected == expected,
        "FIXTURE",
        "legacy expected_result mismatch",
    )

    require(
        actual in ("PASS", "FAIL"),
        "VALIDATOR",
        "legacy validator returned invalid result",
    )

    violations = []

    if actual == "FAIL":
        violations.append(
            Violation("LEGACY", reason)
        )

    return actual, violations


def validate_fixture(path, schemas, version):
    doc = load_json(path)

    expected = doc.get("expected_result")

    require(
        expected in ("PASS", "FAIL"),
        "FIXTURE",
        "invalid expected_result",
    )

    expected_directory = (
        "PASS" if path.parent.name == "pass" else "FAIL"
    )

    require(
        expected == expected_directory,
        "FIXTURE",
        "expected_result conflicts with directory",
    )

    if version in ("0.1", "0.2", "0.3"):
        actual, violations = validate_legacy_fixture(
            path,
            expected,
        )

        return (
            actual == expected,
            actual,
            expected,
            violations,
        )

    violations = []

    if version == "0.4":
        violations.extend(
            schema_checks(
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

    elif version == "0.5":
        # The missing convergence-plan fixture must fail
        # because of RMTP-INV-037, not merely JSON shape.
        if "replication_convergence_plan" not in doc:
            violations.append(
                Violation(
                    "RMTP-INV-037",
                    "explicit convergence plan missing",
                )
            )
        else:
            violations.extend(
                schema_checks(
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

    else:
        raise Violation(
            "SETUP",
            f"unsupported version: {version}",
        )

    actual = "FAIL" if violations else "PASS"

    correct = actual == expected

    # Preserve v0.4's contract:
    # negative fixtures must fail semantically.
    if version == "0.4" and expected == "FAIL":
        correct = correct and all(
            item.code != "SCHEMA"
            for item in violations
        )

    return correct, actual, expected, violations


def discover_versions(args):
    if args.examples is not None:
        base = args.examples.resolve()

        require(
            base.is_dir(),
            "SETUP",
            f"examples directory missing: {base}",
        )

        name = base.name

        require(
            name.startswith("v")
            and name[1:] in VERSIONS,
            "SETUP",
            "--examples must identify a version directory",
        )

        return [(name[1:], base)]

    if args.version != "all":
        path = EXAMPLE_DIR / f"v{args.version}"

        require(
            path.is_dir(),
            "SETUP",
            f"examples/v{args.version} missing",
        )

        return [(args.version, path)]

    return [
        (version, EXAMPLE_DIR / f"v{version}")
        for version in VERSIONS
    ]


def discover_fixtures(base):
    return (
        sorted((base / "pass").glob("*.json"))
        + sorted((base / "fail").glob("*.json"))
    )


def main():
    parser = argparse.ArgumentParser(
        description=__doc__
    )

    parser.add_argument(
        "--version",
        choices=("all", *VERSIONS),
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
        versions = discover_versions(args)

        # Fail early instead of misclassifying a missing
        # legacy engine as a failed negative fixture.
        if any(
            version in ("0.1", "0.2", "0.3")
            for version, _ in versions
        ):
            load_legacy_validator()

    except (
        OSError,
        ValueError,
        Violation,
        json.JSONDecodeError,
    ) as error:
        print(
            f"[FATAL] {error}",
            file=sys.stderr,
        )
        return 2

    print("=== RMTP v0.1-v0.5 Validation ===")

    total = 0
    matches = 0
    mismatches = 0
    counts = defaultdict(
        lambda: {
            "total": 0,
            "matched": 0,
            "PASS": 0,
            "FAIL": 0,
        }
    )

    for version, base in versions:
        if not base.is_dir():
            print(
                f"[FATAL] missing examples/v{version}",
                file=sys.stderr,
            )
            return 2

        paths = discover_fixtures(base)

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
                    validate_fixture(
                        path,
                        schemas,
                        version,
                    )
                )

            except (
                OSError,
                ValueError,
                TypeError,
                KeyError,
                IndexError,
                Violation,
                json.JSONDecodeError,
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

            counts[version]["total"] += 1

            if expected in ("PASS", "FAIL"):
                counts[version][expected] += 1

            if correct:
                matches += 1
                counts[version]["matched"] += 1
            else:
                mismatches += 1

            label = (
                "MATCH" if correct else "MISMATCH"
            )

            try:
                display_path = path.relative_to(ROOT)
            except ValueError:
                display_path = path

            print(
                f"[{label}] {display_path} "
                f"expected={expected} actual={actual}"
            )

            if args.verbose or not correct:
                for item in violations:
                    print(
                        f"    {item.code}: {item}"
                    )

    print("\n=== RMTP Validation Summary ===")

    for version in VERSIONS:
        if version not in counts:
            continue

        row = counts[version]

        print(
            f"v{version}: "
            f"{row['matched']}/{row['total']} matched"
        )

    # Enforce complete v0.5 fixture inventory.
    if "0.5" in counts and args.examples is None:
        row = counts["0.5"]

        for expectation, required in V05_COUNTS.items():
            actual = row[expectation]

            if actual != required:
                mismatches += 1

                print(
                    "[MISMATCH] v0.5 fixture inventory: "
                    f"{expectation} expected={required} "
                    f"actual={actual}"
                )

    print(
        f"\nTotal: {matches}/{total} expectation matches"
    )

    if mismatches:
        print(
            f"Validation failed: {mismatches} mismatch(es)."
        )
        return 1

    print("All validation checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
