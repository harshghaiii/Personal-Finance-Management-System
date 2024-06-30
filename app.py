from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, UserMixin, current_user

app = Flask(__name__)
db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config["SECRET_KEY"] = '6bfd3f8b53ee37a07794664e'
app.config["SESSION_PERMANENT"] = True
login_manager = LoginManager(app)
db.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    with app.app_context():
        return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)
    data = db.relationship('UserProfile', backref='owned_user', lazy=True)
    expense_tracker = db.relationship('Expense', backref='owned_user', lazy=True)
    portfolio = db.relationship('UserInvest', backref='owned_user', lazy=True)
    wallet = db.relationship('UserWallet', backref='owned_user', lazy=True)

    def __repr__(self):
        return f"User {self.username}"
    
class UserProfile(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    income = db.Column(db.Integer())
    budget = db.Column(db.Integer())
    invest_amount = db.Column(db.Integer())
    user = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    
class Expense(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    expense = db.Column(db.Integer(), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    user = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"User {self.category}"
    
class UserInvest(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    invest = db.Column(db.Integer(), nullable=False)
    stock = db.Column(db.Integer(), nullable=False)
    cash = db.Column(db.Integer(), nullable=False)
    fd = db.Column(db.Integer(), nullable=False)
    mf = db.Column(db.Integer(), nullable=False)
    bonds = db.Column(db.Integer(), nullable=False)
    user = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    
class UserWallet(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    amount = db.Column(db.Integer(), nullable=False)
    user = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)

def get_sum_of_expense(category, user):
    list_of_expense_by_category = Expense.query.filter_by(category=category).all()
    sum = 0
    for list_items in list_of_expense_by_category:
        if list_items.user == user:
            sum += list_items.expense

    return sum


@app.route('/', methods=['GET', 'POST'])
def login_page():
    
    if request.method == "POST":
        attempted_user = User.query.filter_by(username=request.form.get("username")).first()
        password = request.form.get('password')
        real_pass = attempted_user.password
         
        if attempted_user and password==real_pass:
            login_user(attempted_user)
            return redirect(url_for('home_page'))  
               
            
    return render_template('login_page.html')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
            
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login_page'))
    
    return render_template('register_page.html')

@app.route('/home')
def home_page():
    
    income = 0
    budget = 0
    invest_amount = 0
    
    if UserProfile.query.filter_by(user=current_user.username).first():
        if UserProfile.query.filter_by(user=current_user.username).first().income:
            object = UserProfile.query.filter_by(user=current_user.username).all()
            income = object[len(object)-1].income
            budget = object[len(object)-1].budget
            invest_amount = object[len(object)-1].invest_amount
        
    expense_object = Expense.query.filter_by(user=current_user.username).all()
    
    grocery_expense = 0
    clothes_expense = 0
    food_expense = 0
    others_expense = 0
        
    if expense_object:
        for e in expense_object:
            if int(e.category) == 1:
                grocery_expense = get_sum_of_expense(1, current_user.username)
            if int(e.category) == 2:
                clothes_expense = get_sum_of_expense(2, current_user.username)
            if int(e.category) == 3:
                food_expense = get_sum_of_expense(3, current_user.username)
            if int(e.category) == 4:
                others_expense = get_sum_of_expense(4, current_user.username)
                

    
    return render_template('home_page.html', income=income, expense=budget, investment=invest_amount, grocery_expense=grocery_expense, clothes_expense=clothes_expense, food_expense=food_expense, others_expense=others_expense)

@app.route('/expense', methods=["GET", "POST"])
def expense_tracker():
    
    grocery_expense = get_sum_of_expense(1, current_user.username)
    clothes_expense = get_sum_of_expense(2, current_user.username)
    food_expense = get_sum_of_expense(3, current_user.username)
    others_expense = get_sum_of_expense(4, current_user.username)
    
    expense_list = [grocery_expense, clothes_expense, food_expense, others_expense]
    sum_of_expense = grocery_expense + clothes_expense + food_expense + others_expense
    min_per = 40
    
    return render_template('expense_tracker.html', grocery_expense=grocery_expense, clothes_expense=clothes_expense, food_expense=food_expense, others_expense=others_expense, expense_list=expense_list, sum_of_expense=sum_of_expense, min_per=min_per)

@app.route('/add', methods=["GET", "POST"])
def add_expense():
    
    if request.method == "POST":
        expense = request.form.get("expense")
        category = request.form.get("category")
        
        expense_to_add = Expense(expense=expense, category=category, user=current_user.username)
        db.session.add(expense_to_add)
        db.session.commit()
        
        return redirect(url_for('expense_tracker'))
    
    return render_template('add_expense.html')   

@app.route('/finlit')
def financial_literacy(): 
    return render_template('fin_lit.html')

@app.route('/portfolio', methods=["GET", "POST"])
def portfolio_page():
    
    total_invest = 0
    mf = 0
    fd = 0
    stock = 0
    cash = 0
    bonds = 0
    
    if request.method == "POST":
        total_invest = request.form.get("total_invest")
        mf = request.form.get("mf")
        fd = request.form.get("fd")
        stock = request.form.get("stock")
        cash = request.form.get("cash")
        bonds = request.form.get("bonds")
        
        item_to_add = UserInvest(invest=total_invest, mf=mf, fd=fd, stock=stock, cash=cash, bonds=bonds, user=current_user.username)
        db.session.add(item_to_add)
        db.session.commit()
        
    list = UserInvest.query.filter_by(user=current_user.username).all()
    if len(list)!=0:
        mf = list[len(list)-1].mf
        fd = list[len(list)-1].fd
        stock = list[len(list)-1].stock
        bonds = list[len(list)-1].bonds
        cash = list[len(list)-1].cash

    return render_template('portfolio.html', total_invest=total_invest, mf=mf, fd=fd, stock=stock, cash=cash, bonds=bonds)

@app.route('/invest')
def invest_page():
    return render_template('invest.html')

@app.route('/profile', methods=["GET", "POST"])
def profile_page():
    
    if request.method == "POST":
        income = request.form.get("income")
        budget = request.form.get("budget")
        invest_amount = int(income) - int(budget)

        profile_to_add = UserProfile(income=income, budget=budget, invest_amount=invest_amount, user=current_user.username)
        db.session.add(profile_to_add)
        db.session.commit()
        
        return redirect(url_for('home_page'))
    
    return render_template('profile_page.html')

@app.route('/wallet', methods=['GET', 'POST'])
def wallet():
    
    if request.method == "POST":
        amount = request.form.get("amount")
        
        amount_to_add = UserWallet(amount=amount, user=current_user.username)
        db.session.add(amount_to_add)
        db.session.commit()
        
        return redirect(url_for('wallet_dashboard'))
    
    return render_template('wallet.html')

@app.route('/walletdash', methods=["GET", "POST"])
def wallet_dashboard():
    
    who_to_pay = ""
    if request.method == "POST":
        who_to_pay = request.form.get("who_to_pay")
        amount_to_pay = request.form.get("amount_to_pay")
        
        cur_user = UserWallet(amount=-(int(amount_to_pay)), user=current_user.username)
        db.session.add(cur_user)
        db.session.commit()
        
        user_to_add_money = UserWallet(amount=amount_to_pay, user=who_to_pay)
        db.session.add(user_to_add_money)
        db.session.commit()
    
    list_of_money = UserWallet.query.filter_by(user=current_user.username).all()
    list_of_user = User.query.all()
    sum=0
    for l in list_of_money:
        sum += l.amount
    
    return render_template('wallet_dashboard.html', sum=sum, list_of_user=list_of_user, who_to_pay=who_to_pay)

@app.route('/pay')
def pay_page():
    return render_template('pay_page.html')

if __name__== '__main__':
    app.run(debug=False, host='0.0.0.0')

