import streamlit as st
from pymongo import MongoClient
import re
from config import MONGO_URI, DB_NAME, COLLECTION_NAME
from streamlit_phone_number_input import phone_number_input

# Configuration de la page
st.set_page_config(page_title="Collecte Tontine INF232", layout="centered")

# Connexion à MongoDB
@st.cache_resource # Pour ne pas se reconnecter à chaque clic
def get_db():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

db = get_db()
collection = db[COLLECTION_NAME]

st.title("🏦 Système de Tontine - Enrôlement")
st.caption("Développé par : KENNE FABREL - Matricule : 23V2570") # Ajoute cette ligne
st.markdown("Complétez le formulaire pour soumettre vos informations.")

# --- FORMULAIRE DE COLLECTE ---
with st.form("form_enrolement", clear_on_submit=True):
    nom = st.text_input("Nom Complet")
    tel_data = phone_number_input("Téléphone", default_country="CM")
    cni = st.text_input("Numéro de CNI")
    montant = st.number_input("Montant de la cotisation souhaitée", min_value=0, step=500)
    
    submitted = st.form_submit_button("Envoyer l'enrôlement")

    if submitted:
        # --- PHASE DE ROBUSTESSE AVANCÉE ---
        
        # 1. Validation du NOM (Lettres et espaces uniquement)
        # ^[a-zA-ZÀ-ÿ\s]+$ signifie : du début à la fin, seulement lettres (incluant accents) et espaces
        if not re.match(r"^[a-zA-ZÀ-ÿ\s]+$", nom):
            st.error("❌ Erreur : Le nom ne doit contenir que des lettres.")
            
        # 2. Validation du TÉLÉPHONE (Exactement 9 chiffres, pas de lettres)
        elif not num_complet:
            st.error("❌ Veuillez entrer un numéro de téléphone valide.")
        # 3. Validation de la CNI (Chiffres uniquement)
        elif not re.match(r"^\d+$", cni):
            st.error("❌ Erreur : Le numéro de CNI doit contenir uniquement des chiffres.")
            
        # 4. Validation du MONTANT (Déjà géré par st.number_input, mais on peut ajouter une sécurité)
        elif montant <= 0:
            st.error("❌ Erreur : Le montant doit être supérieur à zéro.")
            
        else:
            # --- VÉRIFICATION DANS LA BASE DE DONNÉES ---
            existe = collection.find_one({"tel": tel})
            if existe:
                st.warning("⚠️ Ce numéro de téléphone est déjà enregistré.")
            else:
                # Insertion si tout est correct
                nouveau_membre = {
                    "nom": nom.strip().title(), # Nettoie les espaces et met une majuscule
                    "tel": tel,
                    "cni": cni,
                    "montant": montant,
                    "statut": "En attente"
                }
                collection.insert_one(nouveau_membre)
                st.success(f"✅ Félicitations {nom}, votre dossier a été envoyé !")