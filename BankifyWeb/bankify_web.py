# MrJ         |
# Bankify.Web |
# 7/12/2024   |
# ------------

from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, Account, Transaction
import os


def create_app(config_class=None, db_uri=None):
    app = Flask(__name__)

    if config_class:
        app.config.from_object(config_class)
    else:
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a_5up3r_dup3r_s3cr3t_k3y')
        db_dir = os.path.abspath(os.path.dirname(__file__))
        db_path = os.path.join(db_dir, 'instance', 'bankify.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = db_uri or 'sqlite:///' + db_path

    db.init_app(app)

    with app.app_context():
        db.create_all()
        app.logger.info(f"Database initialized at: {app.config['SQLALCHEMY_DATABASE_URI']}")

    @app.route('/')
    def home():
        app.logger.info("Rendering home page")
        return render_template('index.html')

    @app.route('/create_account', methods=['GET', 'POST'])
    def create_account():
        if request.method == 'POST':
            account_id = request.form.get('account_id')
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')

            if not account_id or not name or not email or not password:
                flash('All fields are required!', 'danger')
                return redirect(url_for('create_account'))

            existing_account = Account.query.filter_by(account_id=account_id).first()
            if existing_account:
                flash('Account ID already exists!', 'danger')
                return redirect(url_for('create_account'))

            new_account = Account(account_id=account_id, name=name, email=email, balance=0.0)
            new_account.set_password(password)
            db.session.add(new_account)
            db.session.commit()

            flash('Account created successfully!', 'success')
            return redirect(url_for('login'))

        return render_template('create_account.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            account_id = request.form.get('account_id')
            password = request.form.get('password')

            account = Account.query.filter_by(account_id=account_id).first()
            if account and account.check_password(password):
                session['account_id'] = account_id
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                app.logger.warning(f"Login failed for account_id: {account_id}")
                flash('Invalid credentials!', 'danger')

        return render_template('login.html')

    @app.route('/dashboard')
    def dashboard():
        if 'account_id' not in session:
            flash('Please login first!', 'warning')
            return redirect(url_for('login'))

        account = Account.query.filter_by(account_id=session['account_id']).first()
        return render_template('dashboard.html', account=account)

    @app.route('/deposit', methods=['GET', 'POST'])
    def deposit():
        if 'account_id' not in session:
            flash('Please login first!', 'warning')
            return redirect(url_for('login'))

        if request.method == 'POST':
            amount = round(float(request.form.get('amount')), 2)
            account = Account.query.filter_by(account_id=session['account_id']).first()

            if amount <= 0:
                flash('Invalid amount!', 'danger')
                return redirect(url_for('deposit'))

            account.balance = round(account.balance + amount, 2)
            transaction = Transaction(account_id=account.id, type='Deposit', amount=amount)
            db.session.add(transaction)
            db.session.commit()

            flash('Deposit successful!', 'success')
            return redirect(url_for('dashboard'))

        return render_template('deposit.html')

    @app.route('/withdraw', methods=['GET', 'POST'])
    def withdraw():
        if 'account_id' not in session:
            flash('Please login first!', 'warning')
            return redirect(url_for('login'))

        if request.method == 'POST':
            amount = round(float(request.form.get('amount')), 2)
            account = Account.query.filter_by(account_id=session['account_id']).first()

            if amount <= 0 or amount > account.balance:
                flash('Invalid amount!', 'danger')
                return redirect(url_for('withdraw'))

            account.balance = round(account.balance - amount, 2)
            transaction = Transaction(account_id=account.id, type='Withdrawal', amount=amount)
            db.session.add(transaction)
            db.session.commit()

            flash('Withdrawal successful!', 'success')
            return redirect(url_for('dashboard'))

        return render_template('withdraw.html')

    @app.route('/transactions')
    def transactions():
        if 'account_id' not in session:
            flash('Please login first!', 'warning')
            return redirect(url_for('login'))

        account = Account.query.filter_by(account_id=session['account_id']).first()
        transactions = Transaction.query.filter_by(account_id=account.id).all()
        return render_template('transactions.html', transactions=transactions)

    @app.route('/logout')
    def logout():
        session.pop('account_id', None)
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))

    @app.template_filter('currency')
    def currency_filter(value):
        return f"{value:,.2f}"

    @app.route('/update_account', methods=['GET', 'POST'])
    def update_account():
        if 'account_id' not in session:
            flash('Please login first!', 'warning')
            return redirect(url_for('login'))

        account = Account.query.filter_by(account_id=session['account_id']).first()

        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')

            if not name or not email or not password:
                flash('All fields are required!', 'danger')
                return redirect(url_for('update_account'))

            account.name = name
            account.email = email
            account.set_password(password)
            db.session.commit()

            flash('Account updated successfully!', 'success')
            return redirect(url_for('dashboard'))

        return render_template('update_account.html', account=account)

    @app.route('/delete_account', methods=['GET', 'POST', 'DELETE'])
    def delete_account():
        if 'account_id' not in session:
            flash('Please login first!', 'warning')
            return redirect(url_for('login'))

        if request.method == 'GET':
            return render_template('delete_account.html')

        if request.method == 'POST' or request.method == 'DELETE':
            account = Account.query.filter_by(account_id=session['account_id']).first()
            if account:
                db.session.delete(account)
                db.session.commit()
                session.pop('account_id', None)
                flash('Account deleted successfully!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Account not found!', 'danger')
                return redirect(url_for('dashboard'))
        else:
            flash('Method not allowed!', 'danger')
            return redirect(url_for('dashboard'))

    app.jinja_env.filters['currency'] = currency_filter

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
