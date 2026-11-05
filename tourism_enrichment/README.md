# Tourism enrichment Phase 1

Isolated, read-only candidate quality gate. Does not connect to Railway or publish records.

Run: `python -m unittest discover -s tests -p test_tourism_quality_gate.py`

Dry-run: `python -m tourism_enrichment.quality_gate candidates.json --existing existing.json`

Input JSON arrays require name_th, province, latitude, longitude, source, source_id, source_url. Every candidate requires human review. Coordinates are checked against a broad Thailand bounding box, not precise province boundaries. Duplicate checks use source identity or identical normalized name within 300 meters. No image license verification, source ingestion, AI text generation, or production database writes are included yet.
