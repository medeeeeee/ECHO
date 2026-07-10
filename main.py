from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    points = db.Column(db.Integer, default=0)
    plants = db.Column(db.String(200), default=0)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Aquí puedes agregar la lógica para registrar al usuario en la base de datos
        # Por ejemplo, puedes crear un nuevo objeto `User` y guardarlo en la base de datos
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    error=''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_db=User.query.all()
        for user in user_db:
            if user.email == email and user.password == password:
                session['user_id'] = user.id
                return redirect('/dashboard')
        error='Correo electrónico o contraseña incorrectos'
        return render_template('index.html', error=error)
        # Aquí puedes agregar la lógica para verificar el correo electrónico y la contraseña en la base de datos
        # Por ejemplo, puedes consultar la base de datos para verificar si el usuario existe y si la contraseña es correcta

        # Si el inicio de sesión es exitoso, puedes redirigir al usuario a otra página
    else:
        return redirect('/')


app.run(debug=True)