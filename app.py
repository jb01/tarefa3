"""Aplicação web Flask de autenticação e cadastro de usuários."""

import functools
import os
import sqlite3
from flask import (
    Flask,
    abort,
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


def create_app(test_config=None):
    """Factory para criação e configuração da aplicação Flask."""
    app = Flask(__name__, instance_relative_config=True)

    # Configurações padrão
    default_db_path = os.path.join(app.instance_path, "app.db")
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod"),
        DATABASE=default_db_path,
    )

    if test_config:
        app.config.update(test_config)

    # Inicializa o banco de dados e cria o admin inicial caso ainda não exista
    with app.app_context():
        init_db(app.config["DATABASE"])

    def get_db():
        """Retorna conexão com o banco associada ao contexto da requisição."""
        if "db" not in g:
            g.db = get_db_connection(app.config["DATABASE"])
        return g.db

    @app.teardown_appcontext
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

    @app.route("/", methods=["GET", "POST"])
    def login():
        """Página inicial com formulário de autenticação."""
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            if not username and not password:
                flash("Informe usuário e senha.", "error")
                return render_template("login.html"), 400
            elif not username:
                flash("Informe o usuário.", "error")
                return render_template("login.html"), 400
            elif not password:
                flash("Informe a senha.", "error")
                return render_template("login.html"), 400

            db = get_db()
            user = get_user_by_username(db, username)

            if user is None or not check_password_hash(user["password_hash"], password):
                flash("Usuário ou senha inválidos.", "error")
                return render_template("login.html"), 401

            # Autenticação bem-sucedida
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["is_admin"] = bool(user["is_admin"])

            # Redirecionamento baseado no perfil
            if session["is_admin"]:
                return redirect(url_for("register"))
            return redirect(url_for("welcome"))

        # GET: se já estiver autenticado, redireciona para a tela correspondente
        if "user_id" in session:
            if session.get("is_admin"):
                return redirect(url_for("register"))
            return redirect(url_for("welcome"))

        return render_template("login.html")

    @app.route("/register", methods=["GET", "POST"])
    @admin_required
    def register():
        """Página de cadastro de novos usuários comuns (exclusiva para administrador)."""
        if request.method == "POST":
            raw_username = request.form.get("username", "")
            username = raw_username.strip()
            password = request.form.get("password", "")

            if not raw_username and not password:
                flash("Preencha todos os campos.", "error")
                return render_template("register.html"), 400

            is_valid, error_msg = validate_username(raw_username)
            if not is_valid:
                flash(error_msg, "error")
                return render_template("register.html"), 400

            if not password:
                flash("Preencha todos os campos.", "error")
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

    @app.route("/welcome")
    @login_required
    def welcome():
        """Página de boas-vindas para usuários comuns autenticados."""
        return render_template("welcome.html")

    @app.route("/logout")
    def logout():
        """Encerra a sessão do usuário autenticado."""
        session.clear()
        return redirect(url_for("login"))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)

