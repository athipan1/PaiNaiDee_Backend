from datetime import datetime, timedelta

from flask import Blueprint, request

from ...models import db
from ...models.external_data import DataSource, ManualUpdate, ScheduledUpdate
from ...utils.response import standardized_response

external_data_bp = Blueprint("external_data", __name__)

VALID_FREQUENCIES = ["hourly", "daily", "weekly", "monthly"]


@external_data_bp.route("/external-data/sources", methods=["GET"])
def get_data_sources():
    """Get all data sources"""
    try:
        sources = DataSource.query.all()
        return standardized_response(
            data=[source.to_dict() for source in sources],
            message="Data sources retrieved successfully",
        )
    except Exception:
        return standardized_response(
            message="Failed to retrieve data sources", success=False, status_code=500
        )


@external_data_bp.route("/external-data/configure", methods=["POST"])
def configure_data_source():
    """Configure a new data source or update existing one"""
    try:
        data = request.get_json()

        if not data:
            return standardized_response(
                message="Request body is required", success=False, status_code=422
            )

        # Required fields validation
        required_fields = ["name", "type"]
        missing_fields = [
            field for field in required_fields if field not in data or not data[field]
        ]

        if missing_fields:
            return standardized_response(
                message=f"Missing required fields: {', '.join(missing_fields)}",
                success=False,
                status_code=422,
            )

        # Validate type
        valid_types = ["api", "database", "file"]
        if data["type"] not in valid_types:
            return standardized_response(
                message=f"Invalid type. Must be one of: {', '.join(valid_types)}",
                success=False,
                status_code=422,
            )

        # Check if data source with same name already exists
        existing_source = DataSource.query.filter_by(name=data["name"]).first()
        if existing_source and (
            "id" not in data or existing_source.id != data.get("id")
        ):
            return standardized_response(
                message="Data source with this name already exists",
                success=False,
                status_code=422,
            )

        # Create or update data source
        if data.get("id"):
            source = db.session.get(DataSource, data["id"])
            if not source:
                return standardized_response(
                    message="Data source not found", success=False, status_code=404
                )
        else:
            source = DataSource()

        source.name = data["name"]
        source.type = data["type"]
        source.endpoint_url = data.get("endpoint_url")
        source.configuration = data.get("configuration", {})
        source.is_active = data.get("is_active", True)
        source.updated_at = datetime.utcnow()

        if not source.id:  # New source
            db.session.add(source)

        db.session.commit()

        return standardized_response(
            data=source.to_dict(), message="Data source configured successfully"
        )

    except Exception:
        db.session.rollback()
        return standardized_response(
            message="Failed to configure data source", success=False, status_code=500
        )


@external_data_bp.route("/external-data/trigger-update", methods=["POST"])
def trigger_manual_update():
    """Trigger a manual update for a data source"""
    try:
        data = request.get_json()

        if not data or "data_source_id" not in data:
            return standardized_response(
                message="data_source_id is required", success=False, status_code=422
            )

        data_source_id = data["data_source_id"]

        # Validate data source exists and is active
        data_source = db.session.get(DataSource, data_source_id)
        if not data_source:
            return standardized_response(
                message="Data source not found", success=False, status_code=404
            )

        if not data_source.is_active:
            return standardized_response(
                message="Cannot trigger update for inactive data source",
                success=False,
                status_code=422,
            )

        # Create manual update record
        manual_update = ManualUpdate(
            data_source_id=data_source_id,
            triggered_by=data.get("triggered_by", "system"),
            status="pending",
        )

        db.session.add(manual_update)
        db.session.commit()

        # Here you would typically trigger the actual update process
        # For now, we'll just simulate immediate completion
        manual_update.status = "completed"
        manual_update.completed_at = datetime.utcnow()
        manual_update.records_processed = data.get("expected_records", 0)
        db.session.commit()

        return standardized_response(
            data=manual_update.to_dict(), message="Manual update triggered successfully"
        )

    except Exception:
        db.session.rollback()
        return standardized_response(
            message="Failed to trigger manual update", success=False, status_code=500
        )


@external_data_bp.route("/external-data/scheduled-update", methods=["POST"])
def create_scheduled_update():
    """Create a scheduled update for a data source"""
    try:
        data = request.get_json()

        if not data:
            return standardized_response(
                message="Request body is required", success=False, status_code=422
            )

        # Required fields validation
        required_fields = ["data_source_id", "frequency"]
        missing_fields = [
            field
            for field in required_fields
            if field not in data or data[field] is None
        ]

        if missing_fields:
            return standardized_response(
                message=f"Missing required fields: {', '.join(missing_fields)}",
                success=False,
                status_code=422,
            )

        # Validate frequency
        frequency = data["frequency"]
        if frequency not in VALID_FREQUENCIES:
            return standardized_response(
                message=f"Invalid frequency. Must be one of: {', '.join(VALID_FREQUENCIES)}",
                success=False,
                status_code=422,
            )

        data_source_id = data["data_source_id"]

        # Validate data source exists
        data_source = db.session.get(DataSource, data_source_id)
        if not data_source:
            return standardized_response(
                message="Data source not found", success=False, status_code=404
            )

        # Check if scheduled update already exists for this data source
        existing_schedule = ScheduledUpdate.query.filter_by(
            data_source_id=data_source_id, is_active=True
        ).first()

        if existing_schedule:
            return standardized_response(
                message="Active scheduled update already exists for this data source",
                success=False,
                status_code=422,
            )

        # Calculate next run time based on frequency
        now = datetime.utcnow()
        if frequency == "hourly":
            next_run = now + timedelta(hours=1)
        elif frequency == "daily":
            next_run = now + timedelta(days=1)
        elif frequency == "weekly":
            next_run = now + timedelta(weeks=1)
        elif frequency == "monthly":
            next_run = now + timedelta(days=30)

        # Create scheduled update
        scheduled_update = ScheduledUpdate(
            data_source_id=data_source_id,
            frequency=frequency,
            is_active=data.get("is_active", True),
            next_run=next_run,
        )

        db.session.add(scheduled_update)
        db.session.commit()

        return standardized_response(
            data=scheduled_update.to_dict(),
            message="Scheduled update created successfully",
        )

    except Exception:
        db.session.rollback()
        return standardized_response(
            message="Failed to create scheduled update", success=False, status_code=500
        )


@external_data_bp.route(
    "/external-data/scheduled-update/<int:schedule_id>", methods=["DELETE"]
)
def delete_scheduled_update(schedule_id):
    """Delete a scheduled update"""
    try:
        scheduled_update = db.session.get(ScheduledUpdate, schedule_id)
        if not scheduled_update:
            return standardized_response(
                message="Scheduled update not found", success=False, status_code=404
            )

        db.session.delete(scheduled_update)
        db.session.commit()

        return standardized_response(message="Scheduled update deleted successfully")

    except Exception:
        db.session.rollback()
        return standardized_response(
            message="Failed to delete scheduled update", success=False, status_code=500
        )
