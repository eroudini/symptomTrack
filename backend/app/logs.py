from datetime import date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from .models import db, SymptomLog

logs_bp = Blueprint("logs", __name__)

@logs_bp.route("/", methods=["GET"])
def get_logs():
    return jsonify({
        "message": "Liste des symptômes",
        "logs": []
    })

def get_current_user_id():
    return int(get_jwt_identity())

def validate_log_data(data):
    errors = []

    for field in ["pain_level", "fatigue_level", "mood_level"]:
        if field not in data:
            errors.append(f"{field} est requis")
        elif not isinstance(data[field], int) or not (0 <= data[field] <= 10):
            errors.append(f"{field} doit être un entier entre 0 et 10")

    if errors:
        return None, errors
    
    return {
        "pain_level": data["pain_level"],
        "fatigue_level": data["fatigue_level"],
        "mood_level": data["mood_level"],
        "medications": data.get("medications"),
        "notes": data.get("notes"),
    }, None

# post /logs 

@logs_bp.route("", methods=["POST"])
@jwt_required()
def create_log():
    user_id = get_current_user_id()
    data = request.get_json()

    if not data:
        return jsonify({"error": "Body JSON requis"}), 400
    
    cleaned, errors = validate_log_data(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    log_date = date.today()
    if "data" in data:
        try:
            log_date = date.fromisoformat(date["date"])
        except ValueError:
            return jsonify({"error": "Format de date invalide. Utilise YYY-MM-DD"}), 400
        
    existing = SymptomLog.query.filter_by(user_id=user_id, date=log_date).first()
    if existing:
        return jsonify({
            "error": "Un log existe déjà pour cette date",
            "existing_id": existing.id
        }), 409
    
    log = SymptomLog(user_id=user_id, date=log_date, **cleaned)
    db.session.add(log)
    db.session.commit()

    return jsonify({"message": "Log crée", "log": log.to_dict()}), 201

# get /logs

@logs_bp.route("", methods=["GET"])
@jwt_required()
def get_logs():
    user_id = get_current_user_id()
    days = request.args.get("days", type=int)

    query = SymptomLog.query.filter_by(user_id=user_id)

    if days:
        from datetime import timedelta
        cutoff = date.today() - timedelta(days=days)
        query = query.filter(SymptomLog.date >= cutoff)

    logs = query.order_by(SymptomLog.date.desc()).all()

    return jsonify({
        "logs": [log.to_dict() for log in logs],
        "count": len(logs)
    }), 200

# get /logs/:id detail d'un log

@logs_bp.route("/", methods=["GET"])
@jwt_required()
def get_log(log_id):
    user_id = get_current_user_id()
    log = SymptomLog.query.filter_by(
        id=log_id, user_id=user_id
    ).first_or_404()
    return jsonify({"log": log.to_dict()}), 200

# put /logs/:id modifier un log

@logs_bp.route("/", methods=["PUT"])
@jwt_required()
def update_log(log_id):
    user_id = get_current_user_id()
    log = SymptomLog.query.filter_by(
        id=log_id, user_id=user_id
    ).first_or_404()

    data = request.get_json()
    if not data:
        return jsonify({"error": "Body JSON requis"}), 400
    
    cleaned, errors = validate_log_data(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    log.pain_level = cleaned["pain_level"]
    log.fatigue_level = cleaned["fatigue_level"]
    log.mood_level = cleaned["mood_level"]
    log.medications = cleaned["medications"]
    log.notes = cleaned["notes"]

    db.session.commit()
    return jsonify({"message": "Log mis à jour", "log": log.to_dict()}), 200

# delete /logs/:id 

@logs_bp.route("/", methods=["DELETE"])
@jwt_required
def delete_log(log_id):
    user_id = get_current_user_id()
    log = SymptomLog.query.filter_by(
        id=log_id, user_id=user_id
    ).first_or_404()

    db.session.delete(log)
    db.session.commit()
    return jsonify({"message": "Log supprimé"}), 200


