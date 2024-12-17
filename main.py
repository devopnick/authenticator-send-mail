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
        return render_template('index.html', name=name, email=current_user.id )
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

    return render_template('register.html', form=form, current_page='register')


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

    return render_template('login.html', form=form, current_page='login')

@app.route("/send-email", methods=["POST"])
@login_required
def send_email():
    recipient_email = request.form.get("recipient_email")
    subject = request.form.get("subject")
    body = request.form.get("body")

    if not recipient_email or not subject or not body:
        flash("Tutti i campi sono obbligatori.", "danger")
        return redirect(url_for("dashboard"))

    try:
        msg = Message(subject=subject,
                      sender=current_user.id,  # Usa l'email dell'utente loggato
                      recipients=[recipient_email],
                      body=body)
        msg.html = body  # Usa HTML nel corpo dell'email se disponibile
        mail.send(msg)
        flash("Email inviata con successo!", "success")
        return redirect(url_for("dashboard"))
    except Exception as e:
        flash(f"Errore nell'invio dell'email: {str(e)}", "danger")
        return redirect(url_for("dashboard"))

@app.route("/profile")
@login_required
def profile():
    return render_template('profile.html', email=current_user.email, current_page='profile')

@app.route("/dashboard")
@login_required
def dashboard():
    name = users.get(current_user.id, {}).get('name', 'utente')
    return render_template('dashboard.html', name=name, email=current_user.id, current_page='dashboard')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Logout effettuato con successo!', 'success')
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)