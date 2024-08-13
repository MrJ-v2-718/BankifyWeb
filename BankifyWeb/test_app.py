# MrJ         |
# Bankify.Web |
# 7/12/2024   |
# ------------

import unittest
import hashlib
from bankify_web import create_app, db, Account
import os


def hash_password(password):
    # Simulate SHA-256 hashing of passwords
    return hashlib.sha256(password.encode()).hexdigest()


class BankifyTestCase(unittest.TestCase):
    def setUp(self):
        # Use a separate test database for testing
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a_5up3r_dup3r_s3cr3t_k3y')
        db_dir = os.path.abspath(os.path.dirname(__file__))
        db_path = os.path.join(db_dir, 'instance', 'bankify.db')  # Adjust as needed
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path

        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            # Add debug output to verify database URI
            self.app.logger.info(f"Using database URI: {self.app.config['SQLALCHEMY_DATABASE_URI']}")

    def tearDown(self):
        # Clean up after each test method runs
        with self.app.app_context():
            test_account = Account.query.filter_by(account_id='12345').first()
            if test_account:
                db.session.delete(test_account)
                db.session.commit()

    def create_test_account(self):
        # Example method to create a test account
        hashed_password = hash_password('password')  # Hash 'password' for testing
        with self.app.app_context():
            test_account = Account(
                account_id='12345',
                name='Test User',
                email='test@example.com',
                password=hashed_password
            )
            db.session.add(test_account)
            db.session.commit()
            # Simulate login by setting session['account_id']
            with self.client as c:
                with c.session_transaction() as sess:
                    sess['account_id'] = '12345'

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to Bankify', response.data)

    def test_login(self):
        self.create_test_account()
        response = self.client.post('/login', data=dict(
            account_id='12345',
            password='password'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login successful!', response.data)

    def test_deposit(self):
        self.create_test_account()
        response = self.client.post('/deposit', data=dict(
            amount='100.00'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Deposit successful!', response.data)

    def test_withdraw(self):
        self.create_test_account()

        # Simulate deposit to ensure sufficient balance for withdrawal
        response = self.client.post('/deposit', data=dict(
            amount='100.00'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Attempt withdrawal
        response = self.client.post('/withdraw', data=dict(
            amount='50.00'
        ), follow_redirects=True)

        # Check if withdrawal success message is present
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Withdrawal successful!', response.data)

    def test_logout(self):
        self.create_test_account()
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have been logged out.', response.data)


if __name__ == '__main__':
    unittest.main()
