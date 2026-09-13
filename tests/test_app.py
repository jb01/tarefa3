"""Suíte de testes automatizados para a aplicação Flask e SQLite."""

import os
import tempfile
import pytest
from werkzeug.security import check_password_hash

from app import create_app
from db import get_db_connection, init_db


@pytest.fixture
def app():
    """Fixture que cria e configura uma instância de aplicação para testes com banco temporário."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    test_app = create_app(
        {
            "TESTING": True,
            "DATABASE": db_path,
            "SECRET_KEY": "test-secret-key",
        }
    )

    yield test_app

    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def client(app):
    """Fixture para o cliente de testes da aplicação."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Fixture para CLI runner se necessário."""
    return app.test_cli_runner()


class TestDatabaseAndBootstrap:
    """Testes de inicialização do banco de dados e bootstrap do administrador."""

    def test_database_initialization(self, app):
        """1. Testa se o banco e a tabela de usuários são criados com a estrutura esperada."""
        with app.app_context():
            conn = get_db_connection(app.config["DATABASE"])
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            table = cursor.fetchone()
            assert table is not None

            cursor.execute("PRAGMA table_info(users)")
            columns = {col[1]: col[2] for col in cursor.fetchall()}
            assert "id" in columns
            assert "username" in columns
            assert "password_hash" in columns
            assert "is_admin" in columns
            conn.close()

    def test_admin_auto_creation_and_hash_security(self, app):
        """2. Testa se o admin inicial é criado automaticamente com is_admin=1 e senha em hash (nunca texto puro)."""
        with app.app_context():
            conn = get_db_connection(app.config["DATABASE"])
            cursor = conn.cursor()
            cursor.execute("SELECT username, password_hash, is_admin FROM users WHERE username = 'admin'")
            admin = cursor.fetchone()
            conn.close()

            assert admin is not None
            assert admin["username"] == "admin"
            assert admin["is_admin"] == 1
            # A senha nunca deve ser 'admin' em texto puro
            assert admin["password_hash"] != "admin"
            # O hash deve ser verificável com a senha inicial 'admin'
            assert check_password_hash(admin["password_hash"], "admin")

    def test_admin_not_duplicated_or_overwritten_on_reinit(self, app):
        """3. Testa se reinicializações adicionais não duplicam nem alteram o admin existente."""
        db_path = app.config["DATABASE"]
        # Executa init_db novamente
        init_db(db_path)
        init_db(db_path)

        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE username = 'admin'")
        result = cursor.fetchone()
        conn.close()

        assert result["count"] == 1


class TestAuthenticationFlow:
    """Testes do fluxo de autenticação e interface de login."""

    def test_login_page_elements(self, client):
        """Testa se a página inicial de login contém os campos e os botões OK e Limpar."""
        response = client.get("/")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'name="username"' in html
        assert 'name="password"' in html
        assert 'OK' in html
        assert 'Limpar' in html
        assert 'id="btn-ok"' in html
        assert 'id="btn-limpar"' in html

    def test_admin_login_success_and_redirect(self, client):
        """4 e 9. Testa autenticação correta de admin/admin e redirecionamento para /register."""
        response = client.post(
            "/",
            data={"username": "admin", "password": "admin"},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.headers["Location"].endswith("/register")

        # Ao seguir o redirecionamento, acessa a tela de cadastro
        follow_response = client.get(response.headers["Location"])
        assert follow_response.status_code == 200
        assert "Cadastro de Usuários" in follow_response.get_data(as_text=True)

    def test_login_invalid_password_rejected(self, client):
        """5. Testa rejeição de senha incorreta para usuário existente."""
        response = client.post(
            "/",
            data={"username": "admin", "password": "senha_errada"},
            follow_redirects=True,
        )
        assert response.status_code == 401
        html = response.get_data(as_text=True)
        assert "Usuário ou senha inválidos." in html

    def test_login_nonexistent_user_rejected(self, client):
        """5. Testa rejeição de usuário inexistente."""
        response = client.post(
            "/",
            data={"username": "nao_existe", "password": "123"},
            follow_redirects=True,
        )
        assert response.status_code == 401
        html = response.get_data(as_text=True)
        assert "Usuário ou senha inválidos." in html

    def test_login_empty_fields_rejected(self, client):
        """Testa validação de ambos os campos vazios no login."""
        response = client.post(
            "/",
            data={"username": "", "password": ""},
            follow_redirects=True,
        )
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert "Informe usuário e senha." in html

    def test_login_empty_username_rejected(self, client):
        """Testa validação de campo de usuário vazio com senha preenchida."""
        response = client.post(
            "/",
            data={"username": "", "password": "admin"},
            follow_redirects=True,
        )
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert "Informe o usuário." in html

    def test_login_empty_password_rejected(self, client):
        """Testa validação de campo de senha vazia com usuário preenchido."""
        response = client.post(
            "/",
            data={"username": "admin", "password": ""},
            follow_redirects=True,
        )
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert "Informe a senha." in html

    def test_login_whitespace_username_rejected(self, client):
        """Testa validação de campo de usuário contendo apenas espaços em branco."""
        response = client.post(
            "/",
            data={"username": "   ", "password": "admin"},
            follow_redirects=True,
        )
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert "Informe o usuário." in html


class TestUserRegistrationAndPrivileges:
    """Testes de cadastro de usuários comuns pelo administrador e validações de regras de negócio."""

    def test_admin_can_register_common_user(self, client, app):
        """6 e 12. Testa cadastro de usuário comum pelo administrador e confirma is_admin=0 no banco."""
        # Login como admin
        client.post("/", data={"username": "admin", "password": "admin"})

        # Cadastra novo usuário
        response = client.post(
            "/register",
            data={"username": "usuario_valido", "password": "senha123"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert "Usuário cadastrado com sucesso." in response.get_data(as_text=True)

        # Valida no banco que o usuário foi criado com hash e is_admin = 0
        with app.app_context():
            conn = get_db_connection(app.config["DATABASE"])
            cursor = conn.cursor()
            cursor.execute("SELECT username, password_hash, is_admin FROM users WHERE username = 'usuario_valido'")
            user = cursor.fetchone()
            conn.close()

            assert user is not None
            assert user["username"] == "usuario_valido"
            assert user["is_admin"] == 0  # Obrigatório ser usuário comum
            assert user["password_hash"] != "senha123"
            assert check_password_hash(user["password_hash"], "senha123")

    def test_duplicate_username_registration_prevented(self, client):
        """7. Testa impedimento de cadastro de nome de usuário duplicado."""
        # Login como admin
        client.post("/", data={"username": "admin", "password": "admin"})

        # Cadastra usuário1
        client.post("/register", data={"username": "usuario_unico", "password": "123"})

        # Tenta cadastrar novamente com o mesmo username
        response = client.post(
            "/register",
            data={"username": "usuario_unico", "password": "456"},
            follow_redirects=True,
        )
        assert response.status_code == 409
        assert "Nome de usuário já cadastrado." in response.get_data(as_text=True)

    def test_register_duplicate_admin_username_prevented(self, client):
        """7. Testa tentativa de cadastrar usuário com nome 'admin' (já existente)."""
        client.post("/", data={"username": "admin", "password": "admin"})
        response = client.post(
            "/register",
            data={"username": "admin", "password": "outrasenha"},
            follow_redirects=True,
        )
        assert response.status_code == 409
        assert "Nome de usuário já cadastrado." in response.get_data(as_text=True)

    def test_register_empty_fields_prevented(self, client):
        """Testa validação de campos obrigatórios no cadastro."""
        client.post("/", data={"username": "admin", "password": "admin"})
        response = client.post(
            "/register",
            data={"username": "", "password": ""},
            follow_redirects=True,
        )
        assert response.status_code == 400
        assert "Preencha todos os campos." in response.get_data(as_text=True)

    def test_register_rejects_empty_or_whitespace_username(self, client, app):
        """Testa que o cadastro rejeita username vazio ou contendo apenas espaços."""
        # Autentica como admin
        client.post("/", data={"username": "admin", "password": "admin"})

        # Tenta cadastrar com username contendo apenas espaços
        response = client.post(
            "/register",
            data={"username": "   ", "password": "senha123"},
            follow_redirects=True,
        )
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert "Nome de usuário não pode ser vazio ou conter apenas espaços." in html

        # Confirma que nenhum usuário foi inserido no banco
        with app.app_context():
            conn = get_db_connection(app.config["DATABASE"])
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE trim(username) = ''")
            result = cursor.fetchone()
            conn.close()
            assert result["count"] == 0

    def test_register_rejects_username_with_digits(self, client, app):
        """Testa que o cadastro rejeita username contendo números."""
        # Autentica como admin
        client.post("/", data={"username": "admin", "password": "admin"})

        # Tenta cadastrar com username contendo dígitos
        response = client.post(
            "/register",
            data={"username": "usuario123", "password": "senhaValida"},
            follow_redirects=True,
        )
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert "Nome de usuário não pode conter números." in html

        # Confirma que o usuário com números não foi inserido no banco
        with app.app_context():
            conn = get_db_connection(app.config["DATABASE"])
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE username = 'usuario123'")
            result = cursor.fetchone()
            conn.close()
            assert result["count"] == 0


class TestCommonUserFlowAndAccessControl:
    """Testes do fluxo do usuário comum e restrições de controle de acesso."""

    def test_common_user_login_and_welcome_redirect(self, client):
        """8 e 10. Testa login de usuário comum e redirecionamento para /welcome."""
        # Primeiro, cadastra usuário comum via admin
        client.post("/", data={"username": "admin", "password": "admin"})
        client.post("/register", data={"username": "maria", "password": "segredo123"})
        client.get("/logout")

        # Login como usuário comum maria
        response = client.post(
            "/",
            data={"username": "maria", "password": "segredo123"},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.headers["Location"].endswith("/welcome")

        # Ao acessar /welcome, exibe mensagem de boas-vindas
        follow_response = client.get("/welcome")
        assert follow_response.status_code == 200
        html = follow_response.get_data(as_text=True)
        assert "Bem-vindo, maria!" in html
        # Não deve conter elementos administrativos ou de cadastro
        assert "Cadastro de Usuários" not in html
        assert 'name="username"' not in html

    def test_common_user_blocked_from_register_page(self, client):
        """11. Testa que usuário comum autenticado não pode acessar /register (retorna 403)."""
        # Cadastra usuário comum
        client.post("/", data={"username": "admin", "password": "admin"})
        client.post("/register", data={"username": "carlos", "password": "senha123"})
        client.get("/logout")

        # Login como usuário comum
        client.post("/", data={"username": "carlos", "password": "senha123"})

        # Tenta acessar /register diretamente via GET
        get_response = client.get("/register")
        assert get_response.status_code == 403

        # Tenta postar em /register diretamente via POST
        post_response = client.post(
            "/register",
            data={"username": "novo_user", "password": "123"},
        )
        assert post_response.status_code == 403

    def test_unauthenticated_user_blocked_from_protected_routes(self, client):
        """Testa que usuários não autenticados são redirecionados para a tela de login."""
        # Acesso direto a /register sem login
        resp_reg = client.get("/register")
        assert resp_reg.status_code == 302
        assert resp_reg.headers["Location"].endswith("/")

        # Acesso direto a /welcome sem login
        resp_wel = client.get("/welcome")
        assert resp_wel.status_code == 302
        assert resp_wel.headers["Location"].endswith("/")

    def test_logout_clears_session(self, client):
        """Testa o encerramento correto da sessão pelo logout."""
        # Login como admin
        client.post("/", data={"username": "admin", "password": "admin"})
        # Logout
        resp_logout = client.get("/logout", follow_redirects=False)
        assert resp_logout.status_code == 302
        assert resp_logout.headers["Location"].endswith("/")

        # Tentar acessar /register deve agora redirecionar para login
        resp_after = client.get("/register")
        assert resp_after.status_code == 302
        assert resp_after.headers["Location"].endswith("/")

