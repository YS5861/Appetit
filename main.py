import sys
import os
import pandas as pd
import json
from flask import Flask, jsonify, render_template, request, flash
from gemini_execute import run
from pathlib import Path
from database_cnfg import Session, Yemek

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
            instructions = json.load(open("outputs/instructions.json", "r", encoding="utf-8"))
            macros = pd.read_csv("outputs/macros_clustered.csv")
            cluster_map = {0 : "Çok Yüksek GHG", 1: "Yüksek GHG", 2: "Ortalama GHG", 3: "Yüksek Karbonhidrat", 4: "Yüksek GHG Düşük Kalori"}


            formatted_tarifler = []
            for i, tarif in enumerate(tarifler):
                formatted_tarifler.append({
                    "id": i+1,  # Generate an ID
                    "ad": tarif.get("name", "Tarif Adı Yok"),
                    "tarif": ", ".join(
                        f'{ingredient.get("item", "Bilinmiyor")}: {ingredient.get("quantity", "Bilinmiyor")}'
                        for ingredient in tarif.get("ingredients", [])
                    ) if tarif.get("ingredients", []) else "Açıklama yok ing",
                    "instructions": "\n".join(instructions[i]["steps"]) if isinstance(instructions[i]["steps"], list) else instructions[i]["steps"],
                    "kalori": macros.iloc[i]["calories_kcal"],
                    "karbonhidrat": macros.iloc[i]["carbs_g"],
                    "protein": macros.iloc[i]["protein_g"],
                    "yag": macros.iloc[i]["fat_g"],
                    "GHG": macros.iloc[i]["GHG"],
                    "cluster": cluster_map.get(macros.iloc[i]["cluster"], "Bilinmiyor"),
                })
            
            # Hiç tarif dönmediyse
            if not tarifler:
                tarifler = [{"name": "Tarif bulunamadı", "ingredients": "Verilen malzemelerle tarif oluşturulamadı."}]
                
        except Exception as e:
            print(f"Hata oluştu: {str(e)}")
            flash(f"İşlem sırasında bir hata oluştu: {str(e)}", "error")
            tarifler = [{"name": "Hata", "ingredients": f"İşlem sırasında bir hata oluştu: {str(e)}"}]

    return render_template("index.html", tarifler=formatted_tarifler)

if __name__ == "__main__":
    app.run(debug=True)