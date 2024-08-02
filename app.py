from flask import Flask, render_template



app = Flask(__name__, static_folder='static')


@app.route('/')
def home():
    return render_template('studentLogin.html')

@app.route('/studentSignUp')
def studentSignUp():
    return render_template('/studentSignUp.html')

@app.route('/adminLogin')
def adminLogin():
    return render_template('adminLogin.html')

@app.route('/adminSignUp')
def signUp():
    return render_template('adminSignUp.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)