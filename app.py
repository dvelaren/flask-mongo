from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import datetime
import random
import bcrypt

app = Flask(__name__)
app.secret_key = b'ChangeMeDavid'
app.config["MONGO_URI"] = "mongodb://10.0.20.30:27017/myDatabase"
mongo = PyMongo(app)
adq = mongo.db.adq


@app.route('/')
def home():
    if 'email' in session:
        samples = adq.find().sort('_id', -1)
        return render_template('home.html', samples=samples)
    else:
        return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'email': request.form['email']})
        if existing_user is None:
            if request.form['password'] == request.form['repassword']:
                hashpass = bcrypt.hashpw(
                    request.form['password'].encode('utf-8'), bcrypt.gensalt())
                users.insert({'name': request.form['username'], 'password': hashpass,
                              'ext': request.form['ext'], 'tel': request.form['tel'], 'email': request.form['email']})
                session['email'] = request.form['email']
                return redirect(url_for('home'))
            else:
                print("Passwords don't match")
                flash("Passwords don't match", 'danger')
        else:
            print("Passwords don't match")
            flash('That username already exists', 'danger')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'email': request.form['email']})
        if login_user:
            if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password']) == login_user['password']:
                session['email'] = request.form['email']
                return redirect(url_for('home'))
            else:
                print("Wrong password")
                flash("Wrong password", 'danger')
        else:
            print("Email doesn't exists in our DB")
            flash("Email doesn't exists in our DB", 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    if 'email' in session:
        session.pop('email', None)
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))


@app.route('/insert')
def insert():
    if 'email' in session:
        x = random.randint(0, 9)
        sample = {"x": x,
                  "x2": x**2,
                  "user": session['email'],
                  "date": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}
        id_sam = adq.insert_one(sample).inserted_id
        print(f"Inserted {sample} by user: {sample['user']}")
        flash(
            f"Inserted doc with date: {sample['date']} by user: {sample['user']}", 'success')
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))


@app.route('/delete')
def delete():
    if 'email' in session:
        doc_id = adq.find().sort('_id', -1).limit(1)
        adq.delete_one(doc_id[0])
        print(f"Removed doc with date: {doc_id[0]['date']}")
        flash(f"Removed doc with date: {doc_id[0]['date']}", 'danger')
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))


@app.route('/delete/id/<id>')
def delete_item(id):
    if 'email' in session:
        doc_id = adq.find_one({"_id": ObjectId(id)})
        print(doc_id)
        adq.delete_one(doc_id)
        print(f"Removed doc with date: {doc_id['date']}")
        flash(f"Removed doc with date: {doc_id['date']}", 'danger')
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
