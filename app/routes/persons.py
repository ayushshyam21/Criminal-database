"""
app/routes/persons.py
Fictional person management (Suspects, Victims, Witnesses, Persons of Interest).
Strictly enforces is_fictional = TRUE.
"""
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_
from app.db import db
from app.models import Person, CasePerson
from app.services.security_service import can_access_case

persons_bp = Blueprint("persons", __name__, url_prefix="/persons")


@persons_bp.route("", strict_slashes=False)
@persons_bp.route("/", strict_slashes=False)
@login_required
def list_persons():
    search = request.args.get("q", "").strip()
    gender_filter = request.args.get("gender", "")
    page = request.args.get("page", 1, type=int)

    query = Person.query

    if search:
        s = f"%{search}%"
        query = query.filter(
            or_(
                Person.first_name.ilike(s),
                Person.last_name.ilike(s),
                Person.phone_contact.ilike(s),
                Person.address_line.ilike(s)
            )
        )

    if gender_filter:
        query = query.filter(Person.gender == gender_filter)

    pagination = query.order_by(Person.last_name, Person.first_name).paginate(page=page, per_page=12, error_out=False)

    return render_template(
        "persons/list.html",
        persons=pagination.items,
        pagination=pagination,
        search_query=search,
        selected_gender=gender_filter
    )


@persons_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_person():
    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        dob_str = request.form.get("date_of_birth")
        gender = request.form.get("gender", "Unknown")
        phone = request.form.get("phone_contact", "").strip()
        address = request.form.get("address_line", "").strip()

        if not first_name or not last_name:
            flash("First and last name are required.", "danger")
            return render_template("persons/create.html")

        dob = None
        if dob_str:
            try:
                dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid date of birth format. Use YYYY-MM-DD.", "warning")
                return render_template("persons/create.html")

        new_person = Person(
            first_name=first_name,
            last_name=last_name,
            date_of_birth=dob,
            gender=gender,
            phone_contact=phone if phone else None,
            address_line=address if address else None,
            is_fictional=True,
            created_at=datetime.utcnow()
        )

        try:
            db.session.add(new_person)
            db.session.commit()
            flash(f"Fictional persona '{new_person.full_name}' registered successfully.", "success")
            return redirect(url_for("persons.person_detail", person_id=new_person.person_id))
        except Exception as e:
            db.session.rollback()
            flash(f"Failed to create persona: {str(e)}", "danger")

    return render_template("persons/create.html")


@persons_bp.route("/<int:person_id>")
@login_required
def person_detail(person_id):
    person = Person.query.get_or_404(person_id)
    all_participations = CasePerson.query.filter_by(person_id=person_id).all()
    # Filter case participations to avoid leaking classified case involvement
    visible_participations = [
        cp for cp in all_participations 
        if can_access_case(current_user, cp.case, action="view")[0]
    ]
    return render_template("persons/detail.html", person=person, participations=visible_participations)


@persons_bp.route("/<int:person_id>/edit", methods=["GET", "POST"])
@login_required
def edit_person(person_id):
    person = Person.query.get_or_404(person_id)

    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        gender = request.form.get("gender")
        phone = request.form.get("phone_contact", "").strip()
        address = request.form.get("address_line", "").strip()

        if not first_name or not last_name:
            flash("First and last names cannot be empty.", "danger")
            return render_template("persons/edit.html", person=person)

        person.first_name = first_name
        person.last_name = last_name
        person.gender = gender
        person.phone_contact = phone if phone else None
        person.address_line = address if address else None

        try:
            db.session.commit()
            flash("Persona profile updated.", "success")
            return redirect(url_for("persons.person_detail", person_id=person.person_id))
        except Exception as e:
            db.session.rollback()
            flash(f"Failed to update persona: {str(e)}", "danger")

    return render_template("persons/edit.html", person=person)
