from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from models import db, Hero, Power, HeroPower
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.exceptions import NotFound, BadRequest
import os

# Set up database URI
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

# Home route
@app.route('/')
def index():
    return '<h1>Superheroes Code Challenge</h1>'

# Get all heroes
@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    return jsonify([hero.to_dict() for hero in heroes])

# Get hero by ID
@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero_by_id(id):
    hero = Hero.query.get(id)
    if not hero:
        return jsonify({"error": "Hero not found"}), 404
    return jsonify(hero.to_dict()), 200

# Get all powers
@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    return jsonify([power.to_dict() for power in powers])

# Get power by ID
@app.route('/powers/<int:id>', methods=['GET'])
def get_power_by_id(id):
    power = Power.query.get(id)
    if not power:
        raise NotFound(description=f"Power with ID {id} not found")
    return jsonify(power.to_dict())

# Update power description
@app.route('/powers/<int:id>', methods=['PATCH'])
def patch_power(id):
    power = Power.query.get(id)
    if not power:
        raise NotFound(description=f"Power with ID {id} not found")

    data = request.get_json()
    if 'description' in data:
        description = data['description']
        if len(description) < 20:
            return jsonify({'errors': ["validation errors"]}), 400
        power.description = description

    db.session.commit()
    return jsonify(power.to_dict())

# Update hero attributes
@app.route('/heroes/<int:id>', methods=['PATCH'])
def patch_hero(id):
    hero = Hero.query.get(id)
    if not hero:
        raise NotFound(description=f"Hero with ID {id} not found")

    data = request.get_json()
    if 'name' in data:
        hero.name = data['name']
    if 'super_name' in data:
        hero.super_name = data['super_name']

    db.session.commit()
    return jsonify(hero.to_dict())

# Create hero-power relationship
@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()

    # Validate strength
    strength = data.get('strength')
    if strength not in ['Strong', 'Weak', 'Average']:
        return jsonify({'errors': ["validation errors"]}), 400

    # Get hero and power
    hero = Hero.query.get(data.get('hero_id'))
    power = Power.query.get(data.get('power_id'))

    if not hero or not power:
        return make_response(jsonify({'error': 'Hero or Power not found'}), 404)

    # Create new hero-power record
    hero_power = HeroPower(strength=strength, hero_id=hero.id, power_id=power.id)
    db.session.add(hero_power)
    db.session.commit()

    return jsonify(hero_power.to_dict())

# Error handlers
@app.errorhandler(NotFound)
def handle_not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(BadRequest)
def handle_bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

# Run the app
if __name__ == '__main__':
    app.run(port=5555, debug=True)
