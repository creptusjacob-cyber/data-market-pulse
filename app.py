import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Config & Style
st.set_page_config(page_title="Data Market Pulse", layout="wide", initial_sidebar_state="expanded")

# Injection de CSS personnalisé pour le look "Dashboard Pro"
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { 
        background-color: #1e2130; 
        padding: 20px; 
        border-radius: 15px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        border: 1px solid #3e4259;
    }
    div[data-testid="stExpander"] { border: none !important; box-shadow: none !important; }
    .stButton>button { 
        width: 100%; 
        border-radius: 10px; 
        background-color: #4CAF50; 
        color: white;
        height: 3em;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Chargement des données
@st.cache_data
def load_data():
    if os.path.exists("jobs_ai_enriched.csv"):
        return pd.read_csv("jobs_ai_enriched.csv")
    return None

df = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=80)
    st.title("Control Panel")
    st.markdown("---")
    if st.button("🔄 Actualiser les données"):
        with st.spinner("Scraping & IA en cours..."):
            os.system("python scraper.py")
            st.cache_data.clear()
        st.rerun()
    
    st.markdown("### 🔍 Filtres")
    city_filter = st.multiselect("Filtrer par Ville", options=df['Ville'].unique() if df is not None else [])
    top_n = st.slider("Nombre de technos", 5, 20, 10)

# --- MAIN CONTENT ---
st.title("Observatoire Tech & Emploi")
st.caption("Analyse en temps réel via Mistral AI (Ollama) & BeautifulSoup")

if df is not None:
    # Application du filtre ville
    df_plot = df[df['Ville'].isin(city_filter)] if city_filter else df

    # 3. KPI Cards (Les chiffres clés)
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Offres Analysées", len(df_plot), delta=f"+{len(df_plot)} new")
    with m2:
        top_city = df_plot['Ville'].mode()[0] if not df_plot.empty else "N/A"
        st.metric("Top Hub", top_city)
    with m3:
        st.metric("Source", "Hellowork", "Online")

    st.markdown("---")

    # 4. Graphiques sur deux colonnes
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("🛠️ Top Compétences")
        all_skills = []
        for s in df_plot['Skills_IA'].dropna():
            all_skills.extend([x.strip().upper() for x in str(s).split(",")])
        
        if all_skills:
            counts = pd.Series(all_skills).value_counts().reset_index().head(top_n)
            counts.columns = ['Skill', 'Total']
            fig = px.bar(counts, x='Total', y='Skill', orientation='h', 
                         color='Total', color_continuous_scale='GnBu',
                         template="plotly_dark")
            fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("📍 Répartition Géo")
        cities = df_plot['Ville'].value_counts().reset_index().head(top_n)
        cities.columns = ['Ville', 'Offres']
        fig_city = px.pie(cities, values='Offres', names='Ville', 
                          hole=0.4, template="plotly_dark",
                          color_discrete_sequence=px.colors.sequential.RdPu_r)
        fig_city.update_layout(margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_city, use_container_width=True)

    # 5. Data Table (cachée par défaut pour ne pas charger la page)
    with st.expander("📄 Voir le détail des données brutes"):
        st.dataframe(df_plot[['Poste', 'Entreprise', 'Ville', 'Skills_IA']], use_container_width=True)

else:
    st.warning("⚠️ Aucune donnée trouvée. Lancez un scan depuis le panneau latéral.")