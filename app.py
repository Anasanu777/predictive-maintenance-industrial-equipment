import joblib
import sqlite3
import datetime
from flask import Flask, request, render_template,redirect,url_for,flash,session

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'pmie'

# SQLite database setup
DATABASE = 'pmie.db'

# Load the Random Forest model
random_forest_model = joblib.load('random_forest_model.pkl')

@app.route('/')
def index():
    
    if 'type' in session and session['type'] == 'user':
        show_modal = request.args.get('show_modal', 'false') 
        data={
            'prediction': request.args.get('prediction'), 
            'feature_1':request.args.get('feature_1'),
            'feature_2':request.args.get('feature_2'), 
            'feature_3':request.args.get('feature_3'), 
            'feature_4':request.args.get('feature_4'),
            }
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE type != ?", ('admin',))
        users = c.fetchall()

        c.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
        profiles = c.fetchone()
        all_data={'users':users, 'profiles':profiles, 'data':data}
        
        return render_template('index.html',show_modal=show_modal,**all_data)
    else:
        return render_template('index.html')

@app.route('/register_db', methods=["GET", "POST"])
def register_db():
    if request.method == 'POST':
        name = request.form['Name']
        #username = request.form['username']
        email = request.form['Email']
        mobile = request.form['Phone Number']
        password = request.form['password']
        
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        existing_user = c.fetchone()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
        else:
            c.execute("INSERT INTO users (name, email, phone, password, type) VALUES (?, ?, ?, ?, ?)",
                      (name, email, mobile,  password, 'user'))
            conn.commit()
            conn.close()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('index'))
    return redirect(url_for('index'))

@app.route('/authe', methods=["GET", "POST"])
def authe():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print("abcd")
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("SELECT id, name, type FROM users WHERE email = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()
       
        if user:
            session['user_id'] = user[0]  # Store user_id in session
            session['username'] = user[1]  # Store username in session
            session['type'] = user[2] # Store User Type in session
            print(session['type'])
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
        return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session['type']=''
    return redirect(url_for('index'))

@app.route('/predict', methods=['POST'])
def predict():
    print("asfnsfsdkjndgjsnd")
    try:
        # Get data from the form
        feature_1 = float(request.form['feature_1'])
        feature_2 = float(request.form['feature_2'])
        feature_3 = float(request.form['feature_3'])
        feature_4 = float(request.form['feature_4'])

        # Print the features for debugging
        print(f"Features: {feature_1}, {feature_2}, {feature_3}, {feature_4}")

        # Make prediction using the Random Forest model
        result = random_forest_model.predict([[feature_1, feature_2, feature_3, feature_4]])[0]
        
        # Print the result for debugging
        print(f"Prediction Result: {result}")

        # Convert the prediction result to a readable format
        prediction_text = "Maintenance Required" if result == 1 else "No Maintenance Required"

        # Render the result page with the prediction
        data={'prediction': prediction_text, 'feature_1':feature_1,'feature_2':feature_2, 'feature_3':feature_3, 'feature_4':feature_4}
        return redirect(url_for('index', show_modal='true', **data))

    except Exception as e:
        # If an error occurs, return the error message
        return str(e)

if __name__ == '__main__':
    app.run(debug=True)
