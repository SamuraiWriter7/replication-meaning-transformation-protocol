#!/usr/bin/env python3
"""RMTP v0.1 example conformance validator (schema + semantic checks)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = {
    "replication_intent": "replication-intent.schema.json",
    "meaning_conversion": "meaning-conversion.schema.json",
    "replication_plan": "replication-plan.schema.json",
}
OUTCOMES = {"NO_REPLICATION", "ALTERNATIVE_PROPOSED", "REPLICATION_PROPOSED", "HELD_FOR_REVIEW"}


class ValidationFailure(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationFailure(message)


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def load_schemas() -> dict[str, Draft202012Validator]:
    validators = {}
    for field, filename in SCHEMAS.items():
        path = ROOT / "schemas" / filename
        schema = load_json(path)
        Draft202012Validator.check_schema(schema)
        validators[field] = Draft202012Validator(schema)
        print(f"[schema-ok] {path.relative_to(ROOT)}")
    return validators


def check_schema(example: dict, validators: dict[str, Draft202012Validator]) -> None:
    for field in ("replication_intent", "meaning_conversion", "replication_plan"):
        if field not in example:
            continue
        errors = sorted(validators[field].iter_errors(example[field]), key=lambda err: (list(map(str, err.absolute_path)), err.message))
        if errors:
            err = errors[0]
            path = ".".join(map(str, err.absolute_path)) or "<root>"
            raise ValidationFailure(f"SCHEMA {field}.{path}: {err.message}")


def check_semantics(example: dict) -> None:
    require(example.get("schema_version") == "0.1.0", "EXAMPLE: schema_version must be 0.1.0")
    intent = example.get("replication_intent")
    conversion = example.get("meaning_conversion")
    require(isinstance(intent, dict) and isinstance(conversion, dict), "EXAMPLE: intent and conversion are required")
    require(conversion["intent_ref"] == intent["intent_id"], "REFERENCE: intent_ref mismatch")
    require(intent.get("parent_id", intent["requester_id"]) == intent["requester_id"], "REFERENCE: parent_id must equal requester_id in v0.1")

    assessment = conversion["deficit_assessment"]
    evidence = assessment["evidence_refs"]
    if assessment["verification_status"] == "verified":
        require(bool(evidence), "EVIDENCE: verified assessment requires evidence_refs")
        require(intent["observed_deficit_ref"] in evidence, "EVIDENCE: observed_deficit_ref not in evidence_refs")
    if assessment["deficit_type"] == "none":
        require(assessment["necessity"] == "not_required", "NECESSITY: no deficit implies not_required")
    if assessment["necessity"] == "required":
        require(assessment["deficit_type"] not in ("none", "unknown"), "NECESSITY: required must identify a deficit")

    alternatives = conversion["evaluated_alternatives"]
    IDs = [item["alternative_id"] for item in alternatives]
    require(len(IDs) == len(set(IDs)), "ALTERNATIVE: duplicate alternative_id")
    require(any(item["strategy"] == "no_replication" for item in alternatives), "ALTERNATIVE: missing no_replication assessment")
    outcome = conversion["selected_outcome"]
    require(outcome in OUTCOMES, "OUTCOME: unsupported outcome")
    selected = conversion.get("selected_alternative_ref")
    matched = [item for item in alternatives if item["alternative_id"] == selected] if selected else []
    if selected is not None:
        require(len(matched) == 1, "ALTERNATIVE: selected_alternative_ref not found")
        require(matched[0]["feasible"], "ALTERNATIVE: selected alternative is infeasible")

    plan = example.get("replication_plan")
    if outcome == "REPLICATION_PROPOSED":
        require(assessment["verification_status"] == "verified" and assessment["necessity"] == "required", "RMTP-INV-008: unverified or unnecessary replication")
        require(bool(evidence), "RMTP-INV-008: missing deficit evidence")
        require(matched and matched[0]["strategy"] == "bounded_replication", "ALTERNATIVE: bounded_replication must be selected")
        authority = conversion["authority_assessment"]
        require(authority["status"] == "within_scope", "AUTHORITY: replication requires within_scope")
        require(authority["authority_ref"] not in {intent["requester_id"], intent.get("parent_id")}, "RMTP-INV-004: self-authorized replication")
        require(plan is not None, "PLAN: REPLICATION_PROPOSED requires a plan")
        require(plan["conversion_ref"] == conversion["conversion_id"], "REFERENCE: conversion_ref mismatch")
        require(plan["authority_ref"] == authority["authority_ref"], "REFERENCE: authority_ref mismatch")
        require(plan["parent_id"] == intent.get("parent_id", intent["requester_id"]), "REFERENCE: plan parent_id mismatch")
        require(plan["proposed_instances"] == conversion["proposed_instance_count"], "RMTP-INV-003: plan instance count differs from conversion")
        require(plan["proposed_instances"] <= intent["requested_instances"], "RMTP-INV-003: plan exceeds requested instances")
        require(plan.get("minimum_sufficient") is True and "minimum_sufficient_evidence_ref" in plan, "RMTP-INV-003: minimum sufficient claim/evidence missing")
        require(plan["minimum_sufficient_evidence_ref"] in evidence, "RMTP-INV-003: minimum sufficient evidence not referenced")
        records = plan["lineage_records"]
        require(len(records) == plan["proposed_instances"], "RMTP-INV-006: lineage count mismatch")
        offspring_ids = [r["offspring_id"] for r in records]
        lineage_refs = [r["lineage_ref"] for r in records]
        require(len(offspring_ids) == len(set(offspring_ids)), "RMTP-INV-006: duplicate offspring IDs")
        require(len(lineage_refs) == len(set(lineage_refs)), "RMTP-INV-006: duplicate lineage refs")
        for record in records:
            require(record["parent_id"] == plan["parent_id"], "RMTP-INV-006: offspring parent mismatch")
            require(record["authority_ref"] == plan["authority_ref"], "RMTP-INV-006: offspring authority mismatch")
        concurrency = plan["resource_limits"].get("max_concurrent_instances")
        if concurrency is not None:
            require(concurrency >= plan["proposed_instances"], "RESOURCE: concurrency below planned simultaneous instances")
        require(plan["lifetime"]["expiration_enforced_by"] == plan["retirement_conditions"]["termination_controller_ref"], "RMTP-INV-005: termination controller mismatch")
        require(plan["execution_authorized"] is False, "RMTP-INV-009: unauthorized execution")
    else:
        require(plan is None, "PLAN: non-replication outcome must not include replication_plan")
        require("proposed_instance_count" not in conversion, "PLAN: non-replication outcome cannot specify instance count")
        if outcome == "NO_REPLICATION":
            require(assessment["necessity"] == "not_required", "NECESSITY: NO_REPLICATION requires not_required")
            require(matched and matched[0]["strategy"] == "no_replication", "ALTERNATIVE: NO_REPLICATION must select no_replication")
        elif outcome == "ALTERNATIVE_PROPOSED":
            require(matched and matched[0]["strategy"] not in {"no_replication", "bounded_replication"}, "ALTERNATIVE: expected non-replication strategy")
        elif outcome == "HELD_FOR_REVIEW":
            auth = conversion.get("authority_assessment", {})
            require(assessment["verification_status"] != "verified" or assessment["necessity"] == "undetermined" or auth.get("status") != "within_scope", "REVIEW: hold requires unresolved condition")
            if selected:
                require(matched and matched[0]["strategy"] == "no_replication", "REVIEW: interim selection must be no_replication")


def run(paths: list[Path], validators: dict[str, Draft202012Validator]) -> int:
    matched_count = 0
    for path in paths:
        relative = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
        expected = None
        try:
            example = load_json(path)
            expected = example.get("expected_result")
            require(expected in {"PASS", "FAIL"}, "EXAMPLE: expected_result must be PASS or FAIL")
            check_schema(example, validators)
            check_semantics(example)
            actual, reason = "PASS", "validated"
        except (ValidationFailure, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            actual, reason = "FAIL", str(exc)
        matched = expected == actual
        print(f"[{'MATCH' if matched else 'MISMATCH'}] {relative} expected={expected} actual={actual} — {reason}")
        matched_count += int(matched)
    print(f"\nRMTP v0.1: {matched_count}/{len(paths)} expectations matched")
    return 0 if matched_count == len(paths) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="Optional individual example files")
    args = parser.parse_args()
    print("=== RMTP v0.1 validation ===")
    try:
        validators = load_schemas()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[fatal] Cannot load schemas: {exc}", file=sys.stderr)
        return 2
    paths = args.paths or sorted((ROOT / "examples" / "v0.1").glob("*/*.json"))
    if not paths:
        print("[fatal] No example files found", file=sys.stderr)
        return 2
    return run(paths, validators)


if __name__ == "__main__":
    sys.exit(main())
