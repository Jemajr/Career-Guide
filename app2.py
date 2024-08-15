from flask import Flask, render_template, jsonify, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text
from main import engine

app = Flask(__name__, static_folder='static')


@app.route('/', methods=['GET', 'POST'])
def login():
    return render_template('studentLogin.html')


@app.route('/studentSignUp', methods=['GET', 'POST'])
def student_signUp():
    if request.method == 'POST':
        # Extract data from the form
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        school_name = request.form['school_name']
        school_email = request.form['school_email']
        password = request.form['password']

        _hashed_password = generate_password_hash(password)
        
        with engine.connect() as connection:    
            account = connection.execute(text("select * from students WHERE email  = :email").bindparams(email=school_email))
    
            # If account exists show error and validation checks
            if account.fetchone():
                flash('Account already exists!')
    
            # Account doesnt exist, add new account into students
            else:
                insert_statement = text("INSERT INTO students (first_name, last_name, school, password_hash, email) VALUES (:first_name, :last_name, :school, :password_hash, :email)").bindparams(
                    first_name=first_name,
                    last_name=last_name,
                    school=school_name,
                    password_hash=_hashed_password,
                    email=school_email
                )
                connection.execute(insert_statement)
                connection.commit()
                flash('You have successfully registered!')
    return render_template('/studentSignUp.html')

@app.route('/adminLogin')
def admin_login():
    return render_template('adminLogin.html')

@app.route('/adminSignUp', methods=['GET', 'POST'])
def admin_signUp():
    if request.method == 'POST':
        # Handle form submission
        school_name = request.form['school_name']
        career_center_email = request.form['career_center_email']
        # Process the data as needed
        return 'Form submitted successfully!'  # Or redirect to another route
    return render_template('/adminSignUp.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)