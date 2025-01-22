from flask import Flask, render_template, request, flash, redirect,url_for, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
from app import create_client
from supabase import create_client, Client
from werkzeug.security import check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, Form, validators, TextAreaField
from wtforms.validators import DataRequired, Email, Length
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__)
app.secret_key = 'your_secret_key'
csrf = CSRFProtect(app)

# Configurazione Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'nicolaguarise00@gmail.com'  # Cambia con il tuo indirizzo email
app.config['MAIL_PASSWORD'] = 'zyrhvorphptgmqic'  # App password generata da Google
app.config['MAIL_DEFAULT_SENDER'] = 'nicolaguarise00@gmail.com'  # Mittente predefinito
mail = Mail(app)


# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User model for Flask-Login
class User(UserMixin):
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email

"""     @staticmethod
    def get(user_id):
        # Recupera l'utente dal database Supabase
        response = supabase.table("user").select("id, email, password").eq("email", user_id).execute()
        if response.data:
            user_data = response.data[0]
            return User(user_data['email'], user_data['id'])
        return None

    def check_password(self, password):
        # Verifica la password (hashing)
        response = supabase.table("user").select("password").eq("email", self.email).execute()
        if response.data:
            stored_password = response.data[0]['password']
            return check_password_hash(stored_password, password)
        return False

    def get_id(self):
        return self.email """

@login_manager.user_loader
def load_user(user_id):
    # Query to Supabase to get the user by ID
    response = supabase.table('user').select('*').eq('id', user_id).execute()
    user_data = response.data
    if user_data:
        user = user_data[0]
        return User(id=user['id'], name=user['name'], email=user['email'])
    return None


# Form per la registrazione
class RegistrationForm(FlaskForm):  # Usa FlaskForm al posto di Form
    name = StringField('Name', validators=[DataRequired(), Length(min=6, max=30)])
    email = EmailField('Email', validators=[DataRequired(), Email(), Length(min=6, max=40)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')  # Pulsante di invio

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Log in')

class EmailForm(FlaskForm):
    recipient_email = EmailField('Destinatario', validators=[DataRequired(), Email()])
    subject = StringField('Oggetto', validators=[DataRequired()])
    body = TextAreaField('Corpo del messaggio', validators=[DataRequired()])


load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase= create_client(url, key)
# Recupera tutti i dati dalla tabella "users"

@app.route("/", methods=['GET', 'POST'])
def index():
    if url and key:
        response = supabase.table("user").select("*").execute()
        data = response.data
        if data:
            name = data[0].get("name")
            email = data[0].get("email")
            psw = data[0].get("password")
        else:
            flash(f"La response è errata!", 'danger')
            
    else:
        flash(f"Key o Url errati ricontrolla i parametri!", 'danger')
    

    if current_user.is_authenticated:
        
        return render_template('index.html', psw=psw, name=name, email=email, current_page='index')
    else:
        return render_template('index.html', psw=None, name=None, email=None, current_page='index' )
        
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        # Controlla se l'email è già registrata
        response = supabase.table("user").select("email").eq("email", email).execute()
        if response.data:  # Se esiste almeno una riga con l'email
            flash("L'email è già registrata. Effettua il login.", 'danger')
            return redirect(url_for('login'))
        else:
            # Inserisci una nuova riga per l'utente
            try:
                response = supabase.table("user").insert({
                    "name": name,
                    "password": password,  # ATTENZIONE: Ricorda di hashare la password!
                    "email": email
                }).execute()

                # Mostra messaggio di successo
                flash(f"Registrazione avvenuta con successo! Benvenuto, {name}.", 'success')

                user = User(id=response.data[0]['id'], name=name, email=email)
                login_user(user)
                return redirect(url_for('dashboard'))

            except Exception as e:
                app.logger.error(f"Errore durante la registrazione: {e}")
                flash(f"Errore durante la registrazione: {str(e.message)}", 'danger')

    # Se l'utente è già autenticato, mostra il form con i dati attuali
    if current_user.is_authenticated:
        return render_template('register.html', form=form, name=current_user.name, email=current_user.email, current_page='register')
    else:
        # Mostra il form vuoto
        return render_template('register.html', form=form, name=None, email=None, current_page='register')


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))  # L'utente è già autenticato, redirigi
    
    if request.method == 'POST' and form.validate():
        email = form.email.data
        password = form.password.data
        
        response = supabase.table('user').select('*').eq('email', email).execute()
        user_data = response.data
        
        if user_data and user_data[0]['password'] == password:
            user = user_data[0]
            login_user(User(id=user['id'], name=user['name'], email=user['email']))
            flash('Login effettuato con successo!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email o password errati!', 'danger')
            
    if current_user.is_authenticated:
        return render_template('login.html', email=email, form=form, current_page='login')
    else:
        return render_template('login.html', email=None, form=form, current_page='login')


@app.route("/send-email", methods=['GET', 'POST'])
@login_required
def sender():
    feedback_message = None
    feedback_class = "danger"
    form = EmailForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        recipient_email = request.form.get("recipient_email")
        subject = request.form.get("subject")
        body = request.form.get("body")

        # Verifica se tutti i campi sono compilati
        if not recipient_email or not subject or not body:
            feedback_message = "Tutti i campi sono obbligatori."
            print(f"Feedback message: {feedback_message}")  # Stampa per debug        
    else:
            try:
                # Split dell'email in caso di più destinatari
                recipients = [email.strip() for email in recipient_email.split(",")]

                # Crea il messaggio
                msg = Message(subject=subject,
                              sender="nicolaguarise00@gmail.com",  # Specifica il mittente
                              recipients=recipients,
                              body=body)
                msg.html = body  # Usa il contenuto HTML della textarea

                # Invio dell'email
                mail.send(msg)

                # Feedback positivo
                feedback_message = "Email inviata con successo!"
                feedback_class = "success"
            except Exception as e:
                feedback_message = "Errore nell'invio dell'email"
                feedback_class = "info"
                print(f"Errore: {feedback_message}")

    if current_user.is_authenticated:
        return render_template('send-email.html', form=form, name=current_user.name, email=current_user.email, current_page='register', feedback_class=feedback_class, feedback_message=feedback_message)
    else:
        return render_template('send-email.html', form=None, name=None, email=None, current_page='register', feedback_class=feedback_class, feedback_message=feedback_message)


@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    # Controlla se il metodo della richiesta è POST
    if request.method == 'POST':
        new_email = request.form['email']
        new_name = request.form['name']
        new_password = request.form['password']

        # Esegui le verifiche necessarie (come la validazione dell'email)
        if not new_email or not new_name or not new_password:
            flash("Tutti i campi sono obbligatori.", "danger")
            return redirect(url_for('profile'))

        # Se non ci sono errori, aggiorna le credenziali dell'utente
        try:
            # Aggiorna l'email, nome e password nel "database" o struttura dati
            users[current_user.id]['email'] = new_email
            users[current_user.id]['name'] = new_name
            users[current_user.id]['password'] = new_password

            # Mostra un messaggio di successo
            flash("Credenziali aggiornate con successo!", "success")
            return redirect(url_for('profile'))

        except Exception as e:
            flash(f"Errore durante l'aggiornamento delle credenziali: {str(e)}", "danger")
            return redirect(url_for('profile'))

    if current_user.is_authenticated:
        return render_template('profile.html', email=current_user.email, name=current_user.name, current_page='profile')
    else:  
        return render_template('profile.html', email=None, name=None)

@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.is_authenticated:
        return render_template('dashboard.html', current_page='dashboard', name=current_user.name, email=current_user.email)
    else:
        return render_template('dashboard.html', password=None, name=None, email=None, current_page='dashboard')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Logout effettuato con successo!', 'success')
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Si è verificato un errore interno: {error}")
    return "Si è verificato un errore interno. I dettagli sono stati registrati.", 500

if __name__ == "__main__":
    app.run(debug=True)
