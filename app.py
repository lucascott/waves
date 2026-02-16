from flask import Flask

from waves.blueprint import blueprint as waves_blueprint

app = Flask(__name__)
app.register_blueprint(waves_blueprint)


@app.route("/health")
def health():
    return "I'm healthy :)"
