from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

from .models import db, User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Crée un nouveau compte utilisateur.
    Body JSON attendu : { "email": "...", "password": "..." }
    """
    data = request.get_json()

    # Valider que les champs requis sont présents
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email et password requis"}), 400

    email = data["email"].lower().strip()
    password = data["password"]

    # Vérifier la longueur minimale du mot de passe
    if len(password) < 8:
        return jsonify({"error": "Le password doit faire au moins 8 caractères"}), 400

    # Vérifier qu'un compte avec cet email n'existe pas déjà
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Un compte existe déjà avec cet email"}), 409

    # Hasher le mot de passe — jamais stocker en clair
    password_hash = generate_password_hash(password)

    # Créer l'utilisateur en base
    user = User(email=email, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()

    # Générer un token JWT directement — l'utilisateur est connecté après register
    # identity = l'identifiant unique de l'utilisateur, converti en string
    token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Compte créé avec succès",
        "token": token,
        "user": user.to_dict()
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Connecte un utilisateur existant.
    Body JSON attendu : { "email": "...", "password": "..." }
    """
    data = request.get_json()

    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email et password requis"}), 400

    email = data["email"].lower().strip()
    password = data["password"]

    # Chercher l'utilisateur par email
    user = User.query.filter_by(email=email).first()

    # Message d'erreur volontairement vague : on ne dit pas si c'est
    # l'email ou le password qui est faux (sécurité)
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Email ou password incorrect"}), 401

    # Générer le token JWT
    token = create_access_token(identity=str(user.id))

    return jsonify({
        "token": token,
        "user": user.to_dict()
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """
    Retourne les infos de l'utilisateur connecté.
    Nécessite un token JWT valide dans le header Authorization.
    """
    # get_jwt_identity() lit l'identity qu'on a mise dans le token
    # On la reconvertit en int pour chercher l'utilisateur en DB
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    return jsonify({"user": user.to_dict()}), 200