def recipe_prompt(ingredients: list[str]) -> str:
    ing_list = ", ".join(ingredients)
    return f"""
Verilen malzemeler: {ing_list}.

Lütfen dört bölüm halinde, açık ve yapılandırılmış şekilde çıktı ver:
1) 3 adet ana yemek (mümkünse yan yemeklerle birlikte) ve her tarif için gerekli malzeme miktarları.
2) Her yemeğin yapılış aşamaları ve püf noktaları.
3) Her yemeğin makro besin değerleri (karbonhidrat, protein, yağ), kalori miktarı. CSV formatında da uygun.
4) Her tarif için tahmini karbon ayak izi (kg CO2e olarak).

Cevabı JSON objesi şeklinde ver:
```json
{{
  "meals": [
    {{
      "name": "...",
      "ingredients": [{{"item":"...","quantity":"..."}} , ...]
    }}, ...
  ],
  "instructions": ["...", "...", ...],
  "macros": [
    {{"name":"...","carbs_g":0,"protein_g":0,"fat_g":0}}
  ],
  "carbon_footprint": [
    {{"name":"...","co2e_kg":0.0}}
  ]
}}
```"""
