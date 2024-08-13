# MrJ         |
# Bankify.Web |
# 7/12/2024   |
# ------------

from flask import Flask
from models import db, Account
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_5up3r_dup3r_s3cr3t_k3y'
# Specify the path to the database file inside the 'instance' folder
db_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = (
        'sqlite:///' + os.path.join(db_dir, 'instance', 'bankify.db')
)

# Initialize SQLAlchemy with the Flask app
db.init_app(app)

if __name__ == "__main__":
    with app.app_context():
        # Query all accounts
        accounts = Account.query.all()
        for account in accounts:
            print(
                f"Account ID: {account.account_id}"
                f"\nName: {account.name}"
                f"\nEmail: {account.email}"
                f"\nPassword: {account.password}"
                f"\nBalance: {account.balance}\n"
            )
