import json
import re
import pandas as pd
from pathlib import Path
from gemini_client import ask_gemini
from prompt_templates import recipe_prompt
from clustering import cluster_data

def save_json(data: dict, path: Path):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

def save_macros_csv(macros: list[dict], path: Path):
    pd.DataFrame(macros).to_csv(path, index=False)

def save_footprint_csv(fp: list[dict], path: Path):
    pd.DataFrame(fp).to_csv(path, index=False)

def run(ingredients: list[str]):
    try:
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

        # Debug için ham text'i kaydet
        with open(out_dir / "raw_text.txt", "w", encoding="utf-8") as f:
            f.write(raw_text)

        # 5) Kod bloğu işaretlerini temizleyip JSON kısmını yakala
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if not match:
            raise ValueError("Gemini çıktısından JSON parse edilemedi:\n" + raw_text)
        
        json_text = match.group(0)

        #data = json.loads(match.group(0))
        
        # JSON'ı düzeltmeye çalış
        try:
            data = json.loads(json_text)
        except json.JSONDecodeError as e:
            print(f"JSON parse hatası: {str(e)}")
            print(f"Hatanın olduğu pozisyon: {e.pos}")
            error_context = json_text[max(0, e.pos-50):min(len(json_text), e.pos+50)]
            print(f"Hata bağlamı: '...{error_context}...'")
            
            # Basit JSON düzeltme çabası (özellikle virgül problemleri için)
            json_text = re.sub(r'(\w+)(\s+)"', r'\1",\2"', json_text)
            json_text = re.sub(r'(\d+)(\s+)"', r'\1",\2"', json_text)
            
            # Manuel bir default JSON yapısı oluştur
            """data = {
                "meals": [{"name": "Öneri bulunamadı", "description": "Gemini API'den gelen cevap işlenemedi."}],
                "instructions": [],
                "macros": [{"name": "N/A", "calories": 0, "protein": 0, "carbs": 0, "fat": 0}]
            }"""
            
            # Düzeltilmiş JSON'ı kaydet
            with open(out_dir / "fixed_json.txt", "w", encoding="utf-8") as f:
                f.write(json_text)

        # 6) Yapılandırılmış verileri ayıkla
        meals = data.get("meals", [])
        instructions = data.get("instructions", [])
        macros = data.get("macros", [])

        # meals ve instructions'ı kaydet
        save_json(meals, out_dir / "meals.json")
        save_json(instructions, out_dir / "instructions.json")

        # 7) Makro besin değerleri ve karbon ayak izi CSV'lerini oluştur
        save_macros_csv(macros, out_dir / "macros.csv")

        print("✅ Öneriler oluşturuldu. `outputs/` klasöründe raw, JSON ve CSV dosyalarını görebilirsin.")

        try:
            cluster_data()
        except Exception as cluster_error:
            print(f"⚠️ Kümeleme işlemi sırasında hata: {str(cluster_error)}")
            
        return meals
        
    except Exception as e:
        print(f"❌ İşlem sırasında hata oluştu: {str(e)}")
        # Hata durumunda boş bir tarif döndür
        default_recipe = [{"name": "Hata", "description": f"İşlem sırasında bir hata oluştu: {str(e)}"}]
        
        # Outputs klasörüne default değerleri yaz
        out_dir = Path("outputs")
        out_dir.mkdir(exist_ok=True)
        save_json(default_recipe, out_dir / "meals.json")
        
        return default_recipe


    

#if __name__ == "__main__":
    #malzemeler = ["patates", "havuç", "tavuk göğsü", "zeytinyağı"]
    #run(malzemeler)
