# Personal Payment Tracker

A privacy-focused, offline-first financial tracking web application that runs entirely on your local system. Track your income, expenses, and financial health with complete data ownership and privacy.

## ✨ Features

### Core Features
- **🔐 Secure Authentication** - User registration and login with password hashing
- **💰 Transaction Management** - Add, edit, and delete credit/debit transactions
- **📊 Visual Analytics** - 6 interactive charts showing spending patterns
- **🔍 Advanced Filtering** - Filter transactions by date, type, category, and amount
- **📥 Export Data** - Export to Excel, PDF, and CSV formats
- **💾 Automatic Backups** - Daily database backups with 30-day retention
- **📱 Mobile Responsive** - Works seamlessly on desktop, tablet, and mobile devices

### Privacy & Security
- ✅ **100% Local Storage** - All data stays on your device
- ✅ **No Cloud Dependency** - Works completely offline
- ✅ **Password Protection** - Secure user authentication
- ✅ **Data Ownership** - You control your financial data
- ✅ **No External APIs** - Zero data transmission to third parties

## 🚀 Quick Start

### Prerequisites

- **Python 3.8 or higher**
- **pip** (Python package installer)

### Installation

1. **Clone or download this repository**
```bash
cd payment-tracker
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Download Chart.js library** (Required for charts)
```bash
curl -L https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js -o static/lib/chart.min.js
```

Alternatively, download manually from:
https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js
and save as `static/lib/chart.min.js`

4. **Run the application**
```bash
python app.py
```

5. **Open your browser and go to:**
```
http://127.0.0.1:5000
```

## 📱 Mobile Access (Same Network)

Access the application from your mobile device on the same WiFi network:

1. **Find your computer's IP address:**

   **Windows:**
   ```bash
   ipconfig
   ```
   Look for "IPv4 Address"

   **Mac/Linux:**
   ```bash
   ifconfig
   ```
   Look for "inet" address

2. **On your mobile browser, navigate to:**
   ```
   http://YOUR_IP_ADDRESS:5000
   ```
   Example: `http://192.168.1.100:5000`

⚠️ **Security Note:** Only use on trusted networks!

## 📚 User Guide

### First Time Setup

1. Click **Register** to create your account
2. Choose a username (3-20 characters)
3. Create a strong password (minimum 8 characters with uppercase, lowercase, and number)
4. You'll be automatically logged in after registration

### Managing Transactions

#### Adding Transactions

1. Click **"+ Add Transaction"** button
2. Select transaction type:
   - **Credit** - Money you received (salary, income, refunds)
   - **Debit** - Money you spent (expenses, bills, purchases)
3. Enter amount
4. Select category (Food, Travel, Shopping, Bills, etc.)
5. Add optional description
6. Click **"Add Transaction"**

💡 **Important:** You cannot add a debit transaction if you have insufficient balance!

#### Editing Transactions

1. Go to **Transactions** page
2. Click the ✏️ (edit) icon next to any transaction
3. Update the details
4. Click **"Update Transaction"**

⚠️ Editing recalculates all subsequent balances automatically

#### Deleting Transactions

1. Go to **Transactions** page
2. Click the 🗑️ (delete) icon
3. Confirm deletion
4. All subsequent balances will be recalculated

### Filtering & Search

On the Transactions page:

- **Date Range** - Filter by start and end date
- **Type** - Show only credits, debits, or both
- **Category** - Filter by specific spending category
- **Amount Range** - Set minimum and maximum amounts
- **Search** - Search in transaction descriptions

Click **Apply Filters** to filter or **Clear Filters** to reset.

### Reports & Analytics

The Reports page provides:

#### Summary Statistics
- Current Balance
- Total Credit
- Total Debit
- Savings Rate

#### Interactive Charts
1. **Credit vs Debit** - Pie chart showing income vs expenses
2. **Category Spending** - Bar chart of spending by category
3. **Daily Spending** - Last 30 days expense trend
4. **Weekly Spending** - Last 12 weeks trend
5. **Monthly Trend** - Last 12 months credit and debit comparison
6. **Balance Trend** - How your balance changed over time

### Exporting Data

From the Reports page:

1. Select export range:
   - All Transactions
   - Current Month
   - Last 3 Months
   - Custom Date Range

2. Choose format:
   - **Excel (.xlsx)** - Formatted spreadsheet with summary
   - **PDF (.pdf)** - Professional report with charts
   - **CSV (.csv)** - Simple format for importing elsewhere

3. Click the export button to download

## 🗄️ Data Management

### Database Location

All data is stored in `database.db` in the project folder.

**⚠️ IMPORTANT:** 
- Never delete this file unless you want to reset everything
- Back it up regularly to external storage
- Keep it secure as it contains your financial data

### Backups

#### Automatic Backups
- Created daily automatically
- Stored in `backups/` folder
- Last 30 days retained
- Filename format: `backup_YYYY-MM-DD.db`

#### Manual Backups
1. Go to **Settings** page
2. Click **"Create Backup Now"**
3. Backup saved to `backups/` folder

#### Restoring from Backup
1. Stop the application
2. Replace `database.db` with your backup file
3. Restart the application

## 🔒 Security Best Practices

### Password Requirements
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- Special characters recommended

### General Security
- ✅ Use a strong, unique password
- ✅ Log out when finished
- ✅ Create regular backups
- ✅ Only access on trusted networks
- ✅ Keep your computer secure
- ❌ Don't share your credentials
- ❌ Don't access over public WiFi

## 📁 Project Structure

```
payment-tracker/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── database.db                 # SQLite database (auto-created)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── templates/                  # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── transactions.html
│   ├── edit_transaction.html
│   ├── reports.html
│   └── settings.html
│
├── static/                     # Static files
│   ├── css/
│   │   ├── style.css
│   │   └── responsive.css
│   ├── js/
│   │   ├── main.js
│   │   ├── charts.js
│   │   └── validation.js
│   └── lib/
│       └── chart.min.js       # Chart.js library
│
├── utils/                      # Helper functions
│   ├── __init__.py
│   ├── db_helper.py           # Database operations
│   ├── auth_helper.py         # Authentication
│   └── export_helper.py       # Export functions
│
├── backups/                    # Auto-backup folder
└── exports/                    # Exported reports
```

## 🛠️ Technical Stack

### Backend
- **Flask 3.0.0** - Web framework
- **SQLite3** - Database (no server required)
- **Werkzeug** - Password hashing
- **openpyxl** - Excel export
- **reportlab** - PDF generation

### Frontend
- **HTML5** - Semantic structure
- **CSS3** - Modern responsive design
- **Vanilla JavaScript** - No external JS dependencies
- **Chart.js** - Data visualization

## ❓ Troubleshooting

### Charts not displaying
**Problem:** Charts show blank or error
**Solution:** Ensure Chart.js is downloaded to `static/lib/chart.min.js`

### Can't access from mobile
**Problem:** Mobile can't connect to the app
**Solution:** 
- Ensure both devices are on same WiFi
- Check firewall isn't blocking port 5000
- Verify you're using correct IP address

### Database locked error
**Problem:** "Database is locked" message
**Solution:** 
- Close any other database connections
- Restart the application
- Check file permissions

### Insufficient balance error
**Problem:** Can't add debit transaction
**Solution:** This is by design - you need credit balance first

### Lost password
**Problem:** Forgot login credentials
**Solution:** 
- No password recovery (privacy by design)
- Delete `database.db` to start fresh (loses all data)
- Or manually reset password in database using Python

## 🔄 Updates & Maintenance

### Updating the Application
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart application
python app.py
```

### Database Migration
When updating, your database automatically maintains compatibility. No manual migration needed.

## 📊 Default Categories

The application includes these default categories:
- 💵 Salary
- 🍔 Food
- 🚗 Travel
- 🛍️ Shopping
- 💡 Bills
- 🎬 Entertainment
- 🏥 Healthcare
- 📚 Education
- 📦 Other

You can use any category you want when adding transactions.

## 🌟 Tips & Tricks

1. **Regular Backups:** Create weekly backups before major changes
2. **Descriptive Reasons:** Add clear descriptions for better tracking
3. **Consistent Categories:** Use consistent category names
4. **Daily Updates:** Update transactions daily for accurate tracking
5. **Review Reports:** Check monthly reports to understand spending patterns
6. **Export Data:** Export quarterly for record keeping

## ⚖️ License

This is free and unencumbered software released into the public domain. You are free to use, modify, and distribute as you see fit.

## 🤝 Support

For issues or questions:
1. Check this README first
2. Review the troubleshooting section
3. Check application logs in the terminal
4. Verify all dependencies are installed

## 🎯 Future Enhancements (Optional)

Potential features you could add:
- [ ] Dark mode toggle
- [ ] Recurring transactions
- [ ] Budget goals per category
- [ ] Multi-currency support
- [ ] Receipt attachments
- [ ] Financial goal tracking
- [ ] Expense predictions
- [ ] Data import from CSV
- [ ] Multiple user accounts per installation
- [ ] Transaction tags

## 📝 Version

**Version 1.0** - Initial Release

---

**Made with ❤️ for financial privacy and data ownership**

**Remember:** Your financial data belongs to you. This application ensures it stays that way!