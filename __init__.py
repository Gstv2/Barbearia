from flask import jsonify
from flask import Flask, render_template, flash, request, redirect, url_for, session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.inspection import inspect
from functools import wraps
from models.user import Base, User
from models.produtos import Base, Produtos
from urllib.parse import quote_plus
import os

# Resto do código sem importações circulares
app = Flask(__name__)
app.static_folder = 'static'

app.secret_key = os.urandom(24)
password = quote_plus("ted@010203")
engine = create_engine(f"mysql://user11:{password}@139.144.26.210:3306/db_equipe11")

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
db_session = Session()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/logout')
@login_required
def logout():
    session.pop('user_email', None)
    return redirect('/login')


@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/loja")
@login_required
def loja():
    try:
        produtos = db_session.query(Produtos).all()  # Query all products

        return render_template("loja.html", produtos=produtos)
    except Exception as e:
        # Lide com exceções, se necessário
        db_session.rollback()
        return "Erro: " + str(e)

# Rota para o login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        try:
            user = db_session.query(User).filter_by(email=email, senha=senha).first()
            if user:
                session['user_email'] = user.email
                db_session.commit()  # Commit a transação bem-sucedida
                return redirect('/loja')
            else:
                mensagem_erro = 'E-mail ou senha incorretos. Verifique suas credenciais.'
                return render_template('login.html', mensagem_erro=mensagem_erro)
        except Exception as e:
            db_session.rollback()  # Rollback em caso de erro
            mensagem_erro = 'Ocorreu um erro ao efetuar o login.'
            return render_template('login.html', mensagem_erro=mensagem_erro)

    return render_template("login.html")


# Rota para o registro de usuários
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        email = request.form['email']
        senha = request.form['senha']
        try:
            new_user = User(email=email, telefone=telefone, nome=nome, senha=senha)
            db_session.add(new_user)
            db_session.commit()
            session['user_email'] = new_user.email
            return redirect('/loja')
        except Exception as e:
            db_session.rollback()
            mensagem_erro = 'Usuário já existente.'
            return render_template('register.html', mensagem_erro=mensagem_erro)

    return render_template("register.html")


@app.route("/usuarios")
@login_required
def usuarios():
    user_email = session['user_email']
    user = db_session.query(User).filter_by(email=user_email).first()
    return render_template("usuarios.html", user=user)



# Função para remover uma produto
@app.route('/remove_product/<int:produto_id>', methods=['DELETE'])
@login_required
def remove_product(produto_id):
    try:
        produto = db_session.query(Produtos).filter_by(id=produto_id).first()
        if produto:
            db_session.delete(produto)
            db_session.commit()
            return jsonify({'message': 'produto removida com sucesso!'})
        else:
            return jsonify({'error': 'produto não encontrada.'}), 404
    except Exception as e:
        return jsonify({'error': 'Erro ao remover a produto.'}), 500

@app.route('/add_product', methods=['POST'])
@login_required
def add_product():
    data = request.get_json()
    if data:
        title = data.get('title')
        description = data.get('description')
        
        produto = Produtos(title=title, description=description)
        db_session.add(produto)
        db_session.commit()
        db_session.close()
        

        return jsonify({'success': True})
    
    return jsonify({'success': False})

# Defina uma rota para editar uma produto existente
@app.route('/edit_product/<int:cardId>', methods=['PUT'])
@login_required
  # Certifique-se de ter configurado a autenticação do Flask-Login
def edit_product(cardId):
    try:
        data = request.get_json()
        if data:
            newTitle = data.get('newTitle')
            newDescription = data.get('newDescription')

            # Encontre a produto com base no ID
            produto = db_session.query(Produtos).filter_by(id=cardId).first()
            
            if produto:
                # Atualize os dados da produto
                produto.title = newTitle
                produto.description = newDescription
                db_session.commit()
                db_session.close()

                return jsonify({'message': 'produto alterada com sucesso!'})
            else:
                return jsonify({'error': 'produto não encontrada.'}), 404
    except Exception as e:
        return jsonify({'error': 'Erro ao alterar a produto.'}), 500



#colocar site no ar
if __name__== "__main__":
  app.run(debug=True)
  
  
  
   #servidor do heroku
   