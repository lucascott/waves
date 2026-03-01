import logging

from flask import Flask

from waves.blueprint import blueprint as waves_blueprint
from waves.caching import cache, get_cache_config

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
cache.init_app(app, config=get_cache_config())
app.register_blueprint(waves_blueprint)


@app.route("/health")
def health():
    return "I'm healthy :)"
