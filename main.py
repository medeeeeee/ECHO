from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel, _
from tareas import tareas
from datetime import date, datetime, timedelta
import random

app = Flask(__name__)
babel = Babel(app)
app.secret_key = "una_clave_secreta"
app.config['BABEL_DEFAULT_LOCALE'] = 'es'
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
    plant_type = db.Column(db.String(200), default=0)
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
    date = db.Column(db.String(100), nullable=False)

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

def create_task(user_id):

    hoy = str(date.today())
    tareas_hoy = Task.query.filter_by(
        user_id=user_id,
        date=hoy
    ).first()
    if tareas_hoy:
        return

    tareas_aleatorias = random.sample(tareas, 4)

    for tarea in tareas_aleatorias:
        db.session.add(Task(
            user_id=user_id,
            name=tarea["name"],
            points=tarea["points"],
            completed=False,
            date=str(date.today())
        ))
    db.session.commit()


def calcular_racha(user_id):
    tareas = Task.query.filter_by(
        user_id=user_id,
        completed=True
    ).all()
    dias = set()
    for tarea in tareas:
        dias.add(datetime.strptime(tarea.date, "%Y-%m-%d").date())
    if not dias:
        return 0
    dias = sorted(dias, reverse=True)
    hoy = date.today()

    # Si hoy no hizo ninguna tarea, empezamos desde ayer
    if dias[0] == hoy:
        anterior = hoy
    elif dias[0] == hoy - timedelta(days=1):
        anterior = hoy - timedelta(days=1)
    else:
        return 0
    racha = 1

    for dia in dias[1:]:
        if dia == anterior - timedelta(days=1):
            racha += 1
            anterior = dia
        else:
            break
    return racha


@babel.localeselector
def get_locale():
    return session.get('lang', 'es')

    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
        plant_name = request.form['plant_name']
        plant_type = request.form['plant_type']
        new_user = User(email=email, password=password, username=username, plant_name=plant_name, plant_type=plant_type)
        db.session.add(new_user)
        db.session.commit()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
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
    
    else:
        return redirect('/')
    
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        create_task(user_id)
        user = User.query.get(user_id)

        tareas = Task.query.filter_by(
            user_id=user_id,
            date=str(date.today())
        ).all()

        return render_template(
            'dashboard.html',
            user=user,
            tareas=tareas
        )
    else:
        return redirect('/')
    

@app.route('/completar_tareas', methods=['POST'])
def completar_tareas():
    if 'user_id' not in session:
        return redirect('/')

    user = User.query.get(session['user_id'])

    tareas_marcadas = request.form.getlist("tareas")

    for tarea_id in tareas_marcadas:
        tarea = Task.query.get(int(tarea_id))

        if tarea and not tarea.completed:
            tarea.completed = True

            user.points += tarea.points
            user.impact += 1

    db.session.commit()
    user.streak = calcular_racha(user.id)
    user.lvl = user.points // 100
    db.session.commit()

    return redirect('/dashboard')

    
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

    session["language"] = request.form["idioma"]
    return redirect(request.referrer)

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

@app.route('/tareas_reg')
def tareas_reg():
    if 'user_id' not in session:
        return redirect('/')

    tareas = Task.query.filter_by(
        user_id=session['user_id']
    ).order_by(Task.date.desc()).all()

    return render_template(
        'registro.html',
        user=User.query.get(session['user_id']),
        tareas=tareas
    )
    
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

with app.app_context():
    db.create_all()

app.run(debug=True)