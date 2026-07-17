from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "una_clave_secreta"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=True)
    points = db.Column(db.Integer, default=0)
    plant_name = db.Column(db.String(200), default=0)
    streak = db.Column(db.Integer, default=0)
    lvl = db.Column(db.Integer, default=0)
    impact = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<User {self.id}>'

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Task {self.id}>'

class DiaryEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<DiaryEntry {self.id}>'


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
    
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        return render_template('dashboard.html', user=user)
    else:
        return redirect('/')
    
@app.route('/ajustes')
def ajustes():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        return render_template('settings.html', user=user)
    else:
        return redirect('/')
    
@app.route('/guardar_ajustes', methods=['POST'])
def guardar_ajustes():
    if 'user_id' not in session:
        return redirect('/')

    user = User.query.get(session['user_id'])

    user.username = request.form['username']
    user.email = request.form['email']
    user.plant_name = request.form['plant_name']

    db.session.commit()

    return redirect('/ajustes')
    
@app.route('/diario')
def diario():
    if 'user_id' not in session:
        return redirect('/')

    entradas = DiaryEntry.query.filter_by(
        user_id=session['user_id']
    )

    return render_template("diario.html", entradas=entradas)

@app.route('/guardar_entrada', methods=['POST'])
def guardar_entrada():
    if 'user_id' not in session:
        return redirect('/')

    entrada = DiaryEntry(
        user_id=session['user_id'],
        title=request.form['titulo'],
        content=request.form['texto'],
        date=request.form['fecha']
    )

    db.session.add(entrada)
    db.session.commit()

    return redirect('/diario')

@app.route('/tareas')
def tareas():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        return render_template('registro.html', user=user)
    else:
        return redirect('/')
    
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

with app.app_context():
    db.create_all()

app.run(debug=True)