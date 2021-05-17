from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)


# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('welcome'))
    return render_template('login.html', error=error)

# landing page after login
@app.route('/welcome')
def welcome():
    return render_template('welcome.html')