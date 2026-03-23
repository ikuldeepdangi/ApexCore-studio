from flask import Flask, render_template, request, redirect, jsonify , send_from_directory
import sqlite3
import sys
import os
from flask_cors import CORS  # Add this import

import mysql.connector
from mysql.connector import Error

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from chatbot import get_response
from mail import send_mail # Works

app = Flask(__name__)
CORS(app, origins=["https://app.apexcorepay.com"])



# New MySQL Database connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME")
        )
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Updated init_db for MySQL syntax
def init_db():
    conn = get_db_connection()
    if not conn: return
    
    cursor = conn.cursor()
    try:
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(255),
                last_name VARCHAR(255),
                email VARCHAR(255) NOT NULL,
                company VARCHAR(255),
                phone VARCHAR(50),
                country VARCHAR(100),
                monthly_volume VARCHAR(100),
                message TEXT,
                source VARCHAR(100) DEFAULT 'contact-page',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create partner_leads table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS partner_leads (
                id INT AUTO_INCREMENT PRIMARY KEY,
                legal_name VARCHAR(255) NOT NULL,
                dba VARCHAR(255),
                cell_number VARCHAR(50) NOT NULL,
                email VARCHAR(255) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
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

@app.route('/about')
def about_us():
    return render_template('base/about_us.html')

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

# @app.route('/industries/forex-crypto')
# def forex_crypto():
#     return render_template('industries/forex-crypto.html')

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
        first_name = request.form.get('firstName', '')
        last_name = request.form.get('lastName', '')
        email = request.form.get('email', '')
        company = request.form.get('company', '')
        phone = request.form.get('phone', '')
        country = request.form.get('country', '')
        monthly_volume = request.form.get('monthly_volume', '')
        message = request.form.get('message', '')
        source = request.form.get('source', 'contact-page')

        if not email:
            return jsonify({'success': False, 'message': 'Please fill in all required fields.'}), 400

        # FIX: Open connection inside the route
        db_conn = get_db_connection()
        if not db_conn:
            return jsonify({'success': False, 'message': 'Database connection failed'}), 500
            
        cursor = db_conn.cursor()
        cursor.execute(
            '''INSERT INTO users 
            (first_name, last_name, email, company, phone, country, monthly_volume, message, source) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''', 
            (first_name, last_name, email, company, phone, country, monthly_volume, message, source)
        )
        db_conn.commit()
        cursor.close()
        db_conn.close()

        # Premium Email Notification
        subject = f"ApexCore Pay - New Lead: {first_name} {last_name}"
        body = f"""
        <div style="font-family: sans-serif; background-color: #f8fafc; padding: 40px 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                <div style="background-color: #0B2A45; padding: 30px; text-align: center;">
                    <img src="https://app.apexcorepay.com/static/logo.png" alt="ApexCore Pay" style="height: 50px; width: auto;">
                    <h2 style="color: #ffffff; margin-top: 15px; font-size: 20px; letter-spacing: 1px;">NEW LEAD ALERT</h2>
                </div>
                <div style="padding: 40px;">
                    <p style="color: #64748b; font-size: 14px; text-transform: uppercase; font-weight: bold; margin-bottom: 20px; border-bottom: 2px solid #3b82f6; display: inline-block;">Contact Details</p>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr><td style="padding: 10px 0; color: #94a3b8; width: 30%;">Name:</td><td style="font-weight: bold; color: #1e293b;">{first_name} {last_name}</td></tr>
                        <tr><td style="padding: 10px 0; color: #94a3b8;">Email:</td><td style="font-weight: bold; color: #3b82f6;">{email}</td></tr>
                        <tr><td style="padding: 10px 0; color: #94a3b8;">Phone:</td><td style="font-weight: bold; color: #1e293b;">{phone}</td></tr>
                        <tr><td style="padding: 10px 0; color: #94a3b8;">Company:</td><td style="font-weight: bold; color: #1e293b;">{company}</td></tr>
                        <tr><td style="padding: 10px 0; color: #94a3b8;">Volume:</td><td style="font-weight: bold; color: #10b981;">{monthly_volume}</td></tr>
                    </table>
                    <div style="margin-top: 30px; padding: 20px; background: #f1f5f9; border-radius: 8px;">
                        <p style="margin: 0 0 10px 0; color: #64748b; font-size: 12px; font-weight: bold;">MESSAGE / DESCRIPTION:</p>
                        <p style="margin: 0; color: #1e293b; line-height: 1.6;">{message}</p>
                    </div>
                </div>
                <div style="background: #f8fafc; padding: 20px; text-align: center; border-top: 1px solid #e2e8f0;">
                    <p style="margin: 0; color: #94a3b8; font-size: 12px;">Generated by ApexCore Pay System &copy; 2026</p>
                </div>
            </div>
        </div>
        """
        send_mail(subject, body)

        return jsonify({'success': True, 'message': 'Form submitted successfully!'}), 200

    except Exception as e:
        print(f"Error submitting form: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to submit form.'}), 500



# Update your init_db() function or add this below it
def init_partner_db():
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        # Use MySQL specific syntax: INT AUTO_INCREMENT PRIMARY KEY
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS partner_leads (
                id INT AUTO_INCREMENT PRIMARY KEY,
                legal_name VARCHAR(255) NOT NULL,
                dba VARCHAR(255),
                cell_number VARCHAR(50) NOT NULL,
                email VARCHAR(255) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
    except Error as e:
        print(f"Error initializing partner database: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        conn.close()

init_partner_db()

@app.route('/submit-partner', methods=['POST'])
def submit_partner():
    try:
        legal_name = request.form.get('legalName', '')
        dba = request.form.get('dba', '')
        cell = request.form.get('cell', '')
        email = request.form.get('email', '')
        description = request.form.get('description', '')

        if not email or not legal_name:
            return jsonify({'success': False, 'message': 'Required fields are missing.'}), 400

        # FIX: Open connection inside the route
        db_conn = get_db_connection()
        if not db_conn:
            return jsonify({'success': False, 'message': 'Database connection failed'}), 500

        cursor = db_conn.cursor()
        cursor.execute(
            '''INSERT INTO partner_leads (legal_name, dba, cell_number, email, description) 
            VALUES (%s, %s, %s, %s, %s)''',
            (legal_name, dba, cell, email, description)
        )
        db_conn.commit()
        cursor.close()
        db_conn.close()

        # Premium Partner Notification
        subject = f"ApexCore Pay - New Partner Application: {legal_name}"
        body = f"""
        <div style="font-family: sans-serif; background-color: #f5f3ff; padding: 40px 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; border: 1px solid #ddd6fe; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);">
                <div style="background-color: #1E73B9; padding: 30px; text-align: center;">
                    <h2 style="color: #ffffff; margin: 0; font-size: 20px; letter-spacing: 2px;">PARTNER REGISTRATION</h2>
                </div>
                <div style="padding: 40px;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr><td style="padding: 12px 0; color: #6b7280; border-bottom: 1px solid #f3f4f6;">Legal Name:</td><td style="padding: 12px 0; font-weight: bold; border-bottom: 1px solid #f3f4f6;">{legal_name}</td></tr>
                        <tr><td style="padding: 12px 0; color: #6b7280; border-bottom: 1px solid #f3f4f6;">DBA:</td><td style="padding: 12px 0; font-weight: bold; border-bottom: 1px solid #f3f4f6;">{dba}</td></tr>
                        <tr><td style="padding: 12px 0; color: #6b7280; border-bottom: 1px solid #f3f4f6;">Email:</td><td style="padding: 12px 0; font-weight: bold; color: #6366f1; border-bottom: 1px solid #f3f4f6;">{email}</td></tr>
                        <tr><td style="padding: 12px 0; color: #6b7280; border-bottom: 1px solid #f3f4f6;">Cell:</td><td style="padding: 12px 0; font-weight: bold; border-bottom: 1px solid #f3f4f6;">{cell}</td></tr>
                    </table>
                    <div style="margin-top: 30px;">
                        <p style="margin-bottom: 10px; color: #6b7280; font-size: 13px;">PARTNER OVERVIEW:</p>
                        <div style="padding: 20px; border-left: 4px solid #6366f1; background: #fdf2ff; font-style: italic; color: #4b5563;">
                            "{description}"
                        </div>
                    </div>
                    <a href="mailto:{email}" style="display: block; margin-top: 30px; padding: 15px; background: #1E73B9; color: #ffffff; text-align: center; text-decoration: none; border-radius: 8px; font-weight: bold;">Reply to Partner</a>
                </div>
            </div>
        </div>
        """
        send_mail(subject, body)

        return jsonify({'success': True, 'message': 'Partner application received!'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500



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
