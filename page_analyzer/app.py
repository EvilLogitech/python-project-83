from flask import (Flask, redirect,
                   render_template,
                   request, flash,
                   get_flashed_messages,
                   url_for)


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')
