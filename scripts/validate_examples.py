#!/usr/bin/env python3
"""RMTP v0.1/v0.2 conformance: JSON Schemas, semantics, expected results."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = {
    "replication_intent": "replication-intent.schema.json",
    "meaning_conversion": "meaning-conversion.schema.json",
    "replication_plan": "replication-plan.schema.json",
    "structural_evidence": "structural-evidence-v0.2.schema.json",
    "authority_envelope": "authority-envelope-v0.2.schema.json",
    "verification_bundle": "verification-bundle-v0.2.schema.json",
}
EXPECTED = {
    "v0.1": {
        "pass": {
            "bounded-worker-replication.json", "no-replication-required.json",
            "alternative-load-redistribution.json", "held-for-review.json",
        },
        "fail": {
            "unverified-deficit-replication.json", "self-authorized-replication.json",
            "missing-retirement-condition.json", "lineage-count-mismatch.json",
            "excessive-replication-count.json",
        },
    },
    "v0.2": {
        "pass": {
            "verified-bounded-replication.json", "authority-limit-respected.json",
            "no-replication-verified.json", "verification-held.json",
        },
        "fail": {
            "expired-evidence.json", "self-issued-authority.json",
            "revoked-authority.json", "authority-instance-limit-exceeded.json",
            "evidence-reference-mismatch.json",
            "verification-bundle-reference-mismatch.json",
        },
    },
}


class ValidationFailure(Exception):
    """Conformance rule was violated."""


def ensure(condition: bool, rule: str) -> None:
    if not condition:
        raise ValidationFailure(rule)


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as stream:
        data = json.load(stream)
    ensure(isinstance(data, dict), f"JSON: expected object in {path}")
    return data


def schemas() -> dict[str, Draft202012Validator]:
    result = {}
    for field, name in SCHEMAS.items():
        path = ROOT / "schemas" / name
        schema = load_json(path)
        Draft202012Validator.check_schema(schema)
        result[field] = Draft202012Validator(schema, format_checker=FormatChecker())
        print(f"[schema-ok] {path.relative_to(ROOT)}")
    return result


def validate_schema(field: str, value: object, validators: dict) -> None:
    errors = list(validators[field].iter_errors(value))
    if errors:
        error = sorted(errors, key=lambda e: (tuple(map(str, e.absolute_path)), e.message))[0]
        location = ".".join(map(str, error.absolute_path)) or "<root>"
        raise ValidationFailure(f"SCHEMA {field}.{location}: {error.message}")


def schema_checks(data: dict, validators: dict) -> None:
    for field in ("replication_intent", "meaning_conversion", "replication_plan",
                  "authority_envelope", "verification_bundle"):
        if field in data:
            validate_schema(field, data[field], validators)
    if data["schema_version"] == "0.2.0":
        records = data.get("structural_evidence")
        ensure(isinstance(records, list) and records,
               "RMTP-EV-001: structural_evidence records required")
        for record in records:
            validate_schema("structural_evidence", record, validators)
        ensure("authority_envelope" in data and "verification_bundle" in data,
               "RMTP-INV-016: v0.2 authority_envelope and verification_bundle required")


def utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    ensure(parsed.tzinfo is not None and parsed.utcoffset() is not None,
           "TIME: timestamp must include timezone")
    return parsed.astimezone(timezone.utc)


def unique(values: list, rule: str) -> None:
    ensure(len(values) == len(set(values)), rule)


def common_semantics(data: dict) -> None:
    intent = data["replication_intent"]
    conversion = data["meaning_conversion"]
    ensure(conversion["intent_ref"] == intent["intent_id"],
           "RMTP-INV-016: conversion intent reference mismatch")
    ensure(intent.get("parent_id", intent["requester_id"]) == intent["requester_id"],
           "REFERENCE: v0.1 parent_id must match requester_id")
    deficit = conversion["deficit_assessment"]
    refs = deficit["evidence_refs"]
    if deficit["verification_status"] == "verified":
        ensure(refs and intent["observed_deficit_ref"] in refs,
               "RMTP-INV-008: verified deficit requires referenced evidence")
    if deficit["deficit_type"] == "none":
        ensure(deficit["necessity"] == "not_required",
               "NECESSITY: no deficit requires not_required")
    if deficit["necessity"] == "required":
        ensure(deficit["deficit_type"] not in ("none", "unknown"),
               "NECESSITY: required needs concrete deficit")

    alternatives = conversion["evaluated_alternatives"]
    unique([a["alternative_id"] for a in alternatives], "ALTERNATIVE: duplicate IDs")
    ensure(any(a["strategy"] == "no_replication" for a in alternatives),
           "ALTERNATIVE: no_replication must be evaluated")
    chosen_id = conversion.get("selected_alternative_ref")
    matches = [a for a in alternatives if a["alternative_id"] == chosen_id]
    if chosen_id is not None:
        ensure(len(matches) == 1 and matches[0]["feasible"],
               "ALTERNATIVE: selected alternative missing or infeasible")
    chosen = matches[0]["strategy"] if matches else None
    outcome = conversion["selected_outcome"]
    plan = data.get("replication_plan")
    if outcome == "REPLICATION_PROPOSED":
        ensure(deficit["verification_status"] == "verified" and
               deficit["necessity"] == "required" and bool(refs),
               "RMTP-INV-008: replication lacks verified necessity")
        ensure(chosen == "bounded_replication", "ALTERNATIVE: bounded_replication not selected")
        authority = conversion["authority_assessment"]
        ensure(authority["status"] == "within_scope", "AUTHORITY: status not within_scope")
        ensure(authority["authority_ref"] not in (intent["requester_id"], intent.get("parent_id")),
               "RMTP-INV-004: self-authorization")
        ensure(plan is not None, "PLAN: proposed replication requires a plan")
        ensure(plan["conversion_ref"] == conversion["conversion_id"],
               "RMTP-INV-016: plan conversion reference mismatch")
        ensure(plan["authority_ref"] == authority["authority_ref"],
               "RMTP-INV-016: plan authority reference mismatch")
        ensure(plan["parent_id"] == intent.get("parent_id", intent["requester_id"]),
               "RMTP-INV-006: plan parent mismatch")
        count = plan["proposed_instances"]
        ensure(count == conversion["proposed_instance_count"] and count <= intent["requested_instances"],
               "RMTP-INV-003: excessive or inconsistent replication count")
        ensure(plan.get("minimum_sufficient") is True and
               plan.get("minimum_sufficient_evidence_ref") in refs,
               "RMTP-INV-003: minimum sufficiency reference missing")
        lineage = plan["lineage_records"]
        ensure(len(lineage) == count, "RMTP-INV-006: lineage count mismatch")
        unique([r["offspring_id"] for r in lineage], "RMTP-INV-006: duplicate offspring ID")
        unique([r["lineage_ref"] for r in lineage], "RMTP-INV-006: duplicate lineage reference")
        for child in lineage:
            ensure(child["parent_id"] == plan["parent_id"], "RMTP-INV-006: lineage parent mismatch")
            ensure(child["authority_ref"] == plan["authority_ref"],
                   "RMTP-INV-006: lineage authority mismatch")
        concurrent = plan["resource_limits"].get("max_concurrent_instances")
        if concurrent is not None:
            ensure(concurrent >= count, "RESOURCE: concurrency below proposed simultaneous count")
        ensure(plan["lifetime"]["expiration_enforced_by"] ==
               plan["retirement_conditions"]["termination_controller_ref"],
               "RMTP-INV-005: termination controller mismatch")
        ensure(plan["execution_authorized"] is False, "RMTP-INV-009: execution authorization forbidden")
    else:
        ensure(plan is None and "proposed_instance_count" not in conversion,
               "PLAN: non-replication outcome cannot contain a replication plan/count")
        if outcome == "NO_REPLICATION":
            ensure(deficit["necessity"] == "not_required" and chosen == "no_replication",
                   "NECESSITY: NO_REPLICATION must select no_replication with not_required")
        elif outcome == "ALTERNATIVE_PROPOSED":
            ensure(chosen not in (None, "no_replication", "bounded_replication"),
                   "ALTERNATIVE: non-replication alternative required")
        elif outcome == "HELD_FOR_REVIEW":
            auth = conversion.get("authority_assessment", {})
            ensure(deficit["verification_status"] != "verified" or
                   deficit["necessity"] == "undetermined" or auth.get("status") != "within_scope",
                   "REVIEW: no unresolved condition")
            if chosen_id is not None:
                ensure(chosen == "no_replication", "REVIEW: interim choice must be no_replication")


def v02_semantics(data: dict) -> None:
    intent = data["replication_intent"]
    conversion = data["meaning_conversion"]
    authority = data["authority_envelope"]
    bundle = data["verification_bundle"]
    plan = data.get("replication_plan")
    evidence = data["structural_evidence"]
    checked = utc(bundle["verification_time"])
    evidence_ids = [r["evidence_id"] for r in evidence]
    unique(evidence_ids, "RMTP-EV-001: duplicate evidence IDs")
    ensure(set(evidence_ids) == set(bundle["evidence_refs"]) ==
           set(conversion["deficit_assessment"]["evidence_refs"]),
           "RMTP-INV-016: evidence reference mismatch")
    ensure(intent["observed_deficit_ref"] in evidence_ids,
           "RMTP-EV-006: intent observation not in evidence")
    ensure(bundle["intent_ref"] == intent["intent_id"] and
           bundle["conversion_ref"] == conversion["conversion_id"],
           "RMTP-INV-016: bundle intent or conversion reference mismatch")
    ensure(bundle["authority_ref"] == authority["authority_id"],
           "RMTP-INV-016: bundle authority reference mismatch")
    if plan is None:
        ensure("plan_ref" not in bundle, "RMTP-INV-016: unexpected plan_ref")
    else:
        ensure(bundle.get("plan_ref") == plan["plan_id"],
               "RMTP-INV-016: bundle plan reference mismatch")
    ensure(conversion.get("authority_assessment", {}).get("authority_ref", authority["authority_id"])
           == authority["authority_id"], "RMTP-INV-016: conversion authority mismatch")
    ensure(bundle["execution_authorized"] is False,
           "RMTP-INV-018: verification cannot authorize execution")

    evidence_state = "PASS"
    for record in evidence:
        ensure(record["subject_id"] == intent["requester_id"],
               "RMTP-EV-006: evidence subject mismatch")
        ensure(record["deficit_type"] == conversion["deficit_assessment"]["deficit_type"],
               "RMTP-EV-006: evidence deficit type mismatch")
        ensure(record["observer_id"] != record["verifier_id"] and
               record["verifier_id"] != intent["requester_id"],
               "RMTP-EV-003: independent verifier identity required")
        start, end = utc(record["observed_at"]), utc(record["expires_at"])
        ensure(start < end, "RMTP-EV-004: invalid evidence interval")
        ensure(start <= checked < end, "RMTP-INV-012: evidence expired or not yet valid")
        status = record["verification_status"]
        if status == "rejected":
            evidence_state = "FAIL"
        elif status == "inconclusive" and evidence_state != "FAIL":
            evidence_state = "HELD"
        if status == "verified":
            ensure(bool(record.get("verification_ref")),
                   "RMTP-EV-003: verified evidence missing verification_ref")
    ensure(bundle["evidence_result"] == evidence_state,
           "RMTP-INV-017: incorrect evidence_result")
    assessment = conversion["deficit_assessment"]["verification_status"]
    if evidence_state == "PASS":
        ensure(assessment == "verified", "RMTP-INV-011: conversion evidence status mismatch")
    elif evidence_state == "HELD":
        ensure(assessment != "verified", "RMTP-INV-017: inconclusive evidence declared verified")

    ensure(authority["subject_id"] == intent["requester_id"],
           "RMTP-AV-002: authority subject mismatch")
    ensure(authority["issuer_id"] != intent["requester_id"] and
           authority["issuer_id"] != authority["subject_id"],
           "RMTP-AV-001: self-issued authority")
    valid_from, valid_until = utc(authority["valid_from"]), utc(authority["valid_until"])
    ensure(valid_from < valid_until, "RMTP-AV-005: invalid authority interval")
    status = authority["revocation_status"]
    if status in ("revoked", "expired") or not valid_from <= checked < valid_until:
        authority_state = "FAIL"
    elif status == "unknown":
        authority_state = "HELD"
    else:
        authority_state = "PASS"
    if plan is not None:
        if intent.get("target_scope") not in authority["allowed_scope"] or \
           "bounded_replication" not in authority["allowed_actions"] or \
           plan["proposed_instances"] > authority["max_instances"]:
            authority_state = "FAIL"
    else:
        if "replication_review" not in authority["allowed_actions"] or \
           intent.get("target_scope") not in authority["allowed_scope"]:
            authority_state = "FAIL"
    ensure(bundle["authority_result"] == authority_state,
           "RMTP-INV-015: incorrect authority_result")
    expected_overall = ("FAIL" if "FAIL" in (evidence_state, authority_state)
                        else "HELD" if "HELD" in (evidence_state, authority_state)
                        else "PASS")
    ensure(bundle["overall_result"] == expected_overall,
           "RMTP-INV-017: incorrect overall_result")
    if expected_overall == "HELD":
        ensure(conversion["selected_outcome"] == "HELD_FOR_REVIEW" and plan is None,
               "RMTP-INV-017: HELD requires no replication plan")
    if expected_overall == "PASS" and plan is not None:
        ensure(conversion["selected_outcome"] == "REPLICATION_PROPOSED",
               "RMTP-INV-016: plan requires REPLICATION_PROPOSED")
    # Format and identity checks do NOT authenticate synthetic attestations.
    if expected_overall == "PASS":
        ensure(bundle.get("verification_method") is not None and
               bool(bundle.get("verification_records")),
               "RMTP-INV-017: PASS requires verification metadata")


def check_file(path: Path, validators: dict) -> tuple[str, str, str | None]:
    expected = None
    try:
        data = load_json(path)
        expected = data.get("expected_result")
        ensure(expected in ("PASS", "FAIL"), "EXAMPLE: expected_result must be PASS or FAIL")
        version = data.get("schema_version")
        ensure(version in ("0.1.0", "0.2.0"), "EXAMPLE: unsupported schema_version")
        ensure("replication_intent" in data and "meaning_conversion" in data,
               "EXAMPLE: intent and conversion required")
        schema_checks(data, validators)
        common_semantics(data)
        if version == "0.2.0":
            v02_semantics(data)
        return "PASS", "validated", expected
    except (ValidationFailure, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        return "FAIL", str(exc), expected


def discover() -> list[Path]:
    paths = []
    missing = []
    for version, groups in EXPECTED.items():
        for group, filenames in groups.items():
            folder = ROOT / "examples" / version / group
            for filename in sorted(filenames):
                path = folder / filename
                if path.is_file():
                    paths.append(path)
                else:
                    missing.append(path.relative_to(ROOT).as_posix())
            extras = sorted(set(p.name for p in folder.glob("*.json")) - filenames)
            for name in extras:
                missing.append(f"unexpected fixture: {version}/{group}/{name}")
    if missing:
        raise ValidationFailure("FIXTURE inventory mismatch:\n  " + "\n  ".join(missing))
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path,
                        help="Individual fixtures (disables full inventory requirement)")
    args = parser.parse_args()
    print("=== RMTP v0.1 + v0.2 validation ===")
    try:
        validators = schemas()
        paths = args.paths if args.paths else discover()
        ensure(bool(paths), "FIXTURE: no examples found")
    except (ValidationFailure, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[fatal] {exc}", file=sys.stderr)
        return 2
    matches = 0
    for path in paths:
        actual, reason, expected = check_file(path, validators)
        name = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
        # The directory is an independent expectation; detect accidental label changes.
        if not args.paths:
            expected_by_directory = "PASS" if path.parent.name == "pass" else "FAIL"
            if expected != expected_by_directory:
                print(f"[MISMATCH] {name} expected_result conflicts with directory")
                continue
        matched = actual == expected
        matches += matched
        print(f"[{'MATCH' if matched else 'MISMATCH'}] {name} "
              f"expected={expected} actual={actual} -- {reason}")
    print(f"\nRMTP v0.1 + v0.2: {matches}/{len(paths)} expectations matched")
    return 0 if matches == len(paths) else 1


if __name__ == "__main__":
    sys.exit(main())
