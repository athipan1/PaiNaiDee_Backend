"""Safe, dependency-free tourism candidate quality gate. No production writes."""
from dataclasses import dataclass, asdict
from math import radians, sin, cos, asin, sqrt
import json
import re
import sys
import unicodedata


def normalize_name(value):
    value = unicodedata.normalize("NFKC", str(value or "")).casefold()
    return re.sub(r"\\s+", " ", value).strip()


def distance_m(a, b):
    lat1, lon1, lat2, lon2 = map(radians, (a["latitude"], a["longitude"], b["latitude"], b["longitude"]))
    dlat, dlon = lat2-lat1, lon2-lon1
    return 12742000 * asin(min(1, sqrt(sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2)))


def valid_coordinates(item):
    try:
        lat, lon = float(item["latitude"]), float(item["longitude"])
        return 5.0 <= lat <= 21.0 and 97.0 <= lon <= 106.0
    except (ValueError, TypeError, KeyError):
        return False


def assess(candidates, existing=()):
    """Return candidate decisions without persisting or publishing anything."""
    seen = []
    decisions = []
    for item in candidates:
        issues = []
        name = normalize_name(item.get("name_th"))
        if not name:
            issues.append("missing_thai_name")
        if not valid_coordinates(item):
            issues.append("invalid_thailand_coordinates")
        if not item.get("source") or not item.get("source_id"):
            issues.append("missing_source_identity")
        if not item.get("source_url"):
            issues.append("missing_source_url")
        if not item.get("province"):
            issues.append("missing_province")
        for other in [*existing, *seen]:
            if item.get("source") and item.get("source_id") and item.get("source") == other.get("source") and item.get("source_id") == other.get("source_id"):
                issues.append("duplicate_source_id")
                break
            if name and name == normalize_name(other.get("name_th")) and valid_coordinates(item) and valid_coordinates(other):
                if distance_m(item, other) <= 300:
                    issues.append("possible_duplicate_name_location")
                    break
        status = "rejected" if "invalid_thailand_coordinates" in issues or "missing_thai_name" in issues else "needs_review"
        # Human verification required for all external candidates in phase 1.
        decisions.append({"source": item.get("source"), "source_id": item.get("source_id"), "name_th": item.get("name_th"), "status": status, "issues": issues})
        if not issues:
            seen.append(item)
    return {"total": len(decisions), "approved": 0, "needs_review": sum(d["status"] == "needs_review" for d in decisions), "rejected": sum(d["status"] == "rejected" for d in decisions), "decisions": decisions}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Tourism candidates dry-run; no database writes")
    parser.add_argument("candidates", help="JSON array of candidates")
    parser.add_argument("--existing", help="Optional JSON array of existing places")
    args = parser.parse_args()
    with open(args.candidates, encoding="utf-8") as f:
        candidates = json.load(f)
    with open(args.existing, encoding="utf-8") as f:
        existing = json.load(f) if args.existing else []
    if not isinstance(candidates, list) or not isinstance(existing, list):
        parser.error("JSON inputs must be arrays")
    print(json.dumps(assess(candidates, existing), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
