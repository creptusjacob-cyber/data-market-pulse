import pandas as pd
import plotly.express as px

def generer_viz():
    try:
        # Charger les données enrichies (avec la nouvelle colonne Ville)
        df = pd.read_csv("jobs_ai_enriched.csv")
        
        # 📊 GRAPHIQUE 1 : Top 10 des Compétences
        all_skills = []
        for s in df['Skills_IA'].dropna():
            parts = [skill.strip().upper() for skill in str(s).split(",")]
            all_skills.extend(parts)
        counts = pd.Series(all_skills).value_counts().reset_index()
        counts.columns = ['Compétence', 'Nombre d\'offres']
        
        fig1 = px.bar(counts.head(10), x='Nombre d\'offres', y='Compétence', orientation='h', 
                     title='Top 10 des Technos Data Engineer (Mistral AI)',
                     color='Nombre d\'offres', color_continuous_scale='Viridis')
        fig1.update_layout(yaxis={'categoryorder':'total ascending'})

        # 📊 GRAPHIQUE 2 (LE NOUVEAU) : Top 5 des Villes qui recrutent
        city_counts = df['Ville'].value_counts().reset_index()
        city_counts.columns = ['Ville', 'Nombre d\'offres']
        
        fig2 = px.bar(city_counts.head(5), x='Nombre d\'offres', y='Ville', orientation='h', 
                     title='Top 5 des Hubs de recrutement Data Engineer',
                     color='Nombre d\'offres', color_continuous_scale='Magma_r')
        fig2.update_layout(yaxis={'categoryorder':'total ascending'})

        # Affichage
        fig1.show()
        fig2.show()
        
    except Exception as e:
        print(f"❌ Erreur lors de la viz : {e}")

if __name__ == "__main__":
    generer_viz()