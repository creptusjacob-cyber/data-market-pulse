import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import json

# --- FONCTION IA (Ollama) ---
def extraire_infos_ia(titre, raw_entreprise):
    url_ollama = "http://localhost:11434/api/generate"
    # Nouveau prompt pour extraire skills ET ville
    prompt = f"""
    En tant qu'expert Data Engineer, analyse ce job :
    Titre: "{titre}"
    Entreprise/Lieu: "{raw_entreprise}"

    Réponds UNIQUEMENT par un objet JSON avec ces 2 clés :
    - "skills": Une liste de 3 technos max, séparées par virgules, en MAJUSCULES.
    - "ville": La ville du poste (ex: PARIS, LYON, REMOTE, FRANCE). Mets "FRANCE" si pas clair.

    Exemple de réponse: {{"skills": "PYTHON, SQL, AWS", "ville": "PARIS"}}
    """
    
    payload = {
        "model": "mistral",
        "prompt": prompt,
        "stream": False,
        "format": "json" # Force la réponse en JSON
    }
    
    try:
        response = requests.post(url_ollama, json=payload, timeout=15)
        result = json.loads(response.json().get("response", "{}"))
        return result.get("skills", "PYTHON, SQL").strip().upper(), result.get("ville", "FRANCE").strip().upper()
    except Exception as e:
        print(f"⚠️ Erreur IA: {e}")
        return "PYTHON, SQL", "FRANCE"

# --- PIPELINE PRINCIPAL ---
def run_full_pipeline(nb_pages=3): # On réduit à 3 pages pour le test
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
    all_data = []
    
    # 💡 LE CACHE : On mémorise ce qu'on a déjà analysé (Titre + Ville)
    cache_ia = {} 

    print(f"🚀 Lancement du scraping sur {nb_pages} pages...")

    for page in range(1, nb_pages + 1):
        url = f"https://www.hellowork.com/fr-fr/emploi/recherche.html?k=Data+Engineer&p={page}"
        print(f"📄 Page {page} en cours...")
        
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            job_elements = soup.find_all('h3')

            for el in job_elements:
                text = el.get_text(separator="|").strip()
                parts = text.split("|")
                
                if len(parts) >= 2:
                    poste = parts[0].strip()
                    raw_entreprise = parts[1].strip() # Contient l'entreprise + la ville
                    
                    # Logique de Cache : on crée une clé unique "Titre|RawLieu"
                    cache_key = f"{poste}|{raw_entreprise}"
                    if cache_key in cache_ia:
                        skills, ville = cache_ia[cache_key]
                    else:
                        print(f"  🤖 IA analyse : {poste[:30]}...")
                        skills, ville = extraire_infos_ia(poste, raw_entreprise)
                        cache_ia[cache_key] = (skills, ville)
                    
                    all_data.append({
                        "Poste": poste,
                        "Entreprise": parts[1].split("-")[0].strip() if "-" in parts[1] else parts[1].strip(),
                        "Ville": ville, # NOUVELLE COLONNE
                        "Skills_IA": skills,
                        "Date": datetime.now().strftime("%Y-%m-%d"),
                        "Source": "Hellowork"
                    })
            
            time.sleep(1)

        except Exception as e:
            print(f"❌ Erreur sur la page {page}: {e}")

    # Sauvegarde finale
    if all_data:
        df = pd.DataFrame(all_data)
        df.to_csv("jobs_ai_enriched.csv", index=False)
        print(f"\n✅ SUCCÈS ! {len(df)} offres traitées.")
        print(f"💡 Grâce au cache, l'IA n'a été sollicitée que {len(cache_ia)} fois.")
    else:
        print("❌ Aucune donnée récupérée.")

if __name__ == "__main__":
    run_full_pipeline(nb_pages=3) # On teste sur 3 pages d'abord