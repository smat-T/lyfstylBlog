from app import app
from flask import render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import MySQLdb.cursors, re, hashlib
from newsapi import NewsApiClient

app.secret_key = 'yourADS877uyuykey'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'mysqllocal'
app.config['MYSQL_PASSWORD'] = 'localoasswd'
app.config['MYSQL_DB'] = 'lifenewsblog'

# Intialize MySQL
mysql = MySQL(app)

newsapi = NewsApiClient(api_key='d524ab8c805e420cb9e1ad54db6d054d')


def get_sources_and_domains():
    all_sources = newsapi.get_sources()['sources']
    sources = []
    domains = []
    for e in all_sources:
        id = e['id']
        domain = e['url'].replace("http://", "")
        domain = domain.replace("https://", "")
        domain = domain.replace("www.", "")
        slash = domain.find('/')
        if slash != -1:
            domain = domain[:slash]
        sources.append(id)
        domains.append(domain)
    sources = ", ".join(sources)
    domains = ", ".join(domains)
    return sources, domains


@app.route('/',  methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        sources, domains = get_sources_and_domains()
        keyword = request.form["keyword"]
        related_news = newsapi.get_everything(q=keyword,
                                              sources=sources,
                                              domains=domains,
                                              language='en',
                                              sort_by='relevancy')
        no_of_articles = related_news['totalResults']
        if no_of_articles > 100:
            no_of_articles = 100
        all_articles = newsapi.get_everything(q=keyword,
                                              sources=sources,
                                              domains=domains,
                                              language='en',
                                              sort_by='relevancy',
                                              page_size=no_of_articles)['articles']
        return render_template("index.html", all_articles=all_articles,
                               keyword=keyword)
    else:
        top_headlines = newsapi.get_top_headlines(language="en")
        total_results = top_headlines['totalResults']
        if total_results > 100:
            total_results = 100
        all_headlines = newsapi.get_top_headlines(language="en",
                                                  page_size=total_results)['articles']
        return render_template("index.html", all_headlines=all_headlines)


@app.route('/news',  methods=['GET', 'POST'])
def news():
    if request.method == "POST":
        sources, domains = get_sources_and_domains()
        keyword = request.form["keyword"]
        related_news = newsapi.get_everything(q=keyword,
                                              sources=sources,
                                              domains=domains,
                                              language='en',
                                              sort_by='relevancy')
        no_of_articles = related_news['totalResults']
        if no_of_articles > 100:
            no_of_articles = 100
        all_articles = newsapi.get_everything(q=keyword,
                                              sources=sources,
                                              domains=domains,
                                              language='en',
                                              sort_by='relevancy',
                                              page_size=no_of_articles)['articles']
        return render_template("news.html", all_articles=all_articles,
                               keyword=keyword)
    else:
        top_headlines = newsapi.get_top_headlines(category="general", language="en")
        total_results = top_headlines['totalResults']
        if total_results > 100:
            total_results = 100
        all_headlines = newsapi.get_top_headlines(category="general", language="en",
                                                  page_size=total_results)['articles']
        return render_template("news.html", all_headlines=all_headlines)



@app.route('/login', methods=['GET', 'POST'])
def login():
    
    msg = ''
     # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Retrieve the hashed password
        hash = password + app.secret_key
        hash = hashlib.sha1(hash.encode())
        password = hash.hexdigest()
         # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return the result
        account = cursor.fetchone()

        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('dashboard'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)



@app.route('/register', methods=['GET', 'POST'])
def register():
     # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Hash the password
            hash = password + app.secret_key
            hash = hashlib.sha1(hash.encode())
            password = hash.hexdigest()
            # Account doesn't exist, and the form data is valid, so insert the new account into the accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


@app.route('/dashboard',  methods=['GET', 'POST'])
def dashboard():
     # Check if the user is logged in
    if 'loggedin' in session:

        if request.method == "POST":
            sources, domains = get_sources_and_domains()
            keyword = request.form["keyword"]
            related_news = newsapi.get_everything(q=keyword,
                                                sources=sources,
                                                domains=domains,
                                                language='en',
                                                sort_by='relevancy')
            no_of_articles = related_news['totalResults']
            if no_of_articles > 100:
                no_of_articles = 100
            all_articles = newsapi.get_everything(q=keyword,
                                                sources=sources,
                                                domains=domains,
                                                language='en',
                                                sort_by='relevancy',
                                                page_size=no_of_articles)['articles']
            return render_template("dashboard.html", all_articles=all_articles, username=session['username'], keyword=keyword)
        else:
            top_headlines = newsapi.get_top_headlines(language="en")
            total_results = top_headlines['totalResults']
            if total_results > 100:
                total_results = 100
            all_headlines = newsapi.get_top_headlines(language="en",
                                                    page_size=total_results)['articles']
            return render_template("dashboard.html", username=session['username'], all_headlines=all_headlines)
            
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


'''@app.route('/profile')
def profile():
     # Check if the user is logged in
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT name, username, password, email FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchall()
        cursor.close()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not logged in redirect to login page
    return redirect(url_for('login'))'''

@app.route('/profile')
def profile():
    # Check if the user is logged in
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT name, username, password, email FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchall()
        cursor.close()

        # Check if the account list is not empty before accessing the first element
        if account:
            account_info = account[0]

            # Show the profile page with account info
            return render_template('profile.html', account=account_info)
    # User is not logged in redirect to login page
    return redirect(url_for('login'))



@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('index'))