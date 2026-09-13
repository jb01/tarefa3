"""Aplicação web Flask de autenticação e cadastro de usuários."""

import functools
import os
import sqlite3
from flask import (
    Flask,
    abort,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from db import create_user, get_db_connection, get_user_by_username, init_db


def validate_username(username: str | None) -> tuple[bool, str | None]:
    """Valida se o username é válido (não vazio, não composto apenas por espaços e sem dígitos)."""
    if not username or not username.strip():
        return False, "Nome de usuário não pode ser vazio ou conter apenas espaços."
    if any(char.isdigit() for char in username):
        return False, "Nome de usuário não pode conter números."
    return True, None


def get_db():
    """Retorna conexão com o banco associada ao contexto da requisição atual."""
    if "db" not in g:
        g.db = get_db_connection(current_app.config["DATABASE"])
    return g.db


def close_db(exception=None):
    """Fecha a conexão com o banco ao finalizar a requisição."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def admin_required(view):
    """Decorador para proteger rotas que exigem perfil de administrador."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        if not session.get("is_admin"):
            abort(403)
        return view(**kwargs)

    return wrapped_view


def login_required(view):
    """Decorador para proteger rotas que exigem usuário autenticado."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(**kwargs)

    return wrapped_view


def validate_login_input(username: str, password: str) -> str | None:
    """Valida se os campos de login foram preenchidos corretamente."""
    if not username and not password:
        return "Informe usuário e senha."
    if not username:
        return "Informe o usuário."
    if not password:
        return "Informe a senha."
    return None


def redirect_by_role():
    """Direciona a sessão autenticada para a página correspondente ao perfil."""
    if session.get("is_admin"):
        return redirect(url_for("register"))
    return redirect(url_for("welcome"))


def authenticate_login():
    """Valida as credenciais recebidas e estabelece a sessão autenticada."""
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    error_message = validate_login_input(username, password)
    if error_message:
        flash(error_message, "error")
        return render_template("login.html"), 400

    db = get_db()
    user = get_user_by_username(db, username)

    if user is None or not check_password_hash(user["password_hash"], password):
        flash("Usuário ou senha inválidos.", "error")
        return render_template("login.html"), 401

    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["is_admin"] = bool(user["is_admin"])
    return redirect_by_role()


def login():
    """Exibe o formulário, processa o login ou redireciona a sessão existente."""
    if request.method == "POST":
        return authenticate_login()

    if "user_id" in session:
        return redirect_by_role()

    return render_template("login.html")


def validate_registration_input(raw_username: str, password: str) -> str | None:
    """Valida o cadastro preservando a prioridade das mensagens de erro."""
    if not raw_username and not password:
        return "Preencha todos os campos."
    is_valid, error_message = validate_username(raw_username)
    if not is_valid:
        return error_message
    if not password:
        return "Preencha todos os campos."
    return None


@admin_required
def register():
    """Página de cadastro de novos usuários comuns (exclusiva para administrador)."""
    if request.method == "POST":
        raw_username = request.form.get("username", "")
        username = raw_username.strip()
        password = request.form.get("password", "")

        error_message = validate_registration_input(raw_username, password)
        if error_message:
            flash(error_message, "error")
            return render_template("register.html"), 400

        db = get_db()
        password_hash = generate_password_hash(password)
        try:
            create_user(db, username, password_hash, is_admin=0)
            flash("Usuário cadastrado com sucesso.", "success")
            return redirect(url_for("register"))
        except sqlite3.IntegrityError:
            flash("Nome de usuário já cadastrado.", "error")
            return render_template("register.html"), 409

    return render_template("register.html")


@login_required
def welcome():
    """Página de boas-vindas para usuários comuns autenticados."""
    return render_template("welcome.html")


def logout():
    """Encerra a sessão do usuário autenticado."""
    session.clear()
    return redirect(url_for("login"))


def create_app(test_config=None):
    """Factory para criação e configuração da aplicação Flask."""
    app = Flask(__name__, instance_relative_config=True)

    default_db_path = os.path.join(app.instance_path, "app.db")
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod"),
        DATABASE=default_db_path,
    )

    if test_config:
        app.config.update(test_config)

    with app.app_context():
        init_db(app.config["DATABASE"])

    app.teardown_appcontext(close_db)

    # Registro de rotas HTTP
    app.add_url_rule("/", view_func=login, methods=["GET", "POST"])
    app.add_url_rule("/register", view_func=register, methods=["GET", "POST"])
    app.add_url_rule("/welcome", view_func=welcome, methods=["GET"])
    app.add_url_rule("/logout", view_func=logout, methods=["GET"])

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
