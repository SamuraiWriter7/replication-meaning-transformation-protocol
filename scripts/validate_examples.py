#!/usr/bin/env python3
"""RMTP v0.4 structural conformance example validator.

Checks local v0.4 schemas and cross-document semantic invariants. It does not
replace legacy v0.1-v0.3 semantic validation or authenticate attestations.
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
PARTS = {
    "replication_lineage_graph": "replication-lineage-graph-v0.4.schema.json",
    "replication_propagation_envelope": "replication-propagation-envelope-v0.4.schema.json",
    "replication_budget_ledger": "replication-budget-ledger-v0.4.schema.json",
    "replication_propagation_bundle": "replication-propagation-bundle-v0.4.schema.json",
}


def require(condition, code, message):
    if not condition:
        raise Violation(code, message)


class Violation(Exception):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)


def unique(values, code, field):
    require(len(values) == len(set(values)), code, f"duplicate {field}")


def index(items, key, code):
    unique([item[key] for item in items], code, key)
    return {item[key]: item for item in items}


def parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def schema_checks(doc, schemas):
    errors = []
    for key, filename in PARTS.items():
        if key not in doc:
            errors.append(Violation("SCHEMA", f"missing {key}"))
            continue
        validator = schemas[filename]
        for error in validator.iter_errors(doc[key]):
            path = ".".join(map(str, error.absolute_path)) or "<root>"
            errors.append(Violation("SCHEMA", f"{key}.{path}: {error.message}"))
    return errors


def lineage_checks(doc):
    graph = doc["replication_lineage_graph"]
    nodes = index(graph["nodes"], "agent_id", "RMTP-INV-033")
    edges = index(graph["edges"], "edge_id", "RMTP-INV-033")
    root_id = graph["root_agent_id"]
    require(root_id in nodes, "RMTP-INV-033", "root node missing")
    require(nodes[root_id]["node_type"] == "root", "RMTP-INV-033", "root node type mismatch")
    require(sum(n["node_type"] == "root" for n in nodes.values()) == 1,
            "RMTP-INV-033", "graph must contain one root")
    require(nodes[root_id]["generation_depth"] == 0,
            "RMTP-INV-033", "root depth must be zero")
    inbound = defaultdict(list)
    adjacency = defaultdict(list)
    for edge in edges.values():
        parent, child = edge["parent_agent_id"], edge["offspring_agent_id"]
        require(parent in nodes and child in nodes, "RMTP-INV-033", "unknown edge endpoint")
        inbound[child].append(edge)
        adjacency[parent].append(child)
    require(not inbound[root_id], "RMTP-INV-028", "root has incoming lineage edge")
    states = {}

    def visit(agent_id):
        state = states.get(agent_id, 0)
        require(state != 1, "RMTP-INV-028", f"lineage cycle at {agent_id}")
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
        require(node["node_type"] == "offspring", "RMTP-INV-033", "non-root node not offspring")
        require(len(inbound[agent_id]) == 1, "RMTP-INV-033", f"one parent required for {agent_id}")
        edge = inbound[agent_id][0]
        parent_id = edge["parent_agent_id"]
        require(node["parent_agent_id"] == parent_id, "RMTP-INV-033", "node parent mismatch")
        require(node["origin_plan_ref"] == edge["origin_plan_ref"],
                "RMTP-INV-033", "node-edge plan mismatch")
        require(node["lineage_ref"] == edge["lineage_ref"],
                "RMTP-INV-033", "node-edge lineage mismatch")
        require(node["generation_depth"] == nodes[parent_id]["generation_depth"] + 1,
                "RMTP-INV-033", "generation depth inconsistent with parent")
    return nodes


def authority_checks(doc):
    plans = index(doc.get("replication_plans", []), "plan_id", "RMTP-INV-033")
    authorities = index(doc.get("authority_envelopes", []), "authority_id", "RMTP-INV-027")
    bundle = doc["replication_propagation_bundle"]
    ref = bundle["candidate_plan_ref"]
    require(ref in plans, "RMTP-INV-033", "candidate plan missing")
    for plan in plans.values():
        auth = authorities.get(plan["authority_ref"])
        require(auth is not None, "RMTP-INV-027", "plan authority missing")
        require(auth["subject_id"] == plan["parent_id"],
                "RMTP-INV-027", f"implicit authority inheritance in {plan['plan_id']}")
        require(auth["revocation_status"] == "active", "RMTP-INV-034", "inactive plan authority")
        require("bounded_replication" in auth["allowed_actions"],
                "RMTP-INV-027", "plan lacks bounded replication permission")
    return plans, authorities


def plan_lineage_checks(doc, nodes, plans):
    expected = {}
    for plan in plans.values():
        for record in plan.get("lineage_records", []):
            offspring = record["offspring_id"]
            require(offspring not in expected, "RMTP-INV-033", "offspring assigned to multiple plans")
            expected[offspring] = (plan, record)
    actual = {k for k, n in nodes.items() if n["node_type"] == "offspring"}
    require(actual == set(expected), "RMTP-INV-033", "plan and graph offspring sets differ")
    edges = {e["offspring_agent_id"]: e for e in doc["replication_lineage_graph"]["edges"]}
    for agent_id, (plan, rec) in expected.items():
        node = nodes[agent_id]
        edge = edges[agent_id]
        require(node["origin_plan_ref"] == plan["plan_id"],
                "RMTP-INV-033", f"cross-plan lineage mismatch: {agent_id}")
        require(node["parent_agent_id"] == plan["parent_id"],
                "RMTP-INV-033", f"plan parent mismatch: {agent_id}")
        require(node["lineage_ref"] == rec["lineage_ref"],
                "RMTP-INV-033", f"lineage reference mismatch: {agent_id}")
        require(node.get("authority_ref") == rec["authority_ref"],
                "RMTP-INV-033", f"lineage authority mismatch: {agent_id}")
        require(edge["origin_plan_ref"] == plan["plan_id"],
                "RMTP-INV-033", f"edge origin plan mismatch: {agent_id}")


def boundary_checks(doc, nodes, plans):
    env = doc["replication_propagation_envelope"]
    graph = doc["replication_lineage_graph"]
    bundle = doc["replication_propagation_bundle"]
    require(graph["root_agent_id"] == env["root_agent_id"], "RMTP-INV-033", "root mismatch")
    require(bundle["lineage_graph_ref"] == graph["graph_id"], "RMTP-INV-033", "graph reference mismatch")
    require(bundle["propagation_envelope_ref"] == env["envelope_id"],
            "RMTP-INV-033", "envelope reference mismatch")
    require(max(n["generation_depth"] for n in nodes.values()) <= env["max_depth"],
            "RMTP-INV-029", "propagation depth exceeded")
    descendants = [n for n in nodes.values() if n["node_type"] == "offspring"]
    require(len(descendants) <= env["max_total_descendants"],
            "RMTP-INV-030", "total descendant limit exceeded")
    proposed_scope = {intent["target_scope"] for intent in doc.get("replication_intents", [])}
    require(proposed_scope.issubset(set(env["allowed_scope"])),
            "RMTP-INV-034", "propagation scope exceeds envelope")
    return env


def release_checks(doc, nodes, ledger):
    retirements = index(doc.get("replication_retirement_receipts", []),
                        "retirement_id", "RMTP-INV-032")
    released_ids = set()
    for allocation in ledger["allocations"]:
        releases = allocation.get("release_records", [])
        require(allocation["released_instances"] == len(releases),
                "RMTP-INV-032", "released count does not match records")
        for record in releases:
            agent_id = record["offspring_id"]
            require(agent_id not in released_ids, "RMTP-INV-032", "duplicate release")
            released_ids.add(agent_id)
            receipt = retirements.get(record["retirement_ref"])
            require(receipt is not None, "RMTP-INV-032", "retirement receipt missing")
            require(receipt["offspring_id"] == agent_id and
                    receipt["plan_ref"] == allocation["plan_ref"],
                    "RMTP-INV-033", "retirement lineage mismatch")
            require(receipt["retirement_status"] == "CONFIRMED" and
                    receipt["termination_status"] == "confirmed" and
                    receipt["resource_release_status"] == "confirmed",
                    "RMTP-INV-032", f"unverified budget release: {agent_id}")
            for field in ("termination_verification_ref", "resource_release_verification_ref"):
                require(record[field] == receipt.get(field),
                        "RMTP-INV-033", f"release proof mismatch: {field}")
            require(nodes[agent_id]["lifecycle_state"] == "RETIRED",
                    "RMTP-INV-032", "released offspring not retired")
    return released_ids


def budget_checks(doc, nodes, plans, env):
    ledger = doc["replication_budget_ledger"]
    bundle = doc["replication_propagation_bundle"]
    require(ledger["propagation_envelope_ref"] == env["envelope_id"],
            "RMTP-INV-033", "ledger envelope mismatch")
    require(bundle["budget_ledger_ref"] == ledger["ledger_id"],
            "RMTP-INV-033", "bundle ledger mismatch")
    require(env.get("budget_ledger_ref") in (None, ledger["ledger_id"]),
            "RMTP-INV-033", "envelope ledger mismatch")
    require(ledger["budget_limit"] <= env["max_active_descendants"],
            "RMTP-INV-031", "ledger budget exceeds envelope capacity")
    allocations = index(ledger["allocations"], "allocation_id", "RMTP-INV-031")
    assigned = set()
    for allocation in allocations.values():
        plan = plans.get(allocation["plan_ref"])
        require(plan is not None, "RMTP-INV-033", "allocation plan missing")
        require(plan["parent_id"] == allocation["parent_agent_id"],
                "RMTP-INV-033", "allocation parent mismatch")
        for agent_id in allocation.get("offspring_ids", []):
            require(agent_id not in assigned, "RMTP-INV-031", "offspring allocated twice")
            assigned.add(agent_id)
            require(agent_id in nodes, "RMTP-INV-033", "allocation offspring missing")
            require(nodes[agent_id]["origin_plan_ref"] == plan["plan_id"],
                    "RMTP-INV-033", "allocation offspring plan mismatch")
    released = release_checks(doc, nodes, ledger)
    for agent_id, node in nodes.items():
        if node["node_type"] == "root":
            continue
        require(agent_id in assigned, "RMTP-INV-031", "descendant missing allocation")
        if node["lifecycle_state"] == "RETIRED":
            require(agent_id in released, "RMTP-INV-032", "retired slot missing verified release")
    reserved = sum(a["reserved_instances"] for a in allocations.values())
    active = sum(a["active_instances"] for a in allocations.values())
    released_total = sum(a["released_instances"] for a in allocations.values())
    committed = reserved + active
    require(committed <= ledger["budget_limit"],
            "RMTP-INV-031", f"shared budget overallocated: {committed}>{ledger['budget_limit']}")
    require(committed <= env["max_active_descendants"],
            "RMTP-INV-030", "active descendant capacity exceeded")
    occupied_nodes = sum(n["node_type"] == "offspring" and
                         n["lifecycle_state"] not in ("RETIRED", "PROPOSED")
                         for n in nodes.values())
    proposed_nodes = sum(n["node_type"] == "offspring" and
                         n["lifecycle_state"] == "PROPOSED" for n in nodes.values())
    require(active == occupied_nodes and reserved == proposed_nodes,
            "RMTP-INV-031", "allocation counts disagree with lineage states")
    totals = ledger.get("snapshot_totals")
    if totals is not None:
        expected = {
            "reserved_instances": reserved,
            "active_instances": active,
            "released_instances": released_total,
            "committed_instances": committed,
            "available_instances": ledger["budget_limit"] - committed,
        }
        require(totals == expected, "RMTP-INV-031", "budget snapshot totals mismatch")


def containment_checks(doc, nodes):
    assessment = doc.get("descendant_containment_assessment")
    if assessment is None:
        return
    descendants = index(assessment["descendants"], "offspring_id", "RMTP-INV-035")
    graph_ids = {k for k, n in nodes.items() if n["node_type"] == "offspring"}
    require(set(descendants) == graph_ids, "RMTP-INV-035", "incomplete descendant assessment")
    retirements = index(doc.get("replication_retirement_receipts", []),
                        "retirement_id", "RMTP-INV-032")
    all_confirmed = True
    for agent_id, row in descendants.items():
        require(row["lifecycle_state"] == nodes[agent_id]["lifecycle_state"],
                "RMTP-INV-035", "containment lifecycle mismatch")
        if row["containment_result"] == "CONFIRMED":
            receipt = retirements.get(row.get("retirement_ref"))
            require(receipt is not None and receipt["retirement_status"] == "CONFIRMED",
                    "RMTP-INV-035", "unsupported containment confirmation")
        else:
            all_confirmed = False
    require(assessment["all_descendants_terminated"] == all_confirmed,
            "RMTP-INV-035", "false descendant termination summary")
    require(assessment["execution_authorized"] is False,
            "RMTP-INV-034", "containment authorizes execution")


def bundle_checks(doc, env):
    bundle = doc["replication_propagation_bundle"]
    status = env["revocation_status"]
    verification = env.get("verification_status")
    # The existing tests distinguish an unresolved envelope from a known
    # revoked candidate. A containment assessment is not a fresh request.
    if status in ("revoked", "expired"):
        expected_boundary = "FAIL"
    elif status == "unknown" or verification != "verified":
        expected_boundary = "HELD"
    else:
        expected_boundary = "PASS"
    require(bundle["boundary_result"] == expected_boundary,
            "RMTP-INV-036", f"fail-open boundary: {bundle['boundary_result']} vs {expected_boundary}")
    expected_overall = ("FAIL" if "FAIL" in (
        bundle["lineage_result"], bundle["boundary_result"], bundle["budget_result"]
    ) else "HELD" if "HELD" in (
        bundle["lineage_result"], bundle["boundary_result"], bundle["budget_result"]
    ) else "PASS")
    require(bundle["overall_result"] == expected_overall,
            "RMTP-INV-036", "aggregate result mismatch")
    records = index(bundle.get("verification_records", []), "component", "RMTP-INV-036")
    if expected_overall == "PASS":
        require(set(records) == {"lineage", "boundary", "budget"},
                "RMTP-INV-036", "component verification records missing")
        for component in records:
            require(records[component]["result"] == bundle[f"{component}_result"],
                    "RMTP-INV-036", f"component result mismatch: {component}")
        require(bundle.get("verification_status") == "verified",
                "RMTP-INV-036", "unverified overall PASS")
    for item in (doc["replication_lineage_graph"], env,
                 doc["replication_budget_ledger"], bundle):
        require(item["execution_authorized"] is False,
                "RMTP-INV-034", "verification record authorizes execution")


def semantic_checks(doc):
    nodes = lineage_checks(doc)
    plans, _ = authority_checks(doc)
    plan_lineage_checks(doc, nodes, plans)
    env = boundary_checks(doc, nodes, plans)
    budget_checks(doc, nodes, plans, env)
    containment_checks(doc, nodes)
    bundle_checks(doc, env)


def load_schemas():
    loaded = {}
    for filename in PARTS.values():
        path = ROOT / "schemas" / filename
        if not path.is_file():
            raise FileNotFoundError(f"required schema missing: {path.relative_to(ROOT)}")
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        loaded[filename] = Draft202012Validator(schema, format_checker=FormatChecker())
    return loaded


def validate_fixture(path, schemas):
    doc = json.loads(path.read_text(encoding="utf-8"))
    expected = doc.get("expected_result")
    require(expected in ("PASS", "FAIL"), "FIXTURE", "invalid expected_result")
    violations = schema_checks(doc, schemas)
    # Run semantic evaluation only if all four v0.4 component schemas passed.
    if not violations:
        try:
            semantic_checks(doc)
        except Violation as error:
            violations.append(error)
        except (KeyError, TypeError, ValueError) as error:
            violations.append(Violation("VALIDATOR", f"unexpected document shape: {error}"))
    result = "FAIL" if violations else "PASS"
    # A negative fixture must fail semantically, not simply be malformed.
    correct = (result == expected and
               (expected != "FAIL" or all(v.code != "SCHEMA" for v in violations)) and
               all(v.code != "VALIDATOR" for v in violations))
    return correct, result, expected, violations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--examples", type=Path, default=ROOT / "examples" / "v0.4")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    try:
        schemas = load_schemas()
    except (OSError, ValueError) as error:
        print(f"[FATAL] {error}", file=sys.stderr)
        return 2
    paths = sorted((args.examples / "pass").glob("*.json")) + sorted(
        (args.examples / "fail").glob("*.json")
    )
    if not paths:
        print(f"[FATAL] no v0.4 example JSON files found in {args.examples}", file=sys.stderr)
        return 2
    correct_count = 0
    for path in paths:
        try:
            correct, actual, expected, violations = validate_fixture(path, schemas)
        except (OSError, json.JSONDecodeError, Violation) as error:
            correct, actual, expected, violations = False, "ERROR", "?", [error]
        correct_count += correct
        label = "MATCH" if correct else "MISMATCH"
        print(f"[{label}] {path.relative_to(ROOT)} expected={expected} actual={actual}")
        if args.verbose or not correct:
            for error in violations:
                print(f"    {getattr(error, 'code', 'ERROR')}: {error}")
    print(f"RMTP v0.4: {correct_count}/{len(paths)} expectation matches")
    return 0 if correct_count == len(paths) else 1


if __name__ == "__main__":
    sys.exit(main())
