def recipe_prompt(ingredients: list[str]) -> str:
    ing_list = ", ".join(ingredients)
    return f"""
Verilen malzemeler: {ing_list}.

Lütfen üç bölüm halinde, açık ve yapılandırılmış şekilde çıktı ver:
1) Dört Kişilik 3 adet ana yemek (mümkünse yan yemeklerle birlikte) ve her tarif için gerekli malzeme miktarları.
2) Her yemeğin yapılış aşamaları ve püf noktaları.
3) Her yemeğin makro besin değerleri (karbonhidrat, protein, yağ), kalori miktarı ve sera gazı salınımı. CSV formatında da uygun.
(Makro besin değerlerini sadece sayı olarak belirt, birim, ekstra bilgi veya açıklama ekleme. Örnek: "karbonhidrat: 10g" yerine "10" yaz.)

Cevabı JSON objesi şeklinde ver:
```json
{{
  "meals": [
    {{
      "name": "...",
      "ingredients": [{{"item":"...","quantity":"..."}} , ...]
    }}, ...
  ],
  "instructions": [{{"meal":"...","steps":"..."}} , ...],
  "macros": [
    {{"name":"...","carbs_g":0,"protein_g":0,"fat_g":0,"calories_kcal":0,"GHG":0}},
  ],

}}
```"""
