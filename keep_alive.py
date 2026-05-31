from flask import Flask
from threading import Thread

app = Flask("PrimeX")


@app.route("/")
def home():
    return "Prime X Assistant Running"


def run():
    app.run(
        host="0.0.0.0",
        port=10000
    )


def keep_alive():
    Thread(target=run).start()
