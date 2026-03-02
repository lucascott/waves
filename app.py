import logging

from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics

from waves.blueprint import blueprint as waves_blueprint
from waves.caching import cache, get_cache_config

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
cache.init_app(app, config=get_cache_config())
PrometheusMetrics(
    app,
    excluded_paths=["/static/images/"],
    default_latency_as_histogram=False,
)
app.register_blueprint(waves_blueprint)


@app.route("/health")
def health():
    return "I'm healthy :)"
