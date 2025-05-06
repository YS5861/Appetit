import sys
import os
import json
from flask import Flask, render_template, request, flash
from gemini_execute import run
from pathlib import Path

app = Flask(__name__)
app.config['SECRET_KEY'] = 'appetit-secret-key'  # Flash mesajları için gerekli

@app.route('/', methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/index", methods=["GET", "POST"])
def index_post():
    tarifler = []
    if request.method == "POST":
        try:
            girilen = request.form["malzeme"]
            malzemeler = [m.strip().lower() for m in girilen.split(",")]
            print("Girilen malzemeler:", malzemeler)
            
            # Gemini ile tarifleri al - bu işlev artık hata durumunda bile bir sonuç döndürecek
            tarifler = run(malzemeler)
            
            # Hiç tarif dönmediyse
            if not tarifler:
                tarifler = [{"name": "Tarif bulunamadı", "description": "Verilen malzemelerle tarif oluşturulamadı."}]
                
        except Exception as e:
            print(f"Hata oluştu: {str(e)}")
            flash(f"İşlem sırasında bir hata oluştu: {str(e)}", "error")
            tarifler = [{"name": "Hata", "description": f"İşlem sırasında bir hata oluştu: {str(e)}"}]

    return render_template("index.html", tarifler=tarifler)

if __name__ == "__main__":
    app.run(debug=True)