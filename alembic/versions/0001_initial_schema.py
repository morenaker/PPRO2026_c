"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-10-21
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ExcludeConstraint

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # btree_gist umožní v exclusion constraintu kombinovat "=" na doctor_id a "&&" na rozsahu.
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")

    op.create_table(
        "patient",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("birth_year", sa.Integer, nullable=False),
        sa.Column("phone", sa.String(30), nullable=False),
        sa.Column("insurance_number", sa.String(20), nullable=False),
        sa.Column("insurer", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("insurance_number", name="uq_patient_insurance_number"),
    )
    op.create_index("ix_patient_last_name", "patient", ["last_name"])
    op.create_index("ix_patient_phone", "patient", ["phone"])

    op.create_table(
        "doctor",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("full_name", sa.String(150), nullable=False),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.true()),
    )

    op.create_table(
        "office_hours",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("doctor_id", sa.Integer, sa.ForeignKey("doctor.id"), nullable=False),
        sa.Column("weekday", sa.Integer, nullable=False),
        sa.Column("start_time", sa.Time, nullable=False),
        sa.Column("end_time", sa.Time, nullable=False),
        sa.Column("location", sa.String(200), nullable=False, server_default="Ordinace Na Vyhlídce"),
        sa.Column("bookable", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.CheckConstraint("weekday BETWEEN 0 AND 6", name="ck_office_hours_weekday_range"),
        sa.CheckConstraint("end_time > start_time", name="ck_office_hours_time_order"),
    )
    op.create_index("ix_office_hours_doctor_id", "office_hours", ["doctor_id"])

    op.create_table(
        "procedure",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("points", sa.Integer, nullable=False),
        sa.Column("requires_quantity", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.UniqueConstraint("code", name="uq_procedure_code"),
        sa.CheckConstraint("points >= 0", name="ck_procedure_points_non_negative"),
    )

    op.create_table(
        "appointment",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("patient_id", sa.Integer, sa.ForeignKey("patient.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("doctor_id", sa.Integer, sa.ForeignKey("doctor.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reason", sa.String(500), nullable=False, server_default=""),
        sa.Column("status", sa.String(20), nullable=False, server_default="booked"),
        sa.Column("created_via", sa.String(20), nullable=False, server_default="reception"),
        sa.Column("cancelled_at", sa.DateTime(timezone=True)),
        sa.Column("cancel_reason", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("ends_at > starts_at", name="ck_appointment_time_order"),
        sa.CheckConstraint(
            "status IN ('booked', 'cancelled', 'completed')", name="ck_appointment_status_values"
        ),
        ExcludeConstraint(
            ("doctor_id", "="),
            (sa.text("tstzrange(starts_at, ends_at, '[)')"), "&&"),
            where=sa.text("status <> 'cancelled'"),
            using="gist",
            name="no_overlap_per_doctor",
        ),
    )
    op.create_index("ix_appointment_patient_id", "appointment", ["patient_id"])
    op.create_index("ix_appointment_doctor_id", "appointment", ["doctor_id"])

    op.create_table(
        "visit",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "appointment_id", sa.Integer, sa.ForeignKey("appointment.id", ondelete="RESTRICT"), nullable=False
        ),
        sa.Column("note", sa.String(1000), nullable=False, server_default=""),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("appointment_id", name="uq_visit_appointment_id"),
    )

    op.create_table(
        "visit_procedure",
        sa.Column("visit_id", sa.Integer, sa.ForeignKey("visit.id", ondelete="RESTRICT"), primary_key=True),
        sa.Column(
            "procedure_id", sa.Integer, sa.ForeignKey("procedure.id", ondelete="RESTRICT"), primary_key=True
        ),
        sa.Column("quantity", sa.Integer, nullable=False, server_default="1"),
        sa.CheckConstraint("quantity >= 1", name="ck_visit_procedure_quantity_positive"),
    )


def downgrade() -> None:
    for table in ("visit_procedure", "visit", "appointment", "procedure", "office_hours", "doctor", "patient"):
        op.drop_table(table)
