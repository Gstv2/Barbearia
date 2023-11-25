from flask import jsonify
from flask import Flask, render_template, flash, request, redirect, url_for, session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.inspection import inspect
from functools import wraps
from models.user import Base, User
from models.produtos import Base, Produtos
from models.servicos import Base, Servicos
from models.shopping_cart_items import Base, ShoppingCartItem
from urllib.parse import quote_plus
import smtplib
from email.message import EmailMessage
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
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/logout')
@login_required
def logout():
    session.pop('user_email', None)
    return redirect('/')


@app.route('/', methods=['GET', 'POST'])
def index():
    message = ''  # Variável para armazenar a mensagem a ser exibida na tela
    nome = ''  # Reinicialização da variável nome
    email = ''  # Reinicialização da variável email
    mensagem = ''  # Reinicialização da variável mensagem
    
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        mensagem = request.form['mensagem']

        # Aqui você pode adicionar a lógica para enviar o email
        # Substitua 'seu_email@gmail.com' pelo seu email real
        # Substitua 'sua_senha' pela senha do seu email real
        msg = EmailMessage()
        msg.set_content(f'Nome: {nome}\nEmail: {email}\nMensagem: {mensagem}')

        msg['Subject'] = 'Novo formulário submetido'
        msg['From'] = 'nerysilva2006@gmail.com'
        msg['To'] = 'nerysilva2006@gmail.com'  # Substitua pelo destinatário real

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login('nerysilva2006@gmail.com', 'epgqpcgsghewdifm')
                smtp.send_message(msg)
            message = 'Email enviado com sucesso!'
            nome = ''
            email = ''
            mensagem = ''
            return render_template('index.html', message=message)
        except smtplib.SMTPException as e:
            message = f'Ocorreu um erro ao enviar o email: {e}'
            return render_template('index.html', message=message)
        
    user_email = session.get('user_email', None)
    user = db_session.query(User).filter_by(email=user_email).first()
    return render_template('index.html',user=user)

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
    
# Rota para adicionar um produto ao carrinho
@app.route('/adicionar_produto', methods=['POST'])
@login_required
def adicionar_produto():
    data = request.get_json()
    produto_id = data['produto_id']
    quantidade = data['quantidade']

    # Supondo que você tenha um sistema de autenticação e o email do usuário esteja disponível
    user_email = session["user_email"] # Substitua pelo email do usuário autenticado

    # Verifique se o item já está no carrinho do usuário
    item_existente = ShoppingCartItem.query.filter_by(user_email=user_email, product_id=produto_id).first()

    if item_existente:
        # Se o item já estiver no carrinho, atualize a quantidade
        item_existente.quantity += quantidade
    else:
        
        # Caso contrário, crie um novo item no carrinho
        novo_item = ShoppingCartItem(product_id=produto_id, quantity=quantidade)
        db_session.add(novo_item)
        db_session.commit()


    return jsonify({'status': 'Produto adicionado ao carrinho com sucesso!'})

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
                db_session.close()
                return redirect('/')
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
            return redirect("/add_carrinho")
        except Exception as e:
            db_session.rollback()
            mensagem_erro = 'Usuário já existente.'
            return render_template('register.html', mensagem_erro=mensagem_erro)

    return render_template("register.html")



# Função para remover uma produto
@app.route('/add_carrinho')
@login_required
def add_carrinho():
    user_email = session["user_email"]

    new_car = ShoppingCartItem(user_email=user_email)
    db_session.add(new_car)
    db_session.commit()
    return redirect("/")
    
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
   