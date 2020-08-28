from flask import Flask
from flask_wtf.csrf import CSRFProtect
import os

csrf = CSRFProtect()
app = Flask(__name__)
if __name__ == "__main__":
    app.run(debug=True)
csrf = CSRFProtect(app)
import routes