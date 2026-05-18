import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from admin import setup_admin
from models import db, User, Marvel, Dc, Other, Favoritos
from sqlalchemy import select, and_
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager

app = Flask(__name__)
app.url_map.strict_slashes = False
bcrypt = Bcrypt(app)


db_url = os.getenv("DATABASE_URL")
if db_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

Migrate(app, db)
db.init_app(app)
CORS(app, resources={r"/*": {"origins": "*"}})
setup_admin(app)

app.config["JWT_SECRET_KEY"] = "super-secret"
jwt = JWTManager(app)


@app.route('/signup', methods=['POST'])
def signup():
    body = request.get_json()

    username = body.get("username")
    email = body.get("email")
    birth_date = body.get("birthDate")
    password = body.get("password")

    if not username or not email or not birth_date or not password:
        return jsonify({"msg": "Se requieren username, email, birthDate y password"}), 400
    
    existing_user = db.session.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()

    if existing_user:
        return jsonify({"msg": "El correo ya está registrado"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    new_user = User(
        username=username,
        email=email,
        birth_date=birth_date,
        password=hashed_password
    )   

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "Agente creado con éxito"}), 201


@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email")
    password = request.json.get("password")

    if not email or not password:
        return jsonify({"msg": "Se requieren email y contraseña"}), 400

    user = db.session.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()

    if user is None or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"msg": "Credenciales incorrectas"}), 401

    # Guardamos el ID del usuario en el token para buscar sus favoritos después
    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "msg": "Login exitoso",
        "access_token": access_token,
        "user": user.serialize()
    }), 200

@app.route('/favoritos', methods=['GET'])
@jwt_required()
def get_user_favoritos():
    user_id = get_jwt_identity()
    

    favoritos = db.session.execute(
        select(Favoritos).where(Favoritos.user_id == user_id)
    ).scalars().all()


    hero_ids = [fav.hero_id for fav in favoritos]

    return jsonify({"msg": "ok", "favorites": hero_ids}), 200


@app.route('/favoritos', methods=['POST'])
@jwt_required()
def add_favorite():
    user_id = get_jwt_identity()
    hero_id = request.json.get("hero_id")

    if not hero_id:
        return jsonify({"msg": "Se requiere hero_id"}), 400


    existing_fav = db.session.execute(
        select(Favoritos).where(and_(Favoritos.user_id == user_id, Favoritos.hero_id == hero_id))
    ).scalar_one_or_none()

    if existing_fav:
        return jsonify({"msg": "El héroe ya está en tus favoritos"}), 400

    new_fav = Favoritos(user_id=user_id, hero_id=hero_id)
    db.session.add(new_fav)
    db.session.commit()

    return jsonify({"msg": "Añadido a favoritos"}), 201


@app.route('/favoritos/<int:hero_id>', methods=['DELETE'])
@jwt_required()
def delete_favorite(hero_id):
    user_id = get_jwt_identity()

    favorito = db.session.execute(
        select(Favoritos).where(and_(Favoritos.user_id == user_id, Favoritos.hero_id == hero_id))
    ).scalar_one_or_none()

    if not favorito:
        return jsonify({"msg": "Favorito no encontrado"}), 404

    db.session.delete(favorito)
    db.session.commit()

    return jsonify({"msg": "Héroe eliminado de favoritos"}), 200


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=True)