import json
import re
import pandas as pd
from pathlib import Path
from gemini_client import ask_gemini
from prompt_templates import recipe_prompt

def save_json(data: dict, path: Path):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

def save_macros_csv(macros: list[dict], path: Path):
    pd.DataFrame(macros).to_csv(path, index=False)

def save_footprint_csv(fp: list[dict], path: Path):
    pd.DataFrame(fp).to_csv(path, index=False)

def run(ingredients: list[str]):
    # 1) Prompt hazırla ve API çağrısı 
    prompt = recipe_prompt(ingredients)
    response = ask_gemini(prompt)

    # 2) outputs klasörünü oluştur
    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True)

    # 3) Ham cevabı kaydet
    save_json(response, out_dir / "recipes_raw.json")

    # 4) Gemini cevabından text bloğunu çıkar
    candidate = response["candidates"][0]
    content = candidate["content"]

    # Eğer content bir dict ise, içindeki parts listesindeki text'i al
    if isinstance(content, dict) and "parts" in content:
        raw_text = "".join(part.get("text", "") for part in content["parts"])
    else:
        raw_text = str(content)

    # 5) Kod bloğu işaretlerini temizleyip JSON kısmını yakala
    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if not match:
        raise ValueError("Gemini çıktısından JSON parse edilemedi:\n" + raw_text)
    data = json.loads(match.group(0))

    # 6) Yapılandırılmış verileri ayıkla
    meals        = data.get("meals", [])
    instructions = data.get("instructions", [])
    macros       = data.get("macros", [])
    footprint    = data.get("carbon_footprint", [])

    #meals ve instructions'ı kaydet
    save_json(meals, out_dir / "meals.json")
    save_json(instructions, out_dir / "instructions.json")

    # 7) Makro besin değerleri ve karbon ayak izi CSV'lerini oluştur
    save_macros_csv(macros, out_dir / "macros.csv")
    save_footprint_csv(footprint, out_dir / "footprint.csv")

    print("✅ Öneriler oluşturuldu. `outputs/` klasöründe raw, JSON ve CSV dosyalarını görebilirsin.")

#if __name__ == "__main__":
    #malzemeler = ["patates", "havuç", "tavuk göğsü", "zeytinyağı"]
    #run(malzemeler)
