from database.models.users import UserModel
from service.jwt_token import hash_password
import os
from dotenv import load_dotenv

load_dotenv()
admin_users = UserModel(username="Administrator", password=hash_password(os.getenv('ADMIN_PASSWORD')),
                        email="admin@example.com", birthday="2001-01-01")

user_users = UserModel(username="Useruser", password=hash_password("Useruser@1A"), email="user@example.com",
                       birthday="2001-01-01")

guest_users = UserModel(username="Guestguest", password=hash_password("Guestguest@1A"), email="guest@example.com",
                        birthday="2001-01-01")

users_list = [admin_users, user_users, guest_users]
