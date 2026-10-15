"""
app/models.py
SQLAlchemy ORM models mapped to the 12 normalized tables and 3 database views in crime_db.
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, DateTime, Date, 
    Boolean, Enum, ForeignKey, Numeric, JSON
)
from sqlalchemy.orm import relationship
from app.db import db


class PoliceStation(db.Model):
    __tablename__ = "police_stations"

    station_id = Column(Integer, primary_key=True, autoincrement=True)
    station_name = Column(String(100), unique=True, nullable=False)
    district_code = Column(String(10), unique=True, nullable=False)
    address = Column(String(200), nullable=False)
    phone = Column(String(25), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    users = relationship("User", back_populates="station")
    cases = relationship("Case", back_populates="station")

    def __repr__(self):
        return f"<PoliceStation {self.station_name} ({self.district_code})>"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(Integer, ForeignKey("police_stations.station_id"), nullable=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    role = Column(Enum("Admin", "Officer", "Investigator", name="user_role_enum"), default="Officer", nullable=False)
    full_name = Column(String(100), nullable=False)
    badge_number = Column(String(30), unique=True, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    station = relationship("PoliceStation", back_populates="users")
    created_cases = relationship("Case", back_populates="creator")
    assignments = relationship("CaseAssignment", back_populates="user")
    notes = relationship("InvestigationNote", back_populates="author")

    def get_id(self):
        return str(self.user_id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == "Admin"

    @property
    def is_investigator(self):
        return self.role in ("Investigator", "Admin")

    def __repr__(self):
        return f"<User {self.username} [{self.role}]>"


class Person(db.Model):
    __tablename__ = "persons"

    person_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(Enum("Male", "Female", "Non-Binary", "Unknown", name="person_gender_enum"), default="Unknown", nullable=False)
    phone_contact = Column(String(25), nullable=True)
    address_line = Column(String(200), nullable=True)
    is_fictional = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    case_participations = relationship("CasePerson", back_populates="person")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<Person {self.full_name}>"


class Case(db.Model):
    __tablename__ = "cases"

    case_id = Column(Integer, primary_key=True, autoincrement=True)
    case_number = Column(String(30), unique=True, nullable=False)
    station_id = Column(Integer, ForeignKey("police_stations.station_id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    case_type = Column(
        Enum("Homicide", "Robbery", "Assault", "Burglary", "Theft", "Narcotics", "Fraud", "Cybercrime", "Other", name="case_type_enum"),
        nullable=False
    )
    status = Column(
        Enum("Open", "Under Investigation", "Pending Review", "Closed", "Cold Case", name="case_status_enum"),
        default="Open", nullable=False
    )
    priority = Column(
        Enum("Low", "Medium", "High", "Critical", name="case_priority_enum"),
        default="Medium", nullable=False
    )
    incident_location = Column(String(200), nullable=False)
    date_reported = Column(DateTime, default=datetime.utcnow, nullable=False)
    date_closed = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    is_fictional = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    station = relationship("PoliceStation", back_populates="cases")
    creator = relationship("User", back_populates="created_cases")
    assignments = relationship("CaseAssignment", back_populates="case", cascade="all, delete-orphan")
    involved_persons = relationship("CasePerson", back_populates="case", cascade="all, delete-orphan")
    evidence_items = relationship("Evidence", back_populates="case", cascade="all, delete-orphan")
    notes = relationship("InvestigationNote", back_populates="case", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Case {self.case_number}: {self.title}>"


class CaseAssignment(db.Model):
    __tablename__ = "case_assignments"

    assignment_id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("cases.case_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    assignment_role = Column(
        Enum("Lead Investigator", "Assisting Officer", "Forensic Specialist", name="assign_role_enum"),
        default="Assisting Officer", nullable=False
    )
    assigned_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    unassigned_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    notes = Column(String(255), nullable=True)

    case = relationship("Case", back_populates="assignments")
    user = relationship("User", back_populates="assignments")

    def __repr__(self):
        return f"<Assignment {self.assignment_id}: User {self.user_id} -> Case {self.case_id}>"


class CasePerson(db.Model):
    __tablename__ = "case_persons"

    case_person_id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("cases.case_id"), nullable=False)
    person_id = Column(Integer, ForeignKey("persons.person_id"), nullable=False)
    role_in_case = Column(
        Enum("Suspect", "Victim", "Witness", "Person of Interest", "Reporting Party", name="person_role_enum"),
        nullable=False
    )
    statement_summary = Column(Text, nullable=True)
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    case = relationship("Case", back_populates="involved_persons")
    person = relationship("Person", back_populates="case_participations")

    def __repr__(self):
        return f"<CasePerson Case {self.case_id} Person {self.person_id} [{self.role_in_case}]>"


class Evidence(db.Model):
    __tablename__ = "evidence"

    evidence_id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("cases.case_id"), nullable=False)
    evidence_code = Column(String(50), unique=True, nullable=False)
    evidence_type = Column(
        Enum("Physical", "Digital", "Forensic", "Documentary", "Weapons", "Other", name="evidence_type_enum"),
        nullable=False
    )
    description = Column(Text, nullable=False)
    current_storage_location = Column(String(100), nullable=False)
    current_custody_status = Column(
        Enum("Collected", "In Analysis", "Vault Storage", "Court Presentation", "Disposed", name="custody_status_enum"),
        default="Collected", nullable=False
    )
    collected_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    collected_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    case = relationship("Case", back_populates="evidence_items")
    collector = relationship("User")
    custody_logs = relationship("EvidenceCustodyLog", back_populates="evidence", passive_deletes=True)

    def __repr__(self):
        return f"<Evidence {self.evidence_code}: {self.description[:30]}>"


class EvidenceCustodyLog(db.Model):
    __tablename__ = "evidence_custody_log"

    custody_id = Column(Integer, primary_key=True, autoincrement=True)
    evidence_id = Column(Integer, ForeignKey("evidence.evidence_id"), nullable=False)
    previous_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=False)
    from_location = Column(String(100), nullable=True)
    to_location = Column(String(100), nullable=False)
    handled_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    reason_for_transfer = Column(String(255), nullable=False)
    logged_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    evidence = relationship("Evidence", back_populates="custody_logs")
    handler = relationship("User")

    def __repr__(self):
        return f"<CustodyLog {self.custody_id} for Evidence {self.evidence_id}>"


class InvestigationNote(db.Model):
    __tablename__ = "investigation_notes"

    note_id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("cases.case_id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    note_title = Column(String(150), nullable=False)
    note_body = Column(Text, nullable=False)
    is_confidential = Column(Boolean, default=False, nullable=False)
    logged_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    case = relationship("Case", back_populates="notes")
    author = relationship("User", back_populates="notes")

    def __repr__(self):
        return f"<InvestigationNote {self.note_id}: {self.note_title}>"


class AuditLog(db.Model):
    __tablename__ = "audit_log"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    table_name = Column(String(50), nullable=False)
    record_id = Column(Integer, nullable=False)
    operation_type = Column(Enum("INSERT", "UPDATE", "DELETE", name="audit_op_enum"), nullable=False)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    performed_by = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<AuditLog {self.log_id}: {self.operation_type} on {self.table_name}>"


class IUCRCode(db.Model):
    __tablename__ = "iucr_codes"

    iucr_code = Column(String(10), primary_key=True)
    primary_type = Column(String(50), nullable=False)
    description = Column(String(120), nullable=False)
    fbi_code = Column(String(10), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<IUCR {self.iucr_code}: {self.primary_type}>"


class PublicCrimeIncident(db.Model):
    __tablename__ = "public_crime_incidents"

    incident_id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(BigInteger, unique=True, nullable=False)
    case_number = Column(String(25), nullable=True)
    incident_date = Column(DateTime, nullable=False)
    block = Column(String(120), nullable=True)
    source_iucr_code = Column(String(10), nullable=True)
    source_primary_type = Column(String(50), nullable=False)
    source_description = Column(String(120), nullable=True)
    canonical_iucr_code = Column(String(10), ForeignKey("iucr_codes.iucr_code"), nullable=True)
    location_description = Column(String(100), nullable=True)
    arrest_made = Column(Boolean, nullable=True)
    domestic = Column(Boolean, nullable=True)
    beat = Column(String(10), nullable=True)
    district = Column(String(10), nullable=True)
    ward = Column(Integer, nullable=True)
    community_area = Column(String(15), nullable=True)
    fbi_code = Column(String(10), nullable=True)
    latitude = Column(Numeric(11, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    incident_year = Column(Integer, nullable=False)
    updated_on = Column(DateTime, nullable=True)
    imported_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    canonical_iucr = relationship("IUCRCode")

    def __repr__(self):
        return f"<PublicCrimeIncident {self.source_id}: {self.source_primary_type} ({self.incident_year})>"


# -------------------------------------------------------------------------
# DATABASE VIEWS (Read-Only SQLAlchemy Mappings)
# -------------------------------------------------------------------------
class VCaseSummary(db.Model):
    __tablename__ = "v_case_summary"
    __table_args__ = {"info": {"is_view": True}}

    case_id = Column(Integer, primary_key=True)
    case_number = Column(String(30))
    title = Column(String(200))
    case_type = Column(String(50))
    status = Column(String(50))
    priority = Column(String(50))
    station_name = Column(String(100))
    district_code = Column(String(10))
    lead_investigator = Column(String(100))
    assigned_officer_count = Column(Integer)
    evidence_count = Column(Integer)
    days_elapsed = Column(Integer)
    date_reported = Column(DateTime)
    date_closed = Column(DateTime)


class VOfficerWorkload(db.Model):
    __tablename__ = "v_officer_workload"
    __table_args__ = {"info": {"is_view": True}}

    user_id = Column(Integer, primary_key=True)
    officer_name = Column(String(100))
    badge_number = Column(String(30))
    role = Column(String(50))
    station_name = Column(String(100))
    total_assigned_cases = Column(Integer)
    active_cases = Column(Integer)
    lead_investigator_cases = Column(Integer)
    critical_priority_cases = Column(Integer)


class VPublicIncidentTrends(db.Model):
    __tablename__ = "v_public_incident_trends"
    __table_args__ = {"info": {"is_view": True}}

    incident_year = Column(Integer, primary_key=True)
    district = Column(String(10), primary_key=True)
    source_primary_type = Column(String(50), primary_key=True)
    total_incidents = Column(Integer)
    arrests_made = Column(Integer)
    domestic_incidents = Column(Integer)
    arrest_rate_pct = Column(Numeric(5, 2))
