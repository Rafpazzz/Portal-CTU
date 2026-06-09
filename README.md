# Portal CTU

Sistema web em Django para cadastro, consulta e avaliação de livros, com área administrativa para gerenciar livros, usuários e objetos de laboratório.

## Funcionalidades

- Listagem pública de livros na home.
- Busca de livros para usuários autenticados.
- Página de detalhes do livro.
- Cadastro, edição, visualização e remoção de avaliações.
- Cadastro e perfil de usuários.
- Painel administrativo interno para:
  - gerenciar livros;
  - gerenciar usuários;
  - gerenciar objetos de laboratório;
  - exportar dados de objetos de laboratório em CSV/PDF.

## Tecnologias

- Python 3.12
- Django 6.0.1
- PostgreSQL
- python-dotenv
- psycopg
- reportlab

## Estrutura

```text
Portal-CTU/
├── accounts/                 # Login, cadastro, perfil e telas administrativas
├── book/                     # Catálogo, busca e detalhes dos livros
├── laboratory/               # Gestão de objetos de laboratório
├── reviews/                  # Avaliações dos livros
├── setup/                    # Configurações globais do Django
├── templates/static/         # CSS e JavaScript estáticos
├── manage.py                 # Utilitário principal do Django
├── requirements.txt          # Dependências Python
└── .env.example              # Exemplo de configuração local
```

## Configuração Local

1. Crie ou atualize o ambiente virtual:

```bash
python3 -m venv venv
```

2. Ative o ambiente:

```bash
source venv/bin/activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com os dados do seu PostgreSQL:

```env

#Para rodar o banco localmente

DB_NAME=bd_name
DB_USER=seu_user
DB_PASSWORD=SUA_SENHA
DB_HOST=127.0.0.1
DB_PORT=sua_porta
```

Se o banco ainda não existir, crie-o no PostgreSQL antes de rodar as migrações.

5. Aplique as migrações:

```bash
python manage.py migrate
```

6. Inicie o servidor:

```bash
python manage.py runserver
```

Acesse:

```text
http://127.0.0.1:8000/
```

## Comandos Úteis

Rodar checagem do Django:

```bash
python manage.py check
```

Criar superusuário:

```bash
python manage.py createsuperuser
```

Criar novas migrações depois de alterar modelos:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Observações

- O projeto usa PostgreSQL configurado por variáveis no `.env`.
- O diretório `venv/` não deve ser versionado.
- Se a pasta do projeto for renomeada e scripts do `venv/bin` ficarem apontando para o caminho antigo, recrie ou atualize o ambiente virtual com:

```bash
python3 -m venv --upgrade venv
```
