import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import os
import pytz

DATABASE_PATH = 'database.db'

def get_india_time():
    india = pytz.timezone('Asia/Kolkata')
    return datetime.now(india).strftime("%Y-%m-%d %H:%M:%S")

def get_db_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with schema"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('credit', 'debit')),
            amount REAL NOT NULL CHECK(amount > 0),
            category TEXT NOT NULL,
            reason TEXT,
            transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            balance_after REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Create indexes for performance
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_user_transactions 
        ON transactions(user_id, transaction_date DESC)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_transaction_type 
        ON transactions(user_id, type)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_transaction_category 
        ON transactions(user_id, category)
    ''')
    
    conn.commit()
    conn.close()

def get_user_balance(user_id: int) -> float:
    """Calculate and return current balance"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get sum of all credits
    cursor.execute('''
        SELECT COALESCE(SUM(amount), 0) FROM transactions 
        WHERE user_id = ? AND type = 'credit'
    ''', (user_id,))
    credits = cursor.fetchone()[0]
    
    # Get sum of all debits
    cursor.execute('''
        SELECT COALESCE(SUM(amount), 0) FROM transactions 
        WHERE user_id = ? AND type = 'debit'
    ''', (user_id,))
    debits = cursor.fetchone()[0]
    
    conn.close()
    return credits - debits

def add_transaction(user_id: int, trans_type: str, amount: float, 
                   category: str, reason: str = '') -> Tuple[bool, str]:
    """Add new transaction and update balance"""
    try:
        current_balance = get_user_balance(user_id)
        
        # Check for insufficient balance on debit
        if trans_type == 'debit' and current_balance < amount:
            return False, f"Insufficient balance! Current: ₹{current_balance:,.2f}, Required: ₹{amount:,.2f}"
        
        # Calculate new balance
        if trans_type == 'credit':
            new_balance = current_balance + amount
        else:
            new_balance = current_balance - amount
        
        # Insert transaction
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO transactions (user_id, type, amount, category, reason, transaction_date, balance_after)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, trans_type, amount, category, reason, get_india_time(), new_balance))
        
        conn.commit()
        conn.close()
        
        return True, "Transaction added successfully"
    except Exception as e:
        return False, f"Error adding transaction: {str(e)}"

def edit_transaction(transaction_id: int, user_id: int, updated_data: Dict) -> Tuple[bool, str]:
    """Edit existing transaction and recalculate balances"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get original transaction
        cursor.execute('SELECT * FROM transactions WHERE id = ? AND user_id = ?', 
                      (transaction_id, user_id))
        original = cursor.fetchone()
        
        if not original:
            conn.close()
            return False, "Transaction not found"
        
        # Update transaction
        cursor.execute('''
            UPDATE transactions 
            SET type = ?, amount = ?, category = ?, reason = ?
            WHERE id = ? AND user_id = ?
        ''', (updated_data['type'], updated_data['amount'], updated_data['category'], 
              updated_data['reason'], transaction_id, user_id))
        
        # Recalculate all balances from the beginning
        recalculate_balances(user_id, cursor)
        
        conn.commit()
        conn.close()
        
        return True, "Transaction updated successfully"
    except Exception as e:
        return False, f"Error updating transaction: {str(e)}"

def delete_transaction(transaction_id: int, user_id: int) -> Tuple[bool, str]:
    """Delete transaction and recalculate balances"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Delete transaction
        cursor.execute('DELETE FROM transactions WHERE id = ? AND user_id = ?', 
                      (transaction_id, user_id))
        
        if cursor.rowcount == 0:
            conn.close()
            return False, "Transaction not found"
        
        # Recalculate all balances
        recalculate_balances(user_id, cursor)
        
        conn.commit()
        conn.close()
        
        return True, "Transaction deleted successfully"
    except Exception as e:
        return False, f"Error deleting transaction: {str(e)}"

def recalculate_balances(user_id: int, cursor):
    """Recalculate balance_after for all transactions"""
    # Get all transactions ordered by date
    cursor.execute('''
        SELECT id, type, amount FROM transactions 
        WHERE user_id = ? 
        ORDER BY transaction_date ASC, id ASC
    ''', (user_id,))
    
    transactions = cursor.fetchall()
    balance = 0
    
    for trans in transactions:
        if trans['type'] == 'credit':
            balance += trans['amount']
        else:
            balance -= trans['amount']
        
        cursor.execute('UPDATE transactions SET balance_after = ? WHERE id = ?', 
                      (balance, trans['id']))

def get_transactions(user_id: int, filters: Optional[Dict] = None, 
                     page: int = 1, per_page: int = 20) -> List[Dict]:
    """Get filtered transactions with pagination"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM transactions WHERE user_id = ?'
    params = [user_id]
    
    if filters:
        if filters.get('type') and filters['type'] != 'both':
            query += ' AND type = ?'
            params.append(filters['type'])
        
        if filters.get('category'):
            query += ' AND category = ?'
            params.append(filters['category'])
        
        if filters.get('date_from'):
            query += ' AND transaction_date >= ?'
            params.append(filters['date_from'])
        
        if filters.get('date_to'):
            query += ' AND transaction_date <= ?'
            params.append(filters['date_to'])
        
        if filters.get('min_amount'):
            query += ' AND amount >= ?'
            params.append(filters['min_amount'])
        
        if filters.get('max_amount'):
            query += ' AND amount <= ?'
            params.append(filters['max_amount'])
        
        if filters.get('search'):
            query += ' AND reason LIKE ?'
            params.append(f"%{filters['search']}%")
    
    query += ' ORDER BY transaction_date DESC, id DESC'
    
    # Add pagination
    offset = (page - 1) * per_page
    query += f' LIMIT {per_page} OFFSET {offset}'
    
    cursor.execute(query, params)
    transactions = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return transactions

def get_transaction_count(user_id: int, filters: Optional[Dict] = None) -> int:
    """Get total count of transactions for pagination"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = 'SELECT COUNT(*) FROM transactions WHERE user_id = ?'
    params = [user_id]
    
    if filters:
        if filters.get('type') and filters['type'] != 'both':
            query += ' AND type = ?'
            params.append(filters['type'])
        
        if filters.get('category'):
            query += ' AND category = ?'
            params.append(filters['category'])
        
        if filters.get('date_from'):
            query += ' AND transaction_date >= ?'
            params.append(filters['date_from'])
        
        if filters.get('date_to'):
            query += ' AND transaction_date <= ?'
            params.append(filters['date_to'])
        
        if filters.get('min_amount'):
            query += ' AND amount >= ?'
            params.append(filters['min_amount'])
        
        if filters.get('max_amount'):
            query += ' AND amount <= ?'
            params.append(filters['max_amount'])
        
        if filters.get('search'):
            query += ' AND reason LIKE ?'
            params.append(f"%{filters['search']}%")
    
    cursor.execute(query, params)
    count = cursor.fetchone()[0]
    
    conn.close()
    return count

def get_summary_stats(user_id: int) -> Dict:
    """Get dashboard summary statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Current balance
    current_balance = get_user_balance(user_id)
    
    # Total credit
    cursor.execute('''
        SELECT COALESCE(SUM(amount), 0) FROM transactions 
        WHERE user_id = ? AND type = 'credit'
    ''', (user_id,))
    total_credit = cursor.fetchone()[0]
    
    # Total debit
    cursor.execute('''
        SELECT COALESCE(SUM(amount), 0) FROM transactions 
        WHERE user_id = ? AND type = 'debit'
    ''', (user_id,))
    total_debit = cursor.fetchone()[0]
    
    # Today's expense
    today = datetime.now().date()
    cursor.execute('''
        SELECT COALESCE(SUM(amount), 0) FROM transactions 
        WHERE user_id = ? AND type = 'debit' AND DATE(transaction_date) = ?
    ''', (user_id, today))
    today_expense = cursor.fetchone()[0]
    
    # This month's credit
    first_day = today.replace(day=1)
    cursor.execute('''
        SELECT COALESCE(SUM(amount), 0) FROM transactions 
        WHERE user_id = ? AND type = 'credit' AND DATE(transaction_date) >= ?
    ''', (user_id, first_day))
    month_credit = cursor.fetchone()[0]
    
    # This month's debit
    cursor.execute('''
        SELECT COALESCE(SUM(amount), 0) FROM transactions 
        WHERE user_id = ? AND type = 'debit' AND DATE(transaction_date) >= ?
    ''', (user_id, first_day))
    month_debit = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'current_balance': current_balance,
        'total_credit': total_credit,
        'total_debit': total_debit,
        'today_expense': today_expense,
        'month_credit': month_credit,
        'month_debit': month_debit
    }

def get_category_totals(user_id: int, date_range: Optional[Tuple] = None) -> Dict:
    """Get spending by category"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT category, SUM(amount) as total 
        FROM transactions 
        WHERE user_id = ? AND type = 'debit'
    '''
    params = [user_id]
    
    if date_range:
        query += ' AND transaction_date BETWEEN ? AND ?'
        params.extend(date_range)
    
    query += ' GROUP BY category ORDER BY total DESC'
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    
    conn.close()
    
    return {row['category']: row['total'] for row in results}

def get_daily_totals(user_id: int, days: int = 30) -> List[Dict]:
    """Get daily spending for last N days"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    start_date = datetime.now().date() - timedelta(days=days-1)
    
    cursor.execute('''
        SELECT DATE(transaction_date) as date, 
               SUM(CASE WHEN type = 'debit' THEN amount ELSE 0 END) as debit,
               SUM(CASE WHEN type = 'credit' THEN amount ELSE 0 END) as credit
        FROM transactions 
        WHERE user_id = ? AND DATE(transaction_date) >= ?
        GROUP BY DATE(transaction_date)
        ORDER BY date ASC
    ''', (user_id, start_date))
    
    results = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return results

def get_weekly_totals(user_id: int, weeks: int = 12) -> List[Dict]:
    """Get weekly spending for last N weeks"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    start_date = datetime.now().date() - timedelta(weeks=weeks)
    
    cursor.execute('''
        SELECT strftime('%Y-W%W', transaction_date) as week,
               SUM(CASE WHEN type = 'debit' THEN amount ELSE 0 END) as debit,
               SUM(CASE WHEN type = 'credit' THEN amount ELSE 0 END) as credit
        FROM transactions 
        WHERE user_id = ? AND DATE(transaction_date) >= ?
        GROUP BY week
        ORDER BY week ASC
    ''', (user_id, start_date))
    
    results = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return results

def get_monthly_totals(user_id: int, months: int = 12) -> List[Dict]:
    """Get monthly spending for last N months"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    start_date = (datetime.now().replace(day=1) - timedelta(days=30*months)).date()
    
    cursor.execute('''
        SELECT strftime('%Y-%m', transaction_date) as month,
               SUM(CASE WHEN type = 'debit' THEN amount ELSE 0 END) as debit,
               SUM(CASE WHEN type = 'credit' THEN amount ELSE 0 END) as credit
        FROM transactions 
        WHERE user_id = ? AND DATE(transaction_date) >= ?
        GROUP BY month
        ORDER BY month ASC
    ''', (user_id, start_date))
    
    results = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return results

def get_transaction_by_id(transaction_id: int, user_id: int) -> Optional[Dict]:
    """Get a single transaction by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM transactions WHERE id = ? AND user_id = ?', 
                  (transaction_id, user_id))
    result = cursor.fetchone()
    
    conn.close()
    
    return dict(result) if result else None

def get_all_categories(user_id: int) -> List[str]:
    """Get all unique categories used by user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT category FROM transactions 
        WHERE user_id = ? 
        ORDER BY category
    ''', (user_id,))
    
    categories = [row['category'] for row in cursor.fetchall()]
    
    conn.close()
    
    return categories