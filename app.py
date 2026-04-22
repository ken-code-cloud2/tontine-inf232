import streamlit as st
from pymongo import MongoClient
import re
from config import MONGO_URI, DB_NAME, COLLECTION_NAME

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
st.markdown("Complétez le formulaire pour soumettre vos informations.")

# --- FORMULAIRE DE COLLECTE ---
with st.form("form_enrolement", clear_on_submit=True):
    nom = st.text_input("Nom Complet")
    tel = st.text_input("Téléphone (9 chiffres)")
    cni = st.text_input("Numéro de CNI")
    montant = st.number_input("Montant de la cotisation souhaitée", min_value=1000, step=500)
    
    submitted = st.form_submit_button("Envoyer l'enrôlement")

    if submitted:
        # --- PHASE DE ROBUSTESSE (VALIDATION) ---
        if not nom or not tel or not cni:
            st.error("Veuillez remplir tous les champs obligatoires.")
        elif not re.match(r"^[62]\d{8}$", tel):
            st.error("Le numéro de téléphone doit être valide (9 chiffres).")
        else:
            # Vérifier si le membre existe déjà (Efficacité/Intégrité)
            existe = collection.find_one({"tel": tel})
            if existe:
                st.warning("Ce numéro de téléphone est déjà enregistré.")
            else:
                # Insertion dans MongoDB
                nouveau_membre = {
                    "nom": nom,
                    "tel": tel,
                    "cni": cni,
                    "montant": montant,
                    "statut": "En attente"
                }
                collection.insert_one(nouveau_membre)
                st.success(f"Félicitations {nom}, votre dossier a été envoyé !")
