from flask import Flask
from models import db, User, Recipe

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    print("Deleting all records...")
    Recipe.query.delete()
    User.query.delete()
    db.session.commit()

    print("Creating users...")
    users = [
        User(username="user1", image_url="http://example.com/user1.jpg", bio="Bio for user1"),
        User(username="user2", image_url="http://example.com/user2.jpg", bio="Bio for user2")
    ]
    for user in users:
        user.password_hash = "password"  # Set a password
    db.session.add_all(users)
    db.session.commit()

    print("Creating recipes...")
    recipes = [
        Recipe(
            title="Recipe 1",
            instructions="Instructions for recipe 1" * 10,
            minutes_to_complete=30,
            user_id=users[0].id
        ),
        Recipe(
            title="Recipe 2",
            instructions="Instructions for recipe 2" * 10,
            minutes_to_complete=45,
            user_id=users[1].id
        )
    ]
    db.session.add_all(recipes)
    db.session.commit()

    print("Complete.")