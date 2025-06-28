from flask import Flask, session, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_bcrypt import Bcrypt
from models import db, User, Recipe

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a secure key
app.json.compact = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)
bcrypt = Bcrypt(app)

# Signup Resource: POST /signup
class Signup(Resource):
    def post(self):
        data = request.get_json()
        if not data.get('username') or not data.get('password'):
            return make_response({'errors': ['Username and password are required']}, 422)
        try:
            user = User(
                username=data['username'],
                image_url=data.get('image_url'),
                bio=data.get('bio')
            )
            user.password_hash = data['password']
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return make_response({
                'id': user.id,
                'username': user.username,
                'image_url': user.image_url,
                'bio': user.bio
            }, 201)
        except ValueError as e:
            return make_response({'errors': [str(e)]}, 422)

# CheckSession Resource: GET /check_session
class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = db.session.get(User, user_id)
            return make_response({
                'id': user.id,
                'username': user.username,
                'image_url': user.image_url,
                'bio': user.bio
            }, 200)
        return make_response({'error': 'Unauthorized'}, 401)

# Login Resource: POST /login
class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        if user and user.authenticate(data['password']):
            session['user_id'] = user.id
            return make_response({
                'id': user.id,
                'username': user.username,
                'image_url': user.image_url,
                'bio': user.bio
            }, 200)
        return make_response({'error': 'Invalid username or password'}, 401)

# Logout Resource: DELETE /logout
class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session.pop('user_id')
            return make_response({}, 204)
        return make_response({'error': 'Unauthorized'}, 401)

# RecipeIndex Resource: GET /recipes, POST /recipes
class RecipeIndex(Resource):
    def get(self):
        if session.get('user_id'):
            recipes = [
                {
                    'id': recipe.id,
                    'title': recipe.title,
                    'instructions': recipe.instructions,
                    'minutes_to_complete': recipe.minutes_to_complete,
                    'user': {
                        'id': recipe.user.id,
                        'username': recipe.user.username,
                        'image_url': recipe.user.image_url,
                        'bio': recipe.user.bio
                    }
                } for recipe in Recipe.query.all()
            ]
            return make_response(recipes, 200)
        return make_response({'error': 'Unauthorized'}, 401)

    def post(self):
        if session.get('user_id'):
            data = request.get_json()
            try:
                recipe = Recipe(
                    title=data['title'],
                    instructions=data['instructions'],
                    minutes_to_complete=data.get('minutes_to_complete'),
                    user_id=session['user_id']
                )
                db.session.add(recipe)
                db.session.commit()
                return make_response({
                    'id': recipe.id,
                    'title': recipe.title,
                    'instructions': recipe.instructions,
                    'minutes_to_complete': recipe.minutes_to_complete,
                    'user': {
                        'id': recipe.user.id,
                        'username': recipe.user.username,
                        'image_url': recipe.user.image_url,
                        'bio': recipe.user.bio
                    }
                }, 201)
            except ValueError as e:
                return make_response({'errors': [str(e)]}, 422)
        return make_response({'error': 'Unauthorized'}, 401)

# Register resources with the API
api.add_resource(Signup, '/signup')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(RecipeIndex, '/recipes')

if __name__ == '__main__':
    app.run(port=5555, debug=True)