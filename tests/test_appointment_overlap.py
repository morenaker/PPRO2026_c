"""Klientův tvrdý požadavek: dvě rezervace na stejný termín u stejného lékaře nesmí jít založit."""
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Appointment, Doctor, Patient


def _setup(session):
    doctor = Doctor(full_name="MUDr. Test")
    patient = Patient(
        first_name="A", last_name="B", birth_year=1990, phone="1", insurance_number="1", insurer="111"
    )
    session.add_all([doctor, patient])
    session.flush()
    return doctor, patient


def _appt(doctor, patient, start, minutes=15, status="booked"):
    return Appointment(
        doctor_id=doctor.id,
        patient_id=patient.id,
        starts_at=start,
        ends_at=start + timedelta(minutes=minutes),
        status=status,
    )


START = datetime(2026, 11, 2, 9, 0, tzinfo=timezone.utc)


def test_overlapping_appointments_are_rejected_by_database(session):
    doctor, patient = _setup(session)
    session.add(_appt(doctor, patient, START))
    session.flush()

    session.add(_appt(doctor, patient, START + timedelta(minutes=10)))
    with pytest.raises(IntegrityError):
        session.flush()


def test_back_to_back_appointments_are_allowed(session):
    doctor, patient = _setup(session)
    session.add_all([_appt(doctor, patient, START), _appt(doctor, patient, START + timedelta(minutes=15))])
    session.flush()


def test_cancelled_appointment_frees_the_slot(session):
    doctor, patient = _setup(session)
    session.add(_appt(doctor, patient, START, status="cancelled"))
    session.add(_appt(doctor, patient, START))
    session.flush()
