import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Marvel, Dc, Other, Favoritos
from sqlalchemy import select
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

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret-key")
jwt = JWTManager(app)

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def get_users():
    users = db.session.execute(select(User)).scalars().all()
    result = [u.serialize() for u in users]

    if not result:
        return jsonify({"msg": "No users found"}), 404

    return jsonify({"msg": "ok", "result": result}), 200

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    return jsonify({"msg": "ok", "result": user.serialize()}), 200

@app.route('/marvel', methods=['GET'])
def get_marvels():
    marvels = db.session.execute(select(Marvel)).scalars().all()
    result = [m.serialize() for m in marvels]

    if not result:
        return jsonify({"msg": "No marvel items found"}), 404

    return jsonify({"msg": "ok", "result": result}), 200

@app.route('/marvel/<int:marvel_id>', methods=['GET'])
def get_marvel(marvel_id):
    marvel = db.session.get(Marvel, marvel_id)

    if not marvel:
        return jsonify({"msg": "Marvel item not found"}), 404

    return jsonify({"msg": "ok", "result": marvel.serialize()}), 200

@app.route('/dc', methods=['GET'])
def get_dcs():
    dcs = db.session.execute(select(Dc)).scalars().all()
    result = [d.serialize() for d in dcs]

    if not result:
        return jsonify({"msg": "No DC items found"}), 404

    return jsonify({"msg": "ok", "result": result}), 200

@app.route('/dc/<int:dc_id>', methods=['GET'])
def get_dc(dc_id):
    dc_item = db.session.get(Dc, dc_id)

    if not dc_item:
        return jsonify({"msg": "DC item not found"}), 404

    return jsonify({"msg": "ok", "result": dc_item.serialize()}), 200

@app.route('/other', methods=['GET'])
def get_others():
    others = db.session.execute(select(Other)).scalars().all()
    result = [o.serialize() for o in others]

    if not result:
        return jsonify({"msg": "No other items found"}), 404

    return jsonify({"msg": "ok", "result": result}), 200

@app.route('/other/<int:other_id>', methods=['GET'])
def get_other(other_id):
    other_item = db.session.get(Other, other_id)

    if not other_item:
        return jsonify({"msg": "Other item not found"}), 404

    return jsonify({"msg": "ok", "result": other_item.serialize()}), 200

@app.route('/users/<int:user_id>/favoritos', methods=['GET'])
def get_user_favoritos(user_id):
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    favoritos = [f.serialize() for f in user.favoritos]

    return jsonify({"msg": "ok", "result": favoritos}), 200

@app.route('/favorite/<int:favorito_id>', methods=['DELETE'])
def delete_favorite(favorito_id):
    favorito = db.session.get(Favoritos, favorito_id)

    if not favorito:
        return jsonify({"msg": "Favorito not found"}), 404

    db.session.delete(favorito)
    db.session.commit()

    return jsonify({"msg": "Favorito eliminado"}), 200

@app.route('/signup', methods=['POST'])
def signup():
    body = request.get_json()
    nombre = body.get("nombre")
    apellido = body.get("apellido")
    email = body.get("email")
    password = body.get("password")

    if not nombre or not apellido or not email or not password:
        return jsonify({"msg": "Se requieren nombre, apellido, email y contraseña"}), 400
    
    existing_user = db.session.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()

    if existing_user:
        return jsonify({"msg": "El correo ya está registrado"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    new_user = User(
        nombre=nombre,
        apellido=apellido,
        email=email,
        password=hashed_password
    )   

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "Usuario creado con éxito"}), 201

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
        return jsonify({"msg": "Email o contraseña incorrectos"}), 401

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "msg": "Login exitoso",
        "access_token": access_token,
        "user": user.serialize()
    }), 200

@app.route("/private", methods=["GET"])
@jwt_required()
def private():
    current_user = get_jwt_identity()
    return jsonify(msg="Acceso autorizado", user=current_user), 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=True)