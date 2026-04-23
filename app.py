import streamlit as st
from pymongo import MongoClient
import re
from config import MONGO_URI, DB_NAME, COLLECTION_NAME

# Configuration de la page
st.set_page_config(page_title="Collecte Tontine INF232", layout="centered")

# Connexion à MongoDB
@st.cache_resource 
def get_db():
    # ROBUSTESSE : Timeout ajouté pour éviter le blocage DNS
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000, connectTimeoutMS=20000)
    return client[DB_NAME]

db = get_db()
collection = db[COLLECTION_NAME]

# --- SOLUTION PARTIE 1 : Initialisation de la mémoire des champs ---
if 'nom_val' not in st.session_state: st.session_state.nom_val = ""
if 'tel_val' not in st.session_state: st.session_state.tel_val = ""
if 'cni_val' not in st.session_state: st.session_state.cni_val = ""

# --- INTERFACE ---
st.title("🏦 Système de Tontine - Enrôlement")
st.caption("Développé par : KENNE FABREL - Matricule : 23V2570")
st.markdown("Complétez le formulaire pour soumettre vos informations.")

PAYS = {
    "🇨🇲 Cameroun (+237)": "+237",
    "🇬🇦 Gabon (+241)": "+241",
    "🇹🇩 Tchad (+235)": "+235",
    "🇨🇬 Congo (+242)": "+242",
    "🇨🇫 RCA (+236)": "+236",
    "🇫🇷 France (+33)": "+33"
}

# --- FORMULAIRE DE COLLECTE ---
# SOLUTION PARTIE 2 : On met clear_on_submit=False
with st.form("form_enrolement", clear_on_submit=False):
    st.subheader("Informations Personnelles")
    
    # On lie la valeur du champ à la session_state
    nom = st.text_input("Nom Complet", value=st.session_state.nom_val, placeholder="Ex: Jean Kuete")

    col1, col2 = st.columns([1, 2])
    with col1:
        prefixe_choisi = st.selectbox("Pays", list(PAYS.keys()))
    with col2:
        tel_local = st.text_input("Numéro de téléphone", value=st.session_state.tel_val, placeholder="6XXXXXXXX")
    
    cni = st.text_input("Numéro de CNI", value=st.session_state.cni_val, placeholder="Chiffres uniquement")
    montant = st.number_input("Montant de la cotisation souhaitée", min_value=0, step=500)
    
    submitted = st.form_submit_button("Envoyer l'enrôlement")

# --- LOGIQUE DE VALIDATION ---
if submitted:
    # On sauvegarde immédiatement les saisies dans la session
    st.session_state.nom_val = nom
    st.session_state.tel_val = tel_local
    st.session_state.cni_val = cni

    indicatif = PAYS[prefixe_choisi]
    num_complet = f"{indicatif}{tel_local}"

    # Validations...
    if not nom.strip():
        st.error("❌ Veuillez renseigner le champ 'Nom Complet'.")
    elif not tel_local.strip():
        st.error("❌ Veuillez renseigner le champ 'Numéro de téléphone'.")
    elif not cni.strip():
        st.error("❌ Veuillez renseigner le champ 'Numéro de CNI'.")
    elif not re.match(r"^[a-zA-ZÀ-ÿ\s]+$", nom):
        st.error("❌ Erreur : Le nom ne doit contenir que des lettres.")
    elif not tel_local.isdigit() or len(tel_local) < 8:
        st.error("❌ Erreur : Veuillez entrer un numéro de téléphone valide.")
    elif not cni.isdigit() or len(cni) < 5:
        st.error("❌ Erreur : Le numéro de CNI doit contenir uniquement des chiffres.")
    elif montant <= 0:
        st.error("❌ Erreur : Le montant doit être supérieur à zéro.")
    else:
        # --- VÉRIFICATION ET INSERTION ---
        try:
            existe = collection.find_one({"tel": num_complet})
            if existe:
                st.warning(f"⚠️ Le numéro {num_complet} est déjà enregistré.")
            else:
                nouveau_membre = {
                    "nom": nom.strip().title(),
                    "tel": num_complet,
                    "cni": cni,
                    "montant": montant,
                    "statut": "En attente"
                }
                collection.insert_one(nouveau_membre)
                
                # --- SOLUTION : ON CRÉE LE MESSAGE EN MÉMOIRE ICI ---
                st.session_state.envoi_reussi = f"✅ Enrôlement réussi pour {nom} !"
                
                # --- SI SUCCÈS : On vide la mémoire pour le prochain enrôlement ---
                st.session_state.nom_val = ""
                st.session_state.tel_val = ""
                st.session_state.cni_val = ""
                
                st.rerun() # On force le rafraîchissement pour afficher les champs vides
        except Exception as e:
                st.error(f"❌ Erreur technique : {e}")

# --- AFFICHAGE DU MESSAGE APRÈS LE RERUN ---
# (Indentation corrigée : ce bloc doit être tout à gauche, hors du 'if submitted:')
if "envoi_reussi" in st.session_state:
    st.success(st.session_state.envoi_reussi)
    # On supprime le message de la mémoire pour qu'il ne s'affiche qu'une seule fois
    del st.session_state.envoi_reussi