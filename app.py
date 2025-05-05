import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import json
from flask import Flask, render_template, request
from Gemini.main import run  # Gemini fonksiyonunu al


app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

#buradaki path geçici olarak oluşturuldu düzenlenmesi gerekiyor.
@app.route("/index", methods=["GET", "POST"])
def index():
    tarifler = []
    if request.method == "POST":
        #hangi div den veri geldiğine aşağıda köşeli parantez içinde verilen kısım belirliyor
        girilen = request.form["malzeme"]
        malzemeler = [m.strip().lower() for m in girilen.split(",")]

        # Gemini ile tarifleri al
        run(malzemeler)

        # outputs klasöründeki JSON'u oku
        out_path = "outputs/meals.json"
        if os.path.exists(out_path):
            with open(out_path, "r", encoding="utf-8") as f:
                tarifler = json.load(f)

    return render_template("index.html", tarifler=tarifler)
