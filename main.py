from flask import Flask, render_template, request, redirect, flash, abort
import flask_login
import pymysql
from dynaconf import Dynaconf


conf = Dynaconf(
    settings_file = ["settings.toml"]
)

app = Flask(__name__)
app.secret_key = conf.secret_key

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view=('/sign_in')


class User:
    is_authenticated = True
    is_anonymous = False
    is_active = True

    def __init__(self, user_id, username, email, first_name, last_name):
        self.id = user_id 
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

    def get_id(self):
        return str(self.id)


@login_manager.user_loader
def load_user(user_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM `Customer` WHERE `id` = {user_id}")
    
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result is not None:
        return User(result["id"], result["username"], result["email"], result["first_name"], result["last_name"])
    


def connect_db():
    conn = pymysql.connect(
        host = "10.100.34.80",
        database = "nsingh_noel_voice", 
        user = "nsingh",
        password = conf.password,
        autocommit = True,
        cursorclass = pymysql.cursors.DictCursor
    )

    return conn

@app.route("/")
def index():
    return render_template("homepage.html.jinja")


@app.route("/browse")
def product_browse(): 
    query = request.args.get('query')
    
    conn = connect_db()

    cursor = conn.cursor()

    if query is None:
        cursor.execute("SELECT * FROM `Product`;")
    else:
        cursor.execute(f"SELECT * FROM `Product` WHERE `name` LIKE '%{query}%' ;")
    
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("browse.html.jinja", products = results)


@app.route("/product/<product_id>")
def product_page(product_id):
   
    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM `Product` WHERE `id` = {product_id};")

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result is None:
        abort(404)

    return render_template("product.html.jinja", product = result)
    

@app.route("/product/<product_id>/cart", methods=["POST"])
@flask_login.login_required
def add_to_cart(product_id):
    qty=request.form["qty"]
    customer_id = flask_login.current_user.id

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(f"""
                            
                        INSERT INTO `Cart`
                            (`customer_id`, `product_id`, `qty`)
                        VALUES
                            ( '{customer_id}', '{product_id}', '{qty}');
                            """)
    


@app.route("/sign_in", methods=["POST", "GET"])
def sign_in():
    if flask_login.current_user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        email = request.form['email'].strip()
        password = request.form['password']

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM `Customer` WHERE `email` = '{email}';")

        result = cursor.fetchone()

        if result is None: 
            flash("Your information is inputted wrong..")
        elif password != result["password"]:
            flash("Your information is inputted wrong..")
        else:
            user = User(result["id"], result["username"], result["email"], result["first_name"], result["last_name"])
            
            flask_login.login_user(user)
            
            return redirect('/')

    return render_template("sign_in.html.jinja")


@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return redirect('/')


@app.route("/sign_up", methods=["POST", "GET"] )
def sign_up():
    if flask_login.current_user.is_authenticated:
        return redirect("/")
    else:
    
        if request.method == "POST":
                first_name = request.form["first_name"]
                last_name = request.form["last_name"]
                
                username = request.form["username"]
                email = request.form["email"]
                password = request.form["password"]
                confirm_pass = request.form["confirm_pass"]
                
                phone_num = request.form["phone_num"]
        
                conn = connect_db()

                cursor = conn.cursor()
                
                if password != confirm_pass:
                    flash("Passwords do not match.")
                    return render_template ("sign_up.html.jinja")
                
                if len(password) <= 11:
                    flash("Password isnt strong enough")
                    return render_template ("sign_up.html.jinja")

                try:
                    cursor.execute(f"""
                            
                        INSERT INTO `Customer`
                            (`first_name`, `last_name`, `username`, `email`, `password`, `phone_num`)
                        VALUES
                            ( '{first_name}', '{last_name}', '{username}', '{email}', '{password}', '{phone_num}'  );
                            """)
                except pymysql.err.IntegrityError:
                    flash("Sorry that information is already in use :(")
                
                else:
                    return redirect("/sign_in")

                finally:
                    cursor.close()
                    conn.close()
                    
                
    return render_template ("sign_up.html.jinja")


@app.route('/cart')
@flask_login.login_required
def cart():
    conn = connect_db()
    cursor = conn.cursor()

    customer_id = flask_login.current_user.id

    cursor.execute(f"""
                   SELECT `name`, `price`, `qty`, `image`, `product_id`, `Cart`.`id` 
                   FROM `Cart` 
                   JOIN `Product` ON `Product`.`id` = `product_id`
                   WHERE `customer_id` = {customer_id}
    """)

    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template ("cart.html.jinja", products=results)