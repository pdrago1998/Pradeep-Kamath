from flask import *
import sqlite3
import os
import base64
import secrets
import numpy as np
import pickle
from warnings import filterwarnings
filterwarnings("ignore")
RF=pickle.load(open("XGBOOST.pkl","rb"))

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

command = """CREATE TABLE IF NOT EXISTS user(name TEXT, password TEXT, mobile TEXT, email TEXT)"""
cursor.execute(command)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':

        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()

        phone = request.form['phone']
        password = request.form['password']

        query = "SELECT * FROM user WHERE mobile = '"+phone+"' AND password= '"+password+"'"
        cursor.execute(query)

        result = cursor.fetchone()

        if result:
            session['phone'] = phone
            return render_template('userlog.html')
        else:
            return render_template('signin.html', msg='Sorry, Incorrect Credentials Provided,  Try Again')

    return render_template('signin.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':

        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()

        name = request.form['name']
        password = request.form['password']
        mobile = request.form['phone']
        email = request.form['email']
        
        print(name, mobile, email, password)

        cursor.execute("INSERT INTO user VALUES ('"+name+"', '"+password+"', '"+mobile+"', '"+email+"')")
        connection.commit()

        return render_template('signin.html', msg='Successfully Registered')
    
    return render_template('signup.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()

        data = request.form
        values = []
        keys = []
        for key in data:
            keys.append(key)
            values.append(int(data[key]))

        print(keys, values)
        data = np.array([values])
        prediction = RF.predict(data)[0]
        print(prediction)
        if prediction ==1:
            print("Churn")
            return render_template('userlog.html', result='Prediction is : Churn')
        else:
            return render_template('userlog.html', result='Prediction is : No Churn')
    return render_template('userlog.html')

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
