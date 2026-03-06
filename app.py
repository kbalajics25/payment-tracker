from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from functools import wraps
from datetime import datetime, timedelta
import os
import shutil

from config import Config
from utils.db_helper import (
    init_db, get_user_balance, add_transaction, edit_transaction, 
    delete_transaction, get_transactions, get_transaction_count,
    get_summary_stats, get_category_totals, get_daily_totals,
    get_weekly_totals, get_monthly_totals, get_transaction_by_id,
    get_all_categories
)
from utils.auth_helper import register_user, authenticate_user, get_user_by_id
from utils.export_helper import export_to_excel, export_to_pdf, export_to_csv

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database on startup
init_db()

# Create necessary directories
os.makedirs('backups', exist_ok=True)
os.makedirs('exports', exist_ok=True)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Redirect to login or dashboard"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate
        if not username or not password:
            flash('Username and password are required', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        # Register user
        success, message = register_user(username, password)
        
        if success:
            # Auto-login after registration
            _, user_id, _ = authenticate_user(username, password)
            session['user_id'] = user_id
            session['username'] = username
            flash('Registration successful! Welcome!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(message, 'danger')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Username and password are required', 'danger')
            return render_template('login.html')
        
        success, user_id, message = authenticate_user(username, password)
        
        if success:
            session['user_id'] = user_id
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(message, 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    user_id = session['user_id']
    
    # Get summary statistics
    stats = get_summary_stats(user_id)
    
    # Get recent transactions
    recent_transactions = get_transactions(user_id, page=1, per_page=10)
    
    # Get categories for dropdown
    default_categories = ['Food', 'Travel', 'Shopping', 'Bills', 'Salary', 
                         'Entertainment', 'Healthcare', 'Education', 'Other']
    user_categories = get_all_categories(user_id)
    all_categories = sorted(set(default_categories + user_categories))
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         transactions=recent_transactions,
                         categories=all_categories,
                         currency=Config.CURRENCY_SYMBOL)

@app.route('/add_transaction', methods=['POST'])
@login_required
def add_transaction_route():
    """Add new transaction"""
    user_id = session['user_id']
    
    try:
        trans_type = request.form.get('type')
        amount = float(request.form.get('amount'))
        category = request.form.get('category')
        reason = request.form.get('reason', '').strip()
        
        if not trans_type or not category or amount <= 0:
            flash('Invalid transaction data', 'danger')
            return redirect(url_for('dashboard'))
        
        success, message = add_transaction(user_id, trans_type, amount, category, reason)
        
        if success:
            flash('Transaction added successfully!', 'success')
        else:
            flash(message, 'danger')
    except ValueError:
        flash('Invalid amount entered', 'danger')
    except Exception as e:
        flash(f'Error adding transaction: {str(e)}', 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/edit_transaction/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_transaction_route(id):
    """Edit transaction"""
    user_id = session['user_id']
    
    if request.method == 'POST':
        try:
            updated_data = {
                'type': request.form.get('type'),
                'amount': float(request.form.get('amount')),
                'category': request.form.get('category'),
                'reason': request.form.get('reason', '').strip()
            }
            
            success, message = edit_transaction(id, user_id, updated_data)
            
            if success:
                flash('Transaction updated successfully!', 'success')
                return redirect(url_for('transactions_page'))
            else:
                flash(message, 'danger')
        except ValueError:
            flash('Invalid amount entered', 'danger')
        except Exception as e:
            flash(f'Error updating transaction: {str(e)}', 'danger')
    
    # GET request - show edit form
    transaction = get_transaction_by_id(id, user_id)
    
    if not transaction:
        flash('Transaction not found', 'danger')
        return redirect(url_for('transactions_page'))
    
    default_categories = ['Food', 'Travel', 'Shopping', 'Bills', 'Salary', 
                         'Entertainment', 'Healthcare', 'Education', 'Other']
    
    return render_template('edit_transaction.html', 
                         transaction=transaction, 
                         categories=default_categories)

@app.route('/delete_transaction/<int:id>', methods=['POST'])
@login_required
def delete_transaction_route(id):
    """Delete transaction"""
    user_id = session['user_id']
    
    success, message = delete_transaction(id, user_id)
    
    if success:
        flash('Transaction deleted successfully!', 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('transactions_page'))

@app.route('/transactions')
@login_required
def transactions_page():
    """View all transactions with filters"""
    user_id = session['user_id']
    
    # Get filter parameters
    filters = {}
    
    trans_type = request.args.get('type', 'both')
    if trans_type != 'both':
        filters['type'] = trans_type
    
    category = request.args.get('category')
    if category:
        filters['category'] = category
    
    date_from = request.args.get('date_from')
    if date_from:
        filters['date_from'] = date_from
    
    date_to = request.args.get('date_to')
    if date_to:
        filters['date_to'] = date_to
    
    min_amount = request.args.get('min_amount')
    if min_amount:
        try:
            filters['min_amount'] = float(min_amount)
        except ValueError:
            pass
    
    max_amount = request.args.get('max_amount')
    if max_amount:
        try:
            filters['max_amount'] = float(max_amount)
        except ValueError:
            pass
    
    search = request.args.get('search')
    if search:
        filters['search'] = search
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = Config.TRANSACTIONS_PER_PAGE
    
    # Get transactions
    transactions = get_transactions(user_id, filters, page, per_page)
    total_count = get_transaction_count(user_id, filters)
    total_pages = (total_count + per_page - 1) // per_page
    
    # Get categories for filter dropdown
    default_categories = ['Food', 'Travel', 'Shopping', 'Bills', 'Salary', 
                         'Entertainment', 'Healthcare', 'Education', 'Other']
    user_categories = get_all_categories(user_id)
    all_categories = sorted(set(default_categories + user_categories))
    
    return render_template('transactions.html', 
                         transactions=transactions,
                         categories=all_categories,
                         page=page,
                         total_pages=total_pages,
                         total_count=total_count,
                         filters=request.args,
                         currency=Config.CURRENCY_SYMBOL)

@app.route('/reports')
@login_required
def reports():
    """Generate reports"""
    user_id = session['user_id']
    
    # Get summary stats
    stats = get_summary_stats(user_id)
    
    return render_template('reports.html', 
                         stats=stats,
                         currency=Config.CURRENCY_SYMBOL)

@app.route('/export/<format>')
@login_required
def export_data(format):
    """Export data in specified format"""
    user_id = session['user_id']
    
    try:
        # Get export range
        export_range = request.args.get('range', 'all')
        filters = {}
        
        if export_range == 'current_month':
            first_day = datetime.now().replace(day=1).date()
            filters['date_from'] = first_day.isoformat()
        elif export_range == 'last_3_months':
            three_months_ago = (datetime.now() - timedelta(days=90)).date()
            filters['date_from'] = three_months_ago.isoformat()
        elif export_range == 'custom':
            date_from = request.args.get('date_from')
            date_to = request.args.get('date_to')
            if date_from:
                filters['date_from'] = date_from
            if date_to:
                filters['date_to'] = date_to
        
        # Get all transactions (no pagination for export)
        transactions = get_transactions(user_id, filters, page=1, per_page=100000)
        
        # Get summary stats
        stats = get_summary_stats(user_id)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'excel':
            filename = f'transactions_{timestamp}.xlsx'
            filepath = export_to_excel(transactions, filename, stats)
            return send_file(filepath, as_attachment=True, download_name=filename)
        
        elif format == 'pdf':
            filename = f'transactions_{timestamp}.pdf'
            filepath = export_to_pdf(transactions, filename, stats)
            return send_file(filepath, as_attachment=True, download_name=filename)
        
        elif format == 'csv':
            filename = f'transactions_{timestamp}.csv'
            filepath = export_to_csv(transactions, filename)
            return send_file(filepath, as_attachment=True, download_name=filename)
        
        else:
            flash('Invalid export format', 'danger')
            return redirect(url_for('reports'))
    
    except Exception as e:
        flash(f'Export failed: {str(e)}', 'danger')
        return redirect(url_for('reports'))

@app.route('/api/chart_data/<chart_type>')
@login_required
def get_chart_data(chart_type):
    """API endpoint for chart data"""
    user_id = session['user_id']
    
    try:
        if chart_type == 'credit_vs_debit':
            stats = get_summary_stats(user_id)
            return jsonify({
                'labels': ['Credit', 'Debit'],
                'data': [stats['total_credit'], stats['total_debit']],
                'backgroundColor': ['#10b981', '#ef4444']
            })
        
        elif chart_type == 'category_spending':
            category_totals = get_category_totals(user_id)
            return jsonify({
                'labels': list(category_totals.keys()),
                'data': list(category_totals.values()),
                'backgroundColor': '#3b82f6'
            })
        
        elif chart_type == 'daily_spending':
            daily_data = get_daily_totals(user_id, days=30)
            labels = [datetime.fromisoformat(d['date']).strftime('%b %d') for d in daily_data]
            debits = [d['debit'] for d in daily_data]
            
            return jsonify({
                'labels': labels,
                'data': debits,
                'borderColor': '#8b5cf6'
            })
        
        elif chart_type == 'weekly_spending':
            weekly_data = get_weekly_totals(user_id, weeks=12)
            labels = [f"Week {w['week'][-2:]}" for w in weekly_data]
            debits = [w['debit'] for w in weekly_data]
            
            return jsonify({
                'labels': labels,
                'data': debits,
                'borderColor': '#f59e0b'
            })
        
        elif chart_type == 'monthly_spending':
            monthly_data = get_monthly_totals(user_id, months=12)
            labels = [datetime.strptime(m['month'], '%Y-%m').strftime('%b %Y') for m in monthly_data]
            debits = [m['debit'] for m in monthly_data]
            credits = [m['credit'] for m in monthly_data]
            
            return jsonify({
                'labels': labels,
                'debit_data': debits,
                'credit_data': credits
            })
        
        elif chart_type == 'balance_trend':
            # Get all transactions to show balance trend
            transactions = get_transactions(user_id, page=1, per_page=1000)
            transactions.reverse()  # Oldest first
            
            labels = []
            balances = []
            
            for i, trans in enumerate(transactions):
                if i % max(1, len(transactions) // 50) == 0:  # Sample data points
                    date = datetime.fromisoformat(trans['transaction_date'])
                    labels.append(date.strftime('%b %d'))
                    balances.append(trans['balance_after'])
            
            return jsonify({
                'labels': labels,
                'data': balances,
                'borderColor': '#06b6d4'
            })
        
        else:
            return jsonify({'error': 'Invalid chart type'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/settings')
@login_required
def settings():
    """User settings"""
    user = get_user_by_id(session['user_id'])
    return render_template('settings.html', user=user)

@app.route('/backup', methods=['POST'])
@login_required
def create_backup():
    """Create manual backup"""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        backup_filename = f'backup_{timestamp}.db'
        backup_path = os.path.join('backups', backup_filename)
        
        shutil.copy('database.db', backup_path)
        
        flash(f'Backup created: {backup_filename}', 'success')
    except Exception as e:
        flash(f'Backup failed: {str(e)}', 'danger')
    
    return redirect(url_for('settings'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)