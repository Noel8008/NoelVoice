from flask import Flask, render_template, request, redirect, flash
import pymysql
from dynaconf import Dynaconf

app = Flask(__name__)

conf = Dynaconf(
    settings_file = ["settings.toml"]
)

app.secret_key = conf.secret_key

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

    return render_template("product.html.jinja", product = result)


@app.route("/sign_in")
def sign_in():
    
    return render_template("sign_in.html.jinja")


@app.route("/sign_up", methods=["POST", "GET"] )
def sign_up():
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
    