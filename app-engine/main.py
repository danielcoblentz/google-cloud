from flask import Flask, request, jsonify, render_template, redirect, url_for
import pymysql
import os
import bcrypt  # Ensure bcrypt is installed

app = Flask(__name__)

def open_connection():
    """Establish a database connection."""
    try:
        connection = pymysql.connect(
            user=os.getenv('CLOUD_SQL_USERNAME'),
            password=os.getenv('CLOUD_SQL_PASSWORD'),
            db=os.getenv('CLOUD_SQL_DATABASE_NAME'),
            host=os.getenv('CLOUD_SQL_HOST'),  # If using public IP, or `unix_socket` for Cloud SQL proxy
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.MySQLError as e:
        print(e)
        return None

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('Uname')
    password = request.form.get('Pass')
    email = request.form.get('Email')
    is_organizer = request.form.get('remember') == 'on'  # Checkbox value

    if not username or not password or not email:
        return jsonify({"msg": "Missing fields"}), 400

    connection = open_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                # Check if the user already exists
                cursor.execute("SELECT * FROM Users WHERE email = %s OR username = %s", (email, username))
                user = cursor.fetchone()

                if user:
                    return jsonify({"msg": "User already exists"}), 400

                # Hash the password
                password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

                # Insert the new user
                cursor.execute(
                    "INSERT INTO Users (username, password_hash, email, is_organizer) VALUES (%s, %s, %s, %s)",
                    (username, password_hash, email, is_organizer)
                )
                connection.commit()

                return redirect(url_for('welcome'))

        except pymysql.MySQLError as e:
            return jsonify({"msg": str(e)}), 500

        finally:
            connection.close()

    return jsonify({"msg": "Database connection failed"}), 500

@app.route('/welcome', methods=['GET'])
def welcome():
    return "Welcome!"

if __name__ == '__main__':
    app.run(debug=True)
