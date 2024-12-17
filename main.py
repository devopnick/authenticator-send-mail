from flask import Flask, render_template, request, flash, redirect,url_for
from wtforms import Form, StringField,PasswordField, validators
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configurazione Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'nicolaguarise00@gmail.com'  # Cambia con il tuo indirizzo email
app.config['MAIL_PASSWORD'] = 'zyrhvorphptgmqic'  # App password generata da Google
app.config['MAIL_DEFAULT_SENDER'] = 'nicolaguarise00@gmail.com'  # Mittente predefinito
mail = Mail(app)

# Configurazione di Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
emails = ["example1@gmail.com", "example2@gmail.com"]


# Simulazione di un database per utenti
users = {"nicolaheavy@gmail.com": {"password": "provalogin"}}

# Classe User per Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id

    @staticmethod
    def get(user_id):
        if user_id in users:
            return User(user_id)
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Form per la registrazione
class RegistrationForm(Form):
    name = StringField('Name', [validators.DataRequired(), validators.Length(min=6, max=30)])
    email = StringField('Email', [validators.Length(min=6, max=40), validators.Email(), validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=6)])

# Form per il login
class LoginForm(Form):
    email = StringField('Email', [validators.Email(), validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])

@app.route("/")
def index():
    if current_user.is_authenticated:
        name = users.get(current_user.id, {}).get('name', 'utente')
        return render_template('index.html', name=name, email=current_user.id, current_page='index')
    else:
        return render_template('index.html', name=None, email=None, current_page='index' )
        
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)

    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        if email in users:
            # Passa url_for('login') al template per il link
            flash(f"L'email è già registrata. Prova a fare il <a class='text-white font-bold text-sm' href='{url_for('login')}'>login</a>.", 'danger')
        else:
            users[email] = {"password": password, "name": name}
            flash(f"Registrazione avvenuta con successo! Benvenuto, "+name+".", 'success')

            user = User(email)
            login_user(user)
  
            return redirect(url_for('dashboard'))
    if current_user.is_authenticated:
        name = users.get(current_user.id, {}).get('name', 'utente')
        return render_template('register.html', form=form, name=name, email=current_user.id, current_page='register')
    else:
        return render_template('register.html', form=form, name=None, email=None, current_page='register')


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        email = form.email.data
        password = form.password.data

        if email in users and users[email]['password'] == password:
            user = User(email)
            login_user(user)  # Login dell'utente
            flash('Login effettuato con successo!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email o password errati. Riprova.', 'danger')
    if current_user.is_authenticated:
        name = users.get(current_user.id, {}).get('name', 'utente')
        return render_template('login.html', name=name, email=current_user.id, form=form, current_page='login')
    else:
        return render_template('login.html', name=None, email=None, form=form, current_page='login')

@app.route("/send-email", methods=['GET', 'POST'])
@login_required
def sender():
    feedback_message = None
    feedback_class = "text-red-500"

    if request.method == 'POST':
        recipient_email = request.form.get("recipient_email")
        subject = request.form.get("subject")
        body = request.form.get("body")

        # Verifica se tutti i campi sono compilati
        if not recipient_email or not subject or not body:
            feedback_message = "Tutti i campi sono obbligatori."
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
                feedback_class = "text-green-500"
            except Exception as e:
                # Feedback di errore
                feedback_message = f"Errore nell'invio: {str(e)}"
                print(f"Errore nell'invio dell'email: {str(e)}")  # Stampa errore nella console per il debug
    if current_user.is_authenticated:
        name = users.get(current_user.id, {}).get('name', 'utente')
        return render_template('send-email.html',name=name, email=current_user.id, feedback_class=feedback_class, feedback_message=feedback_message)
    else:
        return render_template('send-email.html',name=name, email=None, feedback_class=feedback_class, feedback_message=feedback_message)


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
        name = users.get(current_user.id, {}).get('name', 'utente')
        return render_template('profile.html', email=current_user.id, name=name)
    else:  
        return render_template('profile.html', email=None, name=None)

@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.is_authenticated:
        name = users.get(current_user.id, {}).get('name', 'utente')
        return render_template('dashboard.html', name=name, email=current_user.id, current_page='dashboard')
    else:
        return render_template('dashboard.html', name=None, email=None, current_page='dashboard')

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