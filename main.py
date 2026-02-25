from flask import Flask, render_template, request, redirect, jsonify , send_from_directory
import sqlite3
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from chatbot import get_response

app = Flask(__name__)

# Database setup
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create table with proper schema
def init_db():
    conn = get_db_connection()
    try:
        # Check if table exists and has old schema
        cursor = conn.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if not columns:
            # Table doesn't exist, create it
            conn.execute('''
                CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                first_name TEXT,
                last_name TEXT,

                email TEXT NOT NULL,
                company TEXT,
                phone TEXT,

                country TEXT,
                monthly_volume TEXT,

                message TEXT,

                source TEXT DEFAULT 'contact-page',

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
        elif 'name' in columns and 'first_name' not in columns:
            # Old schema exists, migrate it
            conn.execute('''
                CREATE TABLE users_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    company TEXT,
                    phone TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # Copy existing data if any
            conn.execute('''
                INSERT INTO users_new (first_name, last_name, email, company, phone, message)
                SELECT COALESCE(name, ''), '', COALESCE(email, ''), '', '', ''
                FROM users
            ''')
            conn.execute('DROP TABLE users')
            conn.execute('ALTER TABLE users_new RENAME TO users')
    except sqlite3.OperationalError:
        # Table doesn't exist, create it
        conn.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL,
                company TEXT,
                phone TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    conn.commit()
    conn.close()

# Initialize database
init_db()


# --- SEO Routes (NEW) ---
@app.route('/robots.txt')
def robots():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'sitemap.xml')

    

@app.route('/')
def index():
    return render_template('base/index.html')

@app.route('/solutions/high-risk-accounts')
def high_risk_accounts():
    return render_template('solutions/high-risk-accounts.html')

@app.route('/solutions/payment-gateway')
def payment_gateway():
    return render_template('solutions/payment-gateway.html')

@app.route('/solutions/chargeback-prevention')
def chargeback_prevention():
    return render_template('solutions/chargeback-prevention.html')

@app.route('/solutions/offshore-processing')
def offshore_processing():
    return render_template('solutions/offshore-processing.html')

# --- Industry Routes --- 
@app.route('/industries/e-commerce')
def ecommerce():
    return render_template('industries/e-commerce.html')

@app.route('/industries/cbd-hemp')
def cbd_hemp():
    return render_template('industries/cbd-hemp.html')

@app.route('/industries/adult-entertainment')
def adult_entertainment():
    return render_template('industries/adult-entertainment.html')

@app.route('/industries/forex-crypto')
def forex_crypto():
    return render_template('industries/forex-crypto.html')

@app.route('/partners/partners')
def partners():
    return render_template('partners/partners.html')





@app.route('/chatbots')
def chatbots():
    return render_template('chatbots.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact')
def contact():
    return render_template('base/contact.html')


@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Get all form fields
        first_name = request.form.get('firstName', '')
        last_name = request.form.get('lastName', '')

        email = request.form.get('email', '')
        company = request.form.get('company', '')
        phone = request.form.get('phone', '')

        country = request.form.get('country', '')
        monthly_volume = request.form.get('monthly_volume', '')

        message = request.form.get('message', '')

        source = request.form.get('source', 'contact-page')

        # Validate required fields
        if not email:
            return jsonify({'success': False, 'message': 'Please fill in all required fields.'}), 400

        # Print all form information
        print("=" * 50)
        print("FORM SUBMISSION RECEIVED")
        print("=" * 50)
        print(f"First Name: {first_name}")
        print(f"Last Name: {last_name}")
        print(f"Email Address: {email}")
        print(f"Company Name: {company}")
        print(f"Phone Number: {phone}")
        print(f"Business Description: {message}")
        print("=" * 50)

        # Store all fields in database
        conn = get_db_connection()
        conn.execute(
            '''INSERT INTO users 
            (first_name, last_name, email, company, phone, country, monthly_volume, message, source) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (first_name, last_name, email, company, phone, country, monthly_volume, message, source)
        )
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Form submitted successfully! We\'ll get back to you soon.'}), 200

    except Exception as e:
        print(f"Error submitting form: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to submit form. Please try again later.'}), 500

@app.route('/chatbot', methods=['POST'])
def chatbot():
    try:
        data = request.get_json()
        user_input = data.get('user_input', '')
        
        if not user_input:
            return jsonify({'response': 'Please provide a message.'}), 400
        
        # Get response from Gemini API
        response = get_response(user_input)
        
        return jsonify({'response': response}), 200
        
    except Exception as e:
        print(f"Error in chatbot endpoint: {str(e)}")
        return jsonify({'response': 'I\'m sorry, I\'m having trouble processing your request right now. Please try again later.'}), 500


@app.route('/landing')
def landing():
    print("landing page  ")
    return render_template('features/landing.html')







if __name__ == "__main__":
    app.run(debug=True)
