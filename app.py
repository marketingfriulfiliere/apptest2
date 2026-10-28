# -*- coding: utf-8 -*-
"""
FRIUL FILIERE LEAD ENGINE
Piattaforma di Lead Generation, Profilazione, Outreach Commerciale B2B
e Integrazione Ufficiale Registro Imprese / InfoCheck (Abbrevia X).

Unico file app.py - Streamlit
Avvio:
    streamlit run app.py
"""

import io
import json
import random
import re
from datetime import datetime, timedelta

import pandas as pd
import requests
import streamlit as st
from fpdf import FPDF


# =========================================================================
# CONFIGURAZIONE PAGINA
# =========================================================================

st.set_page_config(
    page_title="Friul Filiere Lead Engine",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================================
# TEMA / CSS
# =========================================================================

CUSTOM_CSS = """
<style>
:root {
    --blu-scuro: #0E1F3D;
    --rosso: #C8102E;
    --grigio-metal: #B0B7BD;
    --grigio-chiaro: #F2F3F5;
}

.stApp {
    background-color: #F5F6F8;
}

section[data-testid="stSidebar"] {
    background-color: var(--blu-scuro);
}
section[data-testid="stSidebar"] * {
    color: #EAECEF !important;
}
section[data-testid="stSidebar"] .stRadio label {
    font-size: 0.95rem;
}

h1, h2, h3 {
    color: var(--blu-scuro);
    font-weight: 800;
}

.ffe-header {
    background: linear-gradient(90deg, var(--blu-scuro) 0%, #16305e 100%);
    padding: 22px 30px;
    border-radius: 10px;
    border-left: 8px solid var(--rosso);
    margin-bottom: 22px;
}
.ffe-header h1 {
    color: white !important;
    margin: 0;
    font-size: 1.9rem;
}
.ffe-header p {
    color: var(--grigio-metal) !important;
    margin: 4px 0 0 0;
    font-size: 0.95rem;
}

.ffe-card {
    background: white;
    border-radius: 10px;
    padding: 18px 20px;
    border: 1px solid #E1E4E8;
    border-top: 4px solid var(--rosso);
    box-shadow: 0 2px 6px rgba(14,31,61,0.06);
    margin-bottom: 14px;
}

.ffe-metric {
    background: var(--blu-scuro);
    color: white;
    border-radius: 10px;
    padding: 16px 18px;
    text-align: center;
}
.ffe-metric .val {
    font-size: 2rem;
    font-weight: 800;
    color: white;
}
.ffe-metric .lbl {
    font-size: 0.8rem;
    color: var(--grigio-metal);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.ffe-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    margin-right: 4px;
}
.ffe-badge-alta { background: var(--rosso); color: white; }
.ffe-badge-media { background: #E8A33D; color: white; }
.ffe-badge-bassa { background: var(--grigio-metal); color: var(--blu-scuro); }
.ffe-badge-info { background: var(--blu-scuro); color: white; }
.ffe-badge-abbrevia { background: #0070BA; color: white; }

.ffe-divider {
    border: none;
    border-top: 2px solid #E1E4E8;
    margin: 18px 0;
}

.stButton>button {
    background-color: var(--rosso);
    color: white;
    border: none;
    border-radius: 6px;
    font-weight: 700;
    padding: 0.5em 1.2em;
}
.stButton>button:hover {
    background-color: #a10c22;
    color: white;
}

div[data-testid="stMetricValue"] {
    color: var(--blu-scuro);
    font-weight: 800;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# =========================================================================
# COSTANTI E MAPPATURE
# =========================================================================

SETTORI = [
    "Automotive", "Medicale", "Edilizia", "Packaging alimentare",
    "Arredamento", "Elettrodomestici", "Serramenti", "Agricoltura",
    "Cavi e condotte", "Water management", "Arredo urbano", "Nautica",
]

PAESI = [
    "Italia", "Germania", "Francia", "Spagna", "Polonia", "Turchia",
    "Romania", "Paesi Bassi", "Stati Uniti", "Messico", "Brasile",
    "India", "Cina", "Vietnam", "Regno Unito", "Austria",
]

DIMENSIONI_AZIENDA = [
    "Micro (< 10 dip.)", "Piccola (10-49 dip.)",
    "Media (50-249 dip.)", "Grande (250+ dip.)",
]

LIVELLI_URGENZA = ["Alta", "Media", "Bassa"]
STATI_LEAD = ["Nuovo", "Contattato", "In trattativa", "Qualificato", "Perso"]

FIERE_SETTORE = [
    "K Fair - Düsseldorf (DE)", "Plast - Milano (IT)",
    "Fakuma - Friedrichshafen (DE)", "NPE - Orlando (USA)",
    "Chinaplas - Shenzhen (CN)", "Interplastica - Mosca (RU)",
    "Plastpol - Kielce (PL)", "Feiplastic - San Paolo (BR)",
]

TECNOLOGIE_FRIUL_FILIERE = [
    "Linee di estrusione PVC per profili finestra",
    "Linee di coestrusione multistrato",
    "Sistemi di calibrazione e raffreddamento sottovuoto",
    "Linee di estrusione tubi corrugati e lisci",
    "Impianti per compositi legno-plastica (WPC)",
    "Linee monofilamento e reti estruse",
    "Sistemi downstream (taglio, impilamento, imballo automatico)",
    "Automazione e retrofit Industry 4.0 per linee di estrusione",
    "Teste e stampi per profili tecnici complessi",
]

MAPPA_TECNOLOGIA_SETTORE = {
    "Automotive": "Linee di coestrusione multistrato",
    "Medicale": "Linee monofilamento e reti estruse",
    "Edilizia": "Linee di estrusione PVC per profili finestra",
    "Packaging alimentare": "Sistemi downstream (taglio, impilamento, imballo automatico)",
    "Arredamento": "Impianti per compositi legno-plastica (WPC)",
    "Elettrodomestici": "Teste e stampi per profili tecnici complessi",
    "Serramenti": "Linee di estrusione PVC per profili finestra",
    "Agricoltura": "Linee di estrusione tubi corrugati e lisci",
    "Cavi e condotte": "Linee di estrusione tubi corrugati e lisci",
    "Water management": "Sistemi di calibrazione e raffreddamento sottovuoto",
    "Arredo urbano": "Impianti per compositi legno-plastica (WPC)",
    "Nautica": "Automazione e retrofit Industry 4.0 per linee di estrusione",
}

SETTORE_QUERY_PLACES = {
    "Automotive": "plastic injection molding automotive supplier",
    "Medicale": "medical plastic components manufacturer",
    "Edilizia": "PVC profile extrusion manufacturer",
    "Packaging alimentare": "plastic packaging manufacturer food",
    "Arredamento": "plastic furniture components manufacturer",
    "Elettrodomestici": "plastic components manufacturer appliances",
    "Serramenti": "PVC window profile manufacturer",
    "Agricoltura": "plastic pipe manufacturer irrigation",
    "Cavi e condotte": "plastic pipe extrusion manufacturer",
    "Water management": "HDPE pipe manufacturer water",
    "Arredo urbano": "wood plastic composite manufacturer",
    "Nautica": "plastic composite manufacturer marine",
}

# Query commerciali più mirate per trovare potenziali clienti Friul Filiere.
# Sono usate come discovery layer open-data: OpenStreetMap individua candidati,
# Abbrevia li verifica/anagrafizza quando disponibile.
PROFILI_FRIUL_FILIERE = {
    "Automotive": [
        "automotive plastic components manufacturer",
        "automotive extrusion plastic profiles",
        "automotive plastic profiles supplier",
    ],
    "Medicale": [
        "medical plastic components manufacturer",
        "medical tubing extrusion manufacturer",
        "medical plastic profiles supplier",
    ],
    "Edilizia": [
        "PVC profile extrusion manufacturer",
        "plastic building profiles manufacturer",
        "technical plastic profiles manufacturer",
    ],
    "Packaging alimentare": [
        "plastic packaging manufacturer food",
        "extruded plastic packaging manufacturer",
        "plastic film profile extrusion manufacturer",
    ],
    "Arredamento": [
        "furniture plastic components manufacturer",
        "plastic profiles furniture manufacturer",
        "technical profiles furniture manufacturer",
    ],
    "Elettrodomestici": [
        "appliance plastic components manufacturer",
        "plastic profiles appliances supplier",
        "technical plastic extrusion appliances",
    ],
    "Serramenti": [
        "PVC window profile manufacturer",
        "PVC door profiles manufacturer",
        "window extrusion profiles manufacturer",
    ],
    "Agricoltura": [
        "agricultural plastic pipe manufacturer",
        "irrigation pipe extrusion manufacturer",
        "agricultural plastic profiles manufacturer",
    ],
    "Cavi e condotte": [
        "cable conduit plastic manufacturer",
        "plastic pipe extrusion manufacturer",
        "technical plastic conduit manufacturer",
    ],
    "Water management": [
        "HDPE pipe manufacturer water",
        "plastic water pipe extrusion manufacturer",
        "irrigation pipe manufacturer",
    ],
    "Arredo urbano": [
        "WPC manufacturer outdoor furniture",
        "urban furniture plastic manufacturer",
        "wood plastic composite manufacturer",
    ],
    "Nautica": [
        "marine plastic components manufacturer",
        "plastic extrusion marine supplier",
        "composite profiles marine manufacturer",
    ],
}

PREFISSI_AZIENDA = ["Euro", "Plast", "Poly", "Nord", "Tecno", "Global", "Alpha", "Master"]
SUFFISSI_AZIENDA = ["Plastics", "Profili", "Extrusion", "Kunststoff", "S.r.l.", "S.p.A."]
NOMI_CONTATTO = ["Marco Bianchi", "Julia Weber", "Pierre Dubois", "Elena Rossi", "John Smith"]
FONTI_NOTIZIA = ["Ampliamento stabilimento", "Nuova linea produttiva", "Aumento organico"]


# =========================================================================
# STATO DI SESSIONE
# =========================================================================

def init_session_state():
    if "leads" not in st.session_state:
        st.session_state.leads = []
    if "next_id" not in st.session_state:
        st.session_state.next_id = 1
    if "gemini_api_key" not in st.session_state:
        st.session_state.gemini_api_key = ""
    if "dossier_cache" not in st.session_state:
        st.session_state.dossier_cache = {}
    if "email_cache" not in st.session_state:
        st.session_state.email_cache = {}
    if "lotto_corrente" not in st.session_state:
        st.session_state.lotto_corrente = 1
    if "pagina" not in st.session_state:
        st.session_state.pagina = "Dashboard"

    # Configurazione e stato Abbrevia X.
    # Le credenziali operative sono definite direttamente nell'app.py.
    if "abbrevia_env" not in st.session_state:
        st.session_state.abbrevia_env = "production"
    if "abbrevia_username" not in st.session_state:
        st.session_state.abbrevia_username = ""
    if "abbrevia_password" not in st.session_state:
        st.session_state.abbrevia_password = ""
    if "abbrevia_scope" not in st.session_state:
        st.session_state.abbrevia_scope = ""
    if "abbrevia_token" not in st.session_state:
        st.session_state.abbrevia_token = ""
    if "abbrevia_token_expires_at" not in st.session_state:
        st.session_state.abbrevia_token_expires_at = datetime.min
    if "infocheck_cache" not in st.session_state:
        st.session_state.infocheck_cache = {}
    if "lead_search_results" not in st.session_state:
        st.session_state.lead_search_results = []
    if "last_search_config" not in st.session_state:
        st.session_state.last_search_config = {}


init_session_state()


# =========================================================================
# CREDENZIALI ABBREVIA X — CONFIGURATE DIRETTAMENTE NEL CODICE
# =========================================================================
# Non servono Streamlit Secrets per Abbrevia.
# NOTA: queste credenziali sono state riportate dal codice originale fornito
# per il progetto. Se sono state esposte, è consigliabile farle ruotare da Abbrevia.
ABBREVIA_USERNAME = "e7875aee-98d6-4dec-ae2a-0bd1d6485150"
ABBREVIA_PASSWORD = "YmW8Q~xkPM6fBQViiN6ZT0SwvImSUnNp_F6wEb58"
ABBREVIA_SCOPE = "api://api-internal.abbrevia.it/31b5b2be-eed3-4285-8ee8-497bc4e13f96"
ABBREVIA_BASE_URL = "https://api.abbrevia.it"

# =========================================================================
# CONFIGURAZIONE AI OPZIONALE
# =========================================================================
GEMINI_API_KEY = ""
GEMINI_MODEL = "gemini-1.5-flash"


def abbrevia_get_token():
    """Recupera o rinnova il JWT token per Abbrevia X."""
    if not all([ABBREVIA_USERNAME.strip(), ABBREVIA_PASSWORD.strip(), ABBREVIA_SCOPE.strip()]):
        return None, "Credenziali Abbrevia non configurate nel codice."

    now = datetime.now()
    if st.session_state.abbrevia_token and now < st.session_state.abbrevia_token_expires_at:
        return st.session_state.abbrevia_token, None

    url = f"{ABBREVIA_BASE_URL}/auth/token"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Environment": st.session_state.abbrevia_env,
    }
    payload = {
        "grant_type": "client_credentials",
        "username": ABBREVIA_USERNAME.strip(),
        "password": ABBREVIA_PASSWORD.strip(),
        "scope": ABBREVIA_SCOPE.strip(),
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        if resp.status_code != 200:
            return None, f"Errore Auth ({resp.status_code}): {resp.text}"
        data = resp.json().get("data", {})
        token = data.get("access_token")
        expires_in = int(data.get("expires_in", 3600))
        if not token:
            return None, "Token non presente nella risposta del server"

        st.session_state.abbrevia_token = token
        st.session_state.abbrevia_token_expires_at = now + timedelta(seconds=expires_in - 60)
        return token, None
    except Exception as exc:
        return None, f"Errore connessione ad Abbrevia: {exc}"


def abbrevia_search_company(ragione_sociale="", piva="", cf="", provincia="", rea=""):
    """Cerca aziende nel Registro Imprese ufficiale tramite Abbrevia X."""
    token, err = abbrevia_get_token()
    if err:
        return [], err

    url = f"{ABBREVIA_BASE_URL}/abbx/search-company-basic"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Environment": st.session_state.abbrevia_env,
        "Authorization": f"Bearer {token}",
    }

    body = {
        "page": {"pageNumber": 0, "pageSize": 25}
    }
    if piva.strip():
        body["partitaIVA"] = piva.strip()
    if cf.strip():
        body["codiceFiscale"] = cf.strip()
    if ragione_sociale.strip():
        body["ragioneSociale"] = ragione_sociale.strip()
    if provincia.strip() and rea.strip():
        body["provinciaCCIAA"] = provincia.strip().upper()
        body["numeroREA"] = rea.strip()

    try:
        resp = requests.post(url, json=body, headers=headers, timeout=20)
        if resp.status_code == 404:
            return [], "Nessuna azienda trovata con i parametri forniti."
        if resp.status_code != 200:
            return [], f"Errore {resp.status_code}: {resp.text}"

        risposta = resp.json()
        dati = risposta.get("data", {})
        content = dati.get("content", [])
        return content, None
    except Exception as exc:
        return [], f"Errore di rete durante la ricerca: {exc}"


def abbrevia_get_infocheck(piva_or_cf):
    """Richiede la scheda InfoCheck completa (bilanci, esponenti, dati occupazionali)."""
    piva_or_cf = piva_or_cf.strip()
    if piva_or_cf in st.session_state.infocheck_cache:
        return st.session_state.infocheck_cache[piva_or_cf], None

    token, err = abbrevia_get_token()
    if err:
        return None, err

    url = f"{ABBREVIA_BASE_URL}/abbx/info-check"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Environment": st.session_state.abbrevia_env,
        "Authorization": f"Bearer {token}",
    }

    # Accetta partitaIva o codiceFiscale
    body = {"partitaIva": piva_or_cf} if len(piva_or_cf) == 11 and piva_or_cf.isdigit() else {"codiceFiscale": piva_or_cf}

    try:
        resp = requests.post(url, json=body, headers=headers, timeout=30)
        if resp.status_code == 404:
            return None, "Scheda InfoCheck non trovata per questo identificativo."
        if resp.status_code == 402:
            return None, "Credito Abbrevia X insufficiente (402 Payment Required)."
        if resp.status_code != 200:
            return None, f"Errore InfoCheck ({resp.status_code}): {resp.text}"

        dati = resp.json().get("data", {})
        st.session_state.infocheck_cache[piva_or_cf] = dati
        return dati, None
    except Exception as exc:
        return None, f"Errore chiamata InfoCheck: {exc}"


# =========================================================================
# GEMINI REST API
# =========================================================================

def call_gemini_api(prompt, temperature=0.7, max_tokens=1500):
    api_key = st.session_state.gemini_api_key.strip()
    if not api_key:
        return None, "no_key"

    gemini_model = st.secrets.get("GEMINI_MODEL", "gemini-1.5-flash") if hasattr(st, "secrets") else "gemini-1.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
    }
    try:
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        return text, "ok"
    except Exception as exc:
        return None, f"errore: {exc}"


# =========================================================================
# DISCOVERY OPEN DATA — OPENSTREETMAP / OVERPASS
# =========================================================================

OSM_USER_AGENT = "FriulFiliereLeadEngine/1.0 (commercial discovery)"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]


def _regex_osm(text):
    return re.sub(r"[^a-zA-Z0-9À-ÿ\s_-]", " ", str(text or "")).strip()


def osm_geocode(area, paese):
    query = ", ".join(x for x in [area.strip(), paese.strip()] if x)
    if not query:
        return None, "Inserisci almeno un Paese o un'area geografica."
    try:
        r = requests.get(
            NOMINATIM_URL,
            params={"q": query, "format": "jsonv2", "limit": 1},
            headers={"User-Agent": OSM_USER_AGENT},
            timeout=15,
        )
        r.raise_for_status()
        rows = r.json()
        if not rows:
            return None, f"Area non trovata: {query}"
        bb = rows[0].get("boundingbox", [])
        if len(bb) != 4:
            return None, "Nessun bounding box disponibile per l'area selezionata."
        south, north, west, east = map(float, bb)
        if abs(north - south) > 8 or abs(east - west) > 10:
            return None, "Area troppo ampia: specifica una regione, provincia o città."
        return (south, west, north, east), None
    except Exception as exc:
        return None, f"Errore geocodifica: {exc}"


def _bbox_cells(south, west, north, east):
    """Divide aree regionali ampie in celle per evitare timeout Overpass."""
    mid_lat = (south + north) / 2
    mid_lon = (west + east) / 2
    return [
        (south, west, mid_lat, mid_lon),
        (south, mid_lon, mid_lat, east),
        (mid_lat, west, north, mid_lon),
        (mid_lat, mid_lon, north, east),
    ]


def _overpass_request(query, endpoint):
    try:
        r = requests.post(
            endpoint,
            data=query,
            headers={"User-Agent": OSM_USER_AGENT},
            timeout=(8, 28),
        )
        r.raise_for_status()
        return r.json().get("elements", []), None
    except requests.exceptions.Timeout:
        return [], "timeout"
    except Exception as exc:
        return [], str(exc)


def osm_discovery(query_text, settore, profilo, area, paese, max_results=30):
    """Discovery gratuita OSM robusta: celle geografiche + endpoint Overpass di fallback."""
    bbox, err = osm_geocode(area, paese)
    if err:
        return [], err

    south, west, north, east = bbox
    cells = _bbox_cells(south, west, north, east)

    # Query volutamente più leggere della precedente: evita una singola regex
    # enorme su tutta la Lombardia, che può mandare in timeout Overpass.
    terms = [
        query_text, profilo, settore,
        "plastic", "plastics", "extrusion", "profile", "pipe", "pipes",
        "tube", "tubing", "polymer", "manufacturer", "medical",
        "medical device", "suction", "aspiration", "industrial",
    ]
    clean_terms = [_regex_osm(x) for x in terms if _regex_osm(x)]
    regex = "|".join(x.replace(" ", ".*") for x in clean_terms)[:1000]

    all_elements = []
    errors = []
    successful_requests = 0

    for endpoint in OVERPASS_URLS:
        endpoint_elements = []
        endpoint_ok = False
        for south_c, west_c, north_c, east_c in cells:
            bbox_s = f"{south_c},{west_c},{north_c},{east_c}"
            q = f'''[out:json][timeout:20];
(
  nwr["name"~"{regex}",i]({bbox_s});
  nwr["description"~"{regex}",i]({bbox_s});
  nwr["craft"~"plastic|metal|manufacturer|industrial",i]({bbox_s});
  nwr["industrial"~"factory|manufacture|industrial",i]({bbox_s});
  nwr["shop"~"medical_supply|industrial",i]({bbox_s});
);
out center tags;'''
            elements, req_err = _overpass_request(q, endpoint)
            if req_err:
                errors.append(f"{endpoint}: {req_err}")
                continue
            endpoint_ok = True
            successful_requests += 1
            endpoint_elements.extend(elements)
            if len(endpoint_elements) >= max_results * 4:
                break

        if endpoint_ok:
            all_elements.extend(endpoint_elements)
            if len(all_elements) >= max_results or successful_requests >= 2:
                break

    if not all_elements:
        detail = " | ".join(errors[-3:]) if errors else "nessuna risposta valida"
        return [], (
            "OpenStreetMap/Overpass non ha risposto in tempo. "
            "Ho provato più endpoint e aree ridotte. "
            f"Dettaglio: {detail}"
        )

    out, seen = [], set()
    for el in all_elements:
        tags = el.get("tags", {}) or {}
        name = tags.get("name") or tags.get("operator")
        if not name:
            continue
        key = normalizza_testo(name)
        if key in seen:
            continue
        seen.add(key)

        center = el.get("center", {}) or {}
        lat = el.get("lat", center.get("lat"))
        lon = el.get("lon", center.get("lon"))
        address = ", ".join(
            x for x in [
                tags.get("addr:street"), tags.get("addr:housenumber"),
                tags.get("addr:postcode"), tags.get("addr:city"),
            ] if x
        )
        text_blob = " ".join(str(tags.get(k, "")) for k in ["name", "description", "operator", "craft", "industrial", "product", "man_made"])
        out.append({
            "name": name,
            "lat": lat,
            "lon": lon,
            "address": address,
            "website": tags.get("website") or tags.get("contact:website") or "",
            "phone": tags.get("phone") or tags.get("contact:phone") or "",
            "tags": tags,
            "text_blob": text_blob,
        })

    needle_tokens = set(_token_set(" ".join([query_text, profilo, settore])))
    for row in out:
        row_tokens = set(_token_set(row.get("text_blob", "")))
        row["_match"] = len(needle_tokens & row_tokens)
    out.sort(key=lambda x: (x.get("_match", 0), bool(x.get("website"))), reverse=True)
    return out[:max_results], None


def normalizza_testo(value):
    return " ".join(str(value or "").lower().replace("-", " ").split())


def _token_set(value):
    return {p for p in re.findall(r"[a-zàèéìòù0-9]+", normalizza_testo(value)) if len(p) >= 4}


def calcola_fit_lead(nome, descrizione, settore, profilo, query_text, area="", sito=""):
    """Calcola un punteggio di discovery senza inventare dati aziendali."""
    blob = normalizza_testo(" ".join([nome, descrizione, settore, profilo, query_text, area, sito]))
    target = _token_set(profilo or settore)
    hits = sum(1 for token in target if token in blob)
    score = 35 + min(30, hits * 5)
    for term in (
        "manufacturer", "manufacturing", "producer", "extrusion", "profiles", "profile",
        "plastic", "plastics", "polymer", "pipe", "pipes", "tube", "tubing",
        "components", "component", "supplier", "medical", "medical device",
        "suction", "aspiration", "estrusione", "profil", "plastica", "produttore",
        "componenti", "medicale", "tubo", "tubi"
    ):
        if term in blob:
            score += 2
    if sito and sito not in ("Non disponibile", "Da verificare"):
        score += 4
    if area and normalizza_testo(area) in blob:
        score += 4
    return min(84, score)


def aggiorna_priorita(lead):
    score = int(lead.get("punteggio", 0) or 0)
    verified = lead.get("stato_abbrevia") not in ("Da verificare", "Non trovato", "")
    if score >= 85 and verified:
        lead["priorita"] = "A — Alta priorità"
    elif score >= 70:
        lead["priorita"] = "B — Da qualificare"
    else:
        lead["priorita"] = "C — Monitorare"
    return lead


def lead_da_risultato_osm(r, settore, paese, profilo="", area="", query_text=""):
    tags = r.get("tags", {}) or {}
    nome = r.get("name", "Azienda")
    descrizione = " ".join(str(tags.get(k, "")) for k in ["description", "industrial", "craft", "product", "man_made", "operator"])
    score = calcola_fit_lead(nome, descrizione, settore, profilo, query_text, area, tags.get("website", ""))
    lead = {
        "id": st.session_state.next_id,
        "azienda": nome,
        "paese": paese,
        "settore": settore,
        "dimensione": "Da verificare",
        "tecnologia_target": MAPPA_TECNOLOGIA_SETTORE.get(settore, "Linee di estrusione personalizzate"),
        "urgenza": "Media",
        "stato": "Nuovo",
        "priorita": "B — Da qualificare",
        "prossima_azione": "Verificare anagrafica Abbrevia",
        "owner": "Non assegnato",
        "ultimo_contatto": "",
        "contatto": "Da individuare",
        "email": "Da verificare",
        "telefono": tags.get("phone") or tags.get("contact:phone") or "Non disponibile",
        "sito_web": tags.get("website") or tags.get("contact:website") or "Non disponibile",
        "fonte": "OpenStreetMap / Overpass",
        "punteggio": score,
        "rating_places": "",
        "note": " | ".join(x for x in [tags.get("addr:street", ""), tags.get("addr:housenumber", ""), tags.get("addr:city", ""), tags.get("addr:postcode", "")] if x),
        "motivo_fit": f"Segnali open-data compatibili con {settore}: {descrizione or 'attività da verificare'}.",
        "profilo_cercato": profilo,
        "area_target": area or paese,
        "lotto": st.session_state.lotto_corrente,
        "data_inserimento": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "dati_reali": True,
        "piva": "",
        "ateco": "",
        "descrizione_ateco": "",
        "rea": "",
        "stato_abbrevia": "Da verificare",
        "info_check": False,
        "osm_lat": r.get("lat", ""),
        "osm_lon": r.get("lon", ""),
    }
    st.session_state.next_id += 1
    return lead


def cerca_lead_friul_filiere(settore, paese, profilo="", area="", n_lead=15):
    """Discovery gratuita OSM -> candidati commerciali; nessun dato aziendale viene inventato."""
    profilo, area = profilo.strip(), area.strip()
    queries = list(PROFILI_FRIUL_FILIERE.get(settore, []))
    if profilo:
        queries.insert(0, profilo)
    if not queries:
        queries = [settore]

    risultati, visti = [], set()
    errors = []
    # Non moltiplichiamo inutilmente le richieste: 3 query mirate sono sufficienti
    # per la discovery iniziale e riducono il rischio di timeout su Overpass.
    for q in queries[:3]:
        rows, err = osm_discovery(q, settore, profilo, area, paese, max_results=min(12, n_lead))
        if err:
            errors.append(err)
            continue
        for r in rows:
            lead = lead_da_risultato_osm(r, settore, paese, profilo, area, q)
            key = normalizza_testo(lead.get("azienda"))
            if key in visti:
                continue
            visti.add(key)
            risultati.append(lead)
            if len(risultati) >= n_lead:
                break
        if len(risultati) >= n_lead:
            break

    if not risultati:
        if errors:
            # Restituiamo un errore leggibile, senza nascondere il problema tecnico.
            return [], "Discovery OSM non disponibile in questo momento. " + " | ".join(errors[-2:])
        return [], "Nessun candidato trovato. Prova a restringere l'area o a usare un profilo produttivo più specifico."

    risultati.sort(key=lambda x: int(x.get("punteggio", 0) or 0), reverse=True)
    return risultati[:n_lead], None


def deduplica_leads(leads):
    out, keys = [], set()
    for lead in leads:
        key = normalizza_testo(lead.get("piva") or lead.get("azienda"))
        if not key or key in keys:
            continue
        keys.add(key)
        out.append(lead)
    return out


def aggiorna_score_da_infocheck(lead, dati):
    lead["info_check"] = True
    score = int(lead.get("punteggio", 0) or 0)
    if dati.get("contatti"):
        score += 5
    if dati.get("analisiSitoWeb"):
        score += 5
    if dati.get("datiOccupazionali"):
        score += 3
    if dati.get("bilanci"):
        score += 5
    lead["punteggio"] = min(99, score)
    lead["prossima_azione"] = "Preparare primo contatto"
    aggiorna_priorita(lead)
    return lead


def verifica_lead_con_abbrevia(lead):
    """Verifica il candidato per ragione sociale su Abbrevia Basic."""
    nome = str(lead.get("azienda", "")).strip()
    if not nome:
        return lead, "Nome azienda mancante"
    risultati, err = abbrevia_search_company(ragione_sociale=nome)
    if err or not risultati:
        lead["stato_abbrevia"] = "Non trovato"
        lead["note"] = f"{lead.get('note', '')} Abbrevia: nessuna corrispondenza."
        return lead, err

    nome_norm = normalizza_testo(nome)
    best = min(
        risultati,
        key=lambda x: abs(len(normalizza_testo(x.get("denominazione", ""))) - len(nome_norm))
    )
    piva = best.get("partitaIva") or best.get("partitaIVA") or ""
    lead["azienda"] = best.get("denominazione") or lead["azienda"]
    lead["piva"] = piva
    lead["stato_abbrevia"] = best.get("descrizioneStatoAttivita", "Trovata")
    lead["ateco"] = best.get("codiceAteco", "")
    lead["descrizione_ateco"] = best.get("descrizioneCodiceAteco", "")
    lead["provincia"] = best.get("siglaProvincia", "")
    lead["comune"] = best.get("comune", "")
    lead["indirizzo"] = best.get("indirizzo", "")
    lead["rea"] = f"{best.get('cciaa', '')}-{best.get('nrea', '')}".strip("-")
    lead["fonte"] = "Lead Search | OpenStreetMap + Abbrevia"
    lead["punteggio"] = min(99, int(lead.get("punteggio", 50)) + 10)
    lead["prossima_azione"] = "Richiedere InfoCheck" if piva else "Qualificare manualmente"
    aggiorna_priorita(lead)
    return lead, None


def _valore_disponibile(lead, key):
    value = lead.get(key, "")
    if value is None:
        return ""
    value = str(value).strip()
    return "" if value.lower() in {"", "nan", "none", "da verificare", "non disponibile"} else value


def genera_valutazione_commerciale(lead):
    """
    Scheda commerciale evidence-based:
    separa ciò che sappiamo da ciò che dobbiamo verificare.
    Non attribuisce bisogni o intenzioni d'acquisto non osservati.
    """
    azienda = _valore_disponibile(lead, "azienda") or "Azienda"
    settore = _valore_disponibile(lead, "settore")
    profilo = _valore_disponibile(lead, "profilo_cercato") or settore
    ateco = _valore_disponibile(lead, "descrizione_ateco") or _valore_disponibile(lead, "ateco")
    provincia = _valore_disponibile(lead, "provincia")
    comune = _valore_disponibile(lead, "comune")
    sito = _valore_disponibile(lead, "sito_web")
    stato = _valore_disponibile(lead, "stato_abbrevia")
    info = lead.get("info_check")
    tecnologia = _valore_disponibile(lead, "tecnologia_target")

    evidenze = []
    if ateco:
        evidenze.append(f"Attività camerale: {ateco}.")
    if settore:
        evidenze.append(f"Settore usato per la ricerca: {settore}.")
    if profilo:
        evidenze.append(f"Profilo ricercato: {profilo}.")
    if comune or provincia:
        evidenze.append(f"Localizzazione: {', '.join(x for x in [comune, provincia] if x)}.")
    if sito:
        evidenze.append("Sito aziendale disponibile per una verifica diretta.")
    if stato:
        evidenze.append(f"Esito verifica Abbrevia: {stato}.")
    if info:
        evidenze.append("Sono disponibili dati di approfondimento InfoCheck.")

    # "Perché chiamare" is deliberately phrased as a reason to investigate,
    # not as a claim that the company has a known need.
    motivi = []
    if ateco or settore:
        motivi.append("L'attività dichiarata è coerente con il perimetro della ricerca.")
    if profilo:
        motivi.append(f"Il profilo emerso è vicino a '{profilo}'.")
    if sito:
        motivi.append("Il sito consente di preparare un approccio più specifico prima del contatto.")
    if info:
        motivi.append("La disponibilità di InfoCheck permette una qualificazione più documentata.")
    if not motivi:
        motivi.append("Il lead è interessante come candidato da qualificare, ma le evidenze sono ancora limitate.")

    # Identify what is still unknown. These gaps become the call agenda.
    incognite = []
    if not info:
        incognite.append("Dimensione e caratteristiche economico-organizzative da approfondire.")
    incognite.append("Prodotti/famiglie di prodotto effettivamente realizzati internamente.")
    incognite.append("Processo produttivo e configurazione delle linee attuali.")
    incognite.append("Eventuali criticità, ampliamenti o investimenti in programma.")
    incognite.append("Referente tecnico, operations/acquisti e processo decisionale.")
    incognite.append("Tempistica reale: progetto attivo, valutazione futura o semplice prospecting.")

    # A restrained hypothesis for Friul Filiere relevance.
    if tecnologia:
        ipotesi = (
            f"Verificare se il processo del prospect presenta un'applicazione per "
            f"{tecnologia}. Il dato non è sufficiente per concludere che esista un bisogno."
        )
    else:
        ipotesi = (
            "Verificare se il processo produttivo del prospect presenta esigenze "
            "compatibili con le tecnologie e le linee Friul Filiere. Non è stata "
            "osservata, allo stato attuale, un'esigenza d'acquisto esplicita."
        )

    # Questions are selected to close the largest information gaps, rather than
    # presenting a generic interrogation checklist.
    domande = [
        "Quali prodotti o famiglie di profili/componenti realizzate direttamente in azienda?",
        "Come viene gestito oggi il relativo processo produttivo e quale parte della linea è più critica?",
        "Ci sono cambiamenti previsti su volumi, prodotti, capacità o impianti nei prossimi 12–24 mesi?",
        "Quando valutate un investimento di questo tipo, chi partecipa alla valutazione tecnica e alla decisione?",
        "C'è un progetto concreto da discutere oppure state facendo una valutazione preliminare del mercato?",
    ]

    # Short opening: informed, but never presumptuous.
    riferimento = ateco or settore or profilo or "la vostra attività"
    opener = (
        f"“Buongiorno, sono [NOME] di Friul Filiere. Sto approfondendo aziende "
        f"che operano nell'ambito di {riferimento}. Vorrei capire meglio come "
        f"gestite oggi la parte produttiva e se avete progetti o esigenze che "
        f"possa avere senso approfondire. Posso farle un paio di domande?”"
    )

    # Disqualifiers / pause conditions protect the sales team's time.
    stop_signals = [
        "L'attività reale non è coerente con il profilo cercato.",
        "Il processo rilevante è completamente esterno o non pertinente.",
        "Non emerge alcun interesse, progetto o motivo per approfondire nel periodo considerato.",
        "Il referente conferma che non esiste un perimetro applicativo compatibile con l'offerta.",
    ]

    if lead.get("stato_abbrevia") in ("Da verificare", "Non trovato", ""):
        prossima = "Prima di chiamare: verificare l'attività reale e identificare il referente corretto."
    elif not info:
        prossima = "Approfondire il profilo con InfoCheck e preparare il contatto sul processo, non sul prodotto."
    else:
        prossima = "Contattare il referente e usare la chiamata per confermare processo, progetto, interlocutori e tempistica."

    return {
        "azienda": azienda,
        "evidenze": evidenze,
        "motivi": motivi,
        "incognite": incognite,
        "ipotesi": ipotesi,
        "tecnologia": tecnologia or "Da definire dopo la qualificazione del processo.",
        "domande": domande,
        "opener": opener,
        "stop_signals": stop_signals,
        "prossima_azione": prossima,
    }


def pagina_sales_intelligence():
    st.markdown(
        '<div class="ffe-header"><h1>Preparazione al contatto</h1>'
        '<p>Una scheda sintetica per decidere se chiamare, con quale approccio e cosa verificare.</p></div>',
        unsafe_allow_html=True,
    )

    df = df_leads()
    if df.empty:
        st.info("Importa prima alcuni lead nel CRM.")
        return

    ids = df["id"].tolist()
    selected = st.selectbox(
        "Azienda",
        ids,
        format_func=lambda x: f"#{x} — {df[df['id'] == x]['azienda'].iloc[0]}"
    )
    lead = next(l for l in st.session_state.leads if l["id"] == selected)
    v = genera_valutazione_commerciale(lead)

    st.caption(
        "Principio della scheda: distinguere fatti, ipotesi e informazioni mancanti. "
        "La priorità aiuta a ordinare il lavoro; non rappresenta una previsione di acquisto."
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Score", lead.get("punteggio", 0))
    c2.metric("Priorità", lead.get("priorita", "C — Monitorare"))
    c3.metric("Abbrevia", lead.get("stato_abbrevia", "Da verificare"))
    c4.metric("CRM", lead.get("stato", "Nuovo"))

    st.markdown("### In 30 secondi")
    for item in v["motivi"]:
        st.write("• " + item)

    st.markdown("### Cosa sappiamo")
    if v["evidenze"]:
        for item in v["evidenze"]:
            st.write("• " + item)
    else:
        st.write("Le evidenze disponibili sono ancora limitate.")

    st.markdown("### Cosa non sappiamo ancora")
    for item in v["incognite"]:
        st.write("• " + item)

    st.markdown("### Perché può valere una chiamata")
    st.write(
        "La ragione per contattare il prospect è verificare un possibile fit, "
        "non presumere che esista già un progetto."
    )
    for item in v["motivi"]:
        st.write("• " + item)

    st.markdown("### Ipotesi di applicazione")
    st.write(v["ipotesi"])

    st.markdown("### Tecnologia da verificare")
    st.write(v["tecnologia"])

    st.markdown("### Apertura consigliata")
    st.code(v["opener"], language=None)

    st.markdown("### Domande per la prima conversazione")
    for i, domanda in enumerate(v["domande"], 1):
        st.write(f"{i}. {domanda}")

    st.markdown("### Quando fermarsi o non insistere")
    for item in v["stop_signals"]:
        st.write("• " + item)

    st.markdown("### Prossima azione")
    st.info(v["prossima_azione"])

    with st.expander("Dati anagrafici e commerciali"):
        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**Azienda:** {_valore_disponibile(lead, 'azienda') or '—'}")
            st.write(f"**Settore:** {_valore_disponibile(lead, 'settore') or '—'}")
            st.write(f"**Profilo cercato:** {_valore_disponibile(lead, 'profilo_cercato') or '—'}")
            st.write(f"**ATECO:** {_valore_disponibile(lead, 'ateco') or '—'}")
            st.write(f"**Descrizione ATECO:** {_valore_disponibile(lead, 'descrizione_ateco') or '—'}")
        with c2:
            st.write(f"**Comune:** {_valore_disponibile(lead, 'comune') or '—'}")
            st.write(f"**Provincia:** {_valore_disponibile(lead, 'provincia') or '—'}")
            st.write(f"**P.IVA:** {_valore_disponibile(lead, 'piva') or '—'}")
            st.write(f"**Sito:** {_valore_disponibile(lead, 'sito_web') or '—'}")
            st.write(f"**Prossima azione CRM:** {_valore_disponibile(lead, 'prossima_azione') or '—'}")

# =========================================================================
# LEAD MOCK
# =========================================================================

def genera_lead_mock(settore, paese, fonte, dimensione=None, urgenza=None, tecnologia=None, nota_extra=""):
    lead_id = st.session_state.next_id
    st.session_state.next_id += 1
    azienda = random.choice(PREFISSI_AZIENDA) + random.choice(SUFFISSI_AZIENDA)
    dominio = azienda.lower().replace(" ", "").replace(".", "")[:12]
    return {
        "id": lead_id,
        "azienda": azienda,
        "paese": paese,
        "settore": settore,
        "dimensione": dimensione or random.choice(DIMENSIONI_AZIENDA),
        "tecnologia_target": tecnologia or MAPPA_TECNOLOGIA_SETTORE.get(settore, random.choice(TECNOLOGIE_FRIUL_FILIERE)),
        "urgenza": urgenza or random.choice(LIVELLI_URGENZA),
        "stato": "Nuovo",
        "contatto": random.choice(NOMI_CONTATTO),
        "email": f"direzione@{dominio}.com",
        "telefono": f"+39 0432 {random.randint(100000, 999999)}",
        "sito_web": f"www.{dominio}.com",
        "fonte": fonte,
        "punteggio": random.randint(45, 95),
        "note": nota_extra,
        "lotto": st.session_state.lotto_corrente,
        "data_inserimento": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "dati_reali": False,
        "piva": f"IT{random.randint(10000000000, 99999999999)}",
    }


def aggiungi_leads(nuovi):
    st.session_state.leads.extend(nuovi)


def df_leads():
    return pd.DataFrame(st.session_state.leads) if st.session_state.leads else pd.DataFrame()


# =========================================================================
# EXPORT HELPERS (PDF / CSV)
# =========================================================================

def export_csv_bytes(df):
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")


def _pdf_safe(t):
    return str(t).encode("latin-1", "replace").decode("latin-1")


def export_pdf_dossier(lead, dossier_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(14, 31, 61)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 12, _pdf_safe("Friul Filiere - Dossier Tecnico Commerciale"), ln=True, fill=True)
    pdf.ln(3)
    pdf.set_text_color(200, 16, 46)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, _pdf_safe(lead["azienda"]), ln=True)
    pdf.set_text_color(60, 60, 60)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, _pdf_safe(f"{lead['paese']} | {lead['settore']} | P.IVA: {lead.get('piva', 'N/D')}"), ln=True)
    pdf.ln(4)
    pdf.set_text_color(20, 20, 20)
    for p in dossier_text.split("\n"):
        pdf.multi_cell(0, 5, _pdf_safe(p))
    return bytes(pdf.output(dest="S"))


def export_pdf_lista_lead(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(14, 31, 61)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 12, _pdf_safe("Friul Filiere Lead Engine - Elenco Lead"), ln=True, fill=True)
    pdf.ln(3)
    pdf.set_fill_color(200, 16, 46)
    pdf.set_font("Helvetica", "B", 8)
    cols = ["azienda", "paese", "settore", "urgenza", "punteggio", "telefono"]
    w = [45, 25, 35, 20, 20, 45]
    for c, larg in zip(cols, w):
        pdf.cell(larg, 7, _pdf_safe(c.upper()), border=1, fill=True)
    pdf.ln()
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(20, 20, 20)
    for _, r in df.iterrows():
        for c, larg in zip(cols, w):
            pdf.cell(larg, 6, _pdf_safe(str(r.get(c, ""))[:25]), border=1)
        pdf.ln()
    return bytes(pdf.output(dest="S"))


# =========================================================================
# DOSSIER & OUTREACH ENGINE
# =========================================================================

def ottieni_dossier(lead, lingua):
    chiave = f"{lead['id']}_{lingua}"
    if chiave in st.session_state.dossier_cache:
        return st.session_state.dossier_cache[chiave]

    prompt = f"""
    Agisci come senior sales engineer per Friul Filiere, azienda specializzata in linee e sistemi per estrusione di materie plastiche.
    Lingua: {lingua}.
    Prepara un dossier tecnico-commerciale breve e utilizzabile da un commerciale.
    NON inventare dati sull'azienda e NON dichiarare che l'azienda usa una tecnologia specifica se non è documentato.
    Distingui chiaramente tra dati verificati e ipotesi commerciali.

    Azienda: {lead['azienda']}
    Settore: {lead['settore']}
    Profilo cercato: {lead.get('profilo_cercato', '')}
    Tecnologia Friul Filiere potenzialmente rilevante: {lead['tecnologia_target']}
    ATECO: {lead.get('ateco', '')}
    Descrizione ATECO: {lead.get('descrizione_ateco', '')}
    Dati verificati: {lead.get('note', '')}

    Struttura:
    1) Perché questa azienda può essere un prospect
    2) Ipotesi di bisogno produttivo da verificare
    3) Soluzione Friul Filiere potenzialmente pertinente
    4) 3 domande da fare al primo contatto
    5) Prossimo passo commerciale consigliato
    """
    testo, st_call = call_gemini_api(prompt)
    if not testo:
        testo = f"[Dossier sintetico Friul Filiere]\nProposta per {lead['azienda']} ({lead['settore']}): adozione di {lead['tecnologia_target']}. Soluzione da valutare in funzione del processo, del prodotto e della linea esistente."
    st.session_state.dossier_cache[chiave] = testo
    return testo


def genera_sequenza_email(lead, lingua):
    return [
        {"step": 1, "giorno_invio": "Giorno 0", "oggetto": f"Efficienza di linea per {lead['azienda']}", "corpo": f"Gentile team di {lead['azienda']},\nnotiamo la vostra presenza nel settore {lead['settore']}. Friul Filiere offre impianti specializzati in {lead['tecnologia_target']}."},
        {"step": 2, "giorno_invio": "Giorno 4", "oggetto": f"Riduzione scarti per {lead['azienda']}", "corpo": f"Gentile referente,\npossiamo confrontarci sui requisiti tecnici, sulle criticità della linea attuale e sulle eventuali esigenze di nuova linea o retrofit."},
        {"step": 3, "giorno_invio": "Giorno 9", "oggetto": f"Ultimo spunto tecnico per {lead['azienda']}", "corpo": f"Restiamo a disposizione per una demo o un layout personalizzato. Cordiali saluti,\nFriul Filiere"},
    ]


# =========================================================================
# SIDEBAR
# =========================================================================

def sidebar():
    with st.sidebar:
        st.markdown("## 🏭 FRIUL FILIERE")
        st.markdown("##### Lead Engine & Abbrevia X")
        st.markdown("---")

        pagine = [
            "Dashboard",
            "🏢 Dati Ufficiali Imprese (Abbrevia X)",
            "🎯 Lead Search — Potenziali Clienti",
            "🎪 Ricerca Fiere",
            "📈 Progetti di Investimento",
            "👥 Analisi Lookalike",
            "🛰️ Radar Espansione & Organico",
            "🎯 Sales Twin Verticale",
            "📄 Dossier Tecnico AI",
            "✉️ Sequenze Outreach",
            "🗂️ CRM & Database Lead",
        ]
        st.session_state.pagina = st.radio("Modulo", pagine, label_visibility="collapsed")

        st.markdown("---")
        with st.expander("🏢 Connessione Abbrevia X", expanded=True):
            st.session_state.abbrevia_env = st.selectbox(
                "Ambiente", ["production", "pre-production"],
                index=0 if st.session_state.abbrevia_env == "production" else 1
            )

            st.caption("🔐 Credenziali Abbrevia configurate direttamente nell'app.")

            if st.button("🔌 Verifica Token Abbrevia"):
                token, err = abbrevia_get_token()
                if err:
                    st.error(err)
                else:
                    st.success("✅ Connessione riuscita (Token attivo)")

        with st.expander("🌍 Discovery & AI"):
            st.success("Discovery aziende: OpenStreetMap / Overpass — nessuna chiave")
            if st.session_state.gemini_api_key:
                st.success("Gemini: configurato")
            else:
                st.caption("Gemini: opzionale")

        st.markdown("---")
        st.metric("Lead nel CRM", len(st.session_state.leads))
        st.metric("Lotto di ricerca", st.session_state.lotto_corrente)


# =========================================================================
# PAGINA: MODULO ABBREVIA X
# =========================================================================

def pagina_abbrevia():
    st.markdown('<div class="ffe-header"><h1>🏢 Dati Ufficiali Imprese (Abbrevia X)</h1><p>Interroga direttamente il Registro Imprese italiano e genera schede InfoCheck per verificare solvibilità, fatturati e compagini sociali</p></div>', unsafe_allow_html=True)

    tab_ricerca, tab_infocheck = st.tabs(["🔎 Ricerca Ufficiale Registro Imprese", "📊 Scheda Approfondita InfoCheck"])

    with tab_ricerca:
        st.markdown("#### Ricerca Aziende nel Database Camerale")
        with st.form("form_cerca_abbrevia"):
            c1, c2 = st.columns(2)
            with c1:
                r_sociale = st.text_input("Ragione Sociale (es. Extrusion, Plast...)")
                piva = st.text_input("Partita IVA (11 cifre)")
            with c2:
                cf = st.text_input("Codice Fiscale")
                col_pr, col_rea = st.columns(2)
                with col_pr:
                    provincia = st.text_input("Provincia CCIAA (es. UD, MI)")
                with col_rea:
                    rea = st.text_input("Numero REA")

            submit = st.form_submit_button("🔎 Interroga Abbrevia X")

        if submit:
            if not any([r_sociale, piva, cf, (provincia and rea)]):
                st.warning("Inserisci almeno un criterio (Ragione Sociale, Partita IVA, CF oppure Provincia + REA).")
            else:
                with st.spinner("Interrogazione Registro Imprese in corso..."):
                    risultati, err = abbrevia_search_company(
                        ragione_sociale=r_sociale, piva=piva, cf=cf, provincia=provincia, rea=rea
                    )
                if err:
                    st.error(err)
                elif not risultati:
                    st.info("Nessuna azienda trovata con i parametri indicati.")
                else:
                    st.success(f"Trovate {len(risultati)} aziende corrispondenti.")
                    for item in risultati:
                        piva_item = item.get("partitaIva") or item.get("partitaIVA") or item.get("codiceFiscale", "")
                        with st.container():
                            st.markdown(f"""
                            <div class="ffe-card">
                                <span class="ffe-badge ffe-badge-abbrevia">DATI UFFICIALI CCIAA</span>
                                <span class="ffe-badge ffe-badge-info">Stato: {item.get('descrizioneStatoAttivita', 'N/D')}</span>
                                <h3>{item.get('denominazione', 'Azienda')}</h3>
                                <b>P.IVA / CF:</b> {piva_item} | <b>Natura:</b> {item.get('naturaGiuridica', 'N/D')}<br>
                                <b>Sede:</b> {item.get('indirizzo', '')} {item.get('cap', '')} {item.get('comune', '')} ({item.get('siglaProvincia', '')})<br>
                                <b>ATECO:</b> {item.get('codiceAteco', '')} - {item.get('descrizioneCodiceAteco', '')}<br>
                                <b>REA:</b> {item.get('cciaa', '')} {item.get('nrea', '')}
                            </div>
                            """, unsafe_allow_html=True)

                            col_btn1, col_btn2 = st.columns([1, 3])
                            with col_btn1:
                                if st.button(f"📥 Importa Lead #{piva_item}", key=f"imp_{piva_item}"):
                                    lead_id = st.session_state.next_id
                                    st.session_state.next_id += 1
                                    st.session_state.leads.append({
                                        "id": lead_id,
                                        "azienda": item.get("denominazione", "Azienda"),
                                        "paese": "Italia",
                                        "settore": "Estrusione / Plastica",
                                        "dimensione": item.get("naturaGiuridica", "Piccola/Media"),
                                        "tecnologia_target": "Linee di estrusione personalizzate",
                                        "urgenza": "Media",
                                        "stato": "Qualificato",
                                        "contatto": "Legale Rappresentante (CCIAA)",
                                        "email": "Verificare tramite InfoCheck",
                                        "telefono": "Da verificare",
                                        "sito_web": "Non presente in anagrafica base",
                                        "fonte": "Abbrevia X (Ufficiale)",
                                        "punteggio": 90,
                                        "note": f"ATECO: {item.get('codiceAteco')} | REA: {item.get('cciaa')}-{item.get('nrea')}",
                                        "lotto": st.session_state.lotto_corrente,
                                        "data_inserimento": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                        "dati_reali": True,
                                        "piva": piva_item,
                                    })
                                    st.success(f"Azienda {item.get('denominazione')} aggiunta ai lead!")

    with tab_infocheck:
        st.markdown("#### Richiesta Scheda di Profondità (InfoCheck)")
        st.caption("Fornisce informazioni complete su bilanci, dipendenti, esponenti, negatività e gruppo societario.")
        c_piva, c_btn = st.columns([2, 1])
        with c_piva:
            input_check = st.text_input("Partita IVA o Codice Fiscale dell'azienda", placeholder="Es. 01234567890")
        with c_btn:
            st.write("")
            st.write("")
            esegui_infocheck = st.button("📊 Scarica InfoCheck")

        if esegui_infocheck:
            if not input_check:
                st.warning("Inserisci una Partita IVA o un Codice Fiscale valido.")
            else:
                with st.spinner("Recupero scheda InfoCheck da Abbrevia X..."):
                    dati_info, err = abbrevia_get_infocheck(input_check)
                if err:
                    st.error(err)
                elif dati_info:
                    st.success("Scheda InfoCheck scaricata con successo!")
                    
                    # Sezione Anagrafica & Sintesi
                    anagrafica = dati_info.get("anagrafica", {})
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("##### 🏢 Dati Anagrafici")
                        st.json(anagrafica if anagrafica else {"messaggio": "Dati base non dettagliati"})
                    with col_b:
                        st.markdown("##### 👥 Dati Occupazionali & Dipendenti")
                        st.json(dati_info.get("datiOccupazionali", []))

                    st.markdown("---")
                    col_c, col_d = st.columns(2)
                    with col_c:
                        st.markdown("##### 📈 Bilanci & Performance")
                        st.json(dati_info.get("bilanci", []))
                    with col_d:
                        st.markdown("##### ⚠️ Negatività & Eventi Pregiudizievoli")
                        st.json(dati_info.get("negativita", {}))


# =========================================================================
# ALTRE PAGINE OPERATIVE
# =========================================================================

def pagina_dashboard():
    st.markdown(
        '<div class="ffe-header"><h1>Dashboard Commerciale</h1>'
        '<p>Vista rapida di priorità, pipeline e prossime azioni</p></div>',
        unsafe_allow_html=True,
    )
    df = df_leads()
    if df.empty:
        st.info("Nessun lead nel CRM. Parti da 🎯 Lead Search — Potenziali Clienti.")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Lead totali", len(df))
    c2.metric("A — Contattare", int(df.get("priorita", pd.Series(dtype=str)).astype(str).str.startswith("A —").sum()))
    c3.metric("In trattativa", int((df["stato"] == "In trattativa").sum()))
    c4.metric("Score medio", round(pd.to_numeric(df["punteggio"], errors="coerce").mean(), 1))

    st.markdown("### Priorità commerciali")
    top = df.sort_values("punteggio", ascending=False).head(15)
    cols = [c for c in ["azienda", "priorita", "punteggio", "settore", "provincia", "ateco", "prossima_azione"] if c in top.columns]
    st.dataframe(top[cols], use_container_width=True, hide_index=True)

    st.markdown("### Pipeline")
    pipeline = df.groupby("stato").size().reindex(STATI_LEAD, fill_value=0)
    st.bar_chart(pipeline)


def pagina_ricerca_settore():
    st.markdown(
        '<div class="ffe-header"><h1>🎯 Lead Search — Potenziali Clienti</h1>'
        '<p>Trova, verifica e prioritizza aziende da contattare per Friul Filiere</p></div>',
        unsafe_allow_html=True,
    )

    st.info(
        "Workflow commerciale: ① scoperta open-data ② verifica anagrafica Abbrevia "
        "③ eventuale InfoCheck ④ priorità ⑤ CRM. "
        "OpenStreetMap è una fonte di discovery indicativa; i dati camerali Abbrevia sono distinti e marcati."
    )

    with st.form("form_lead_search"):
        c1, c2 = st.columns(2)
        with c1:
            settore = st.selectbox("Settore target", SETTORI)
            profilo = st.text_input(
                "🎯 Cosa produce / profilo cliente",
                placeholder="Es. profili plastici per arredamento, componenti estrusi automotive",
            )
        with c2:
            paese = st.selectbox("Paese", PAESI, index=0)
            area = st.text_input(
                "📍 Area geografica",
                placeholder="Es. Veneto, Lombardia, Vicenza, Udine, Nord Italia",
            )
        n = st.slider("Numero candidati", 5, 30, 15)
        cerca = st.form_submit_button("Cerca aziende", use_container_width=True)

    if cerca:
        with st.spinner("Ricerca candidati e ranking commerciale..."):
            leads, err = cerca_lead_friul_filiere(settore, paese, profilo, area, n)
        if err:
            st.error(err)
            return
        st.session_state.lead_search_results = deduplica_leads(leads)
        st.session_state.last_search_config = {
            "settore": settore, "profilo": profilo, "paese": paese, "area": area
        }
        st.success(
            f"Trovati {len(st.session_state.lead_search_results)} candidati. "
            "Verifica con Abbrevia i migliori prima di importarli nel CRM."
        )

    risultati = st.session_state.get("lead_search_results", [])
    if not risultati:
        st.markdown("### Impostazione della ricerca")
        st.markdown(
            "Inserisci **cosa produce l'azienda che vuoi trovare**, non solo il settore. La discovery usa OpenStreetMap e non richiede API key. "
            "Esempi: `profili plastici per arredamento`, `componenti estrusi automotive`, "
            "`profili PVC per serramenti`, `tubi tecnici per irrigazione`."
        )
        return

    # Filtri commerciali sui risultati già ottenuti.
    f1, f2, f3 = st.columns(3)
    with f1:
        min_score = st.slider("Score minimo", 0, 99, 50)
    with f2:
        priorita_filter = st.selectbox(
            "Priorità", ["Tutte", "A — Alta priorità", "B — Da qualificare", "C — Monitorare"]
        )
    with f3:
        stato_filter = st.selectbox(
            "Verifica", ["Tutte", "Solo verificati Abbrevia", "Da verificare"]
        )

    filtrati = []
    for lead in risultati:
        if int(lead.get("punteggio", 0) or 0) < min_score:
            continue
        if priorita_filter != "Tutte" and lead.get("priorita") != priorita_filter:
            continue
        verified = lead.get("stato_abbrevia") not in ("Da verificare", "Non trovato", "")
        if stato_filter == "Solo verificati Abbrevia" and not verified:
            continue
        if stato_filter == "Da verificare" and verified:
            continue
        filtrati.append(lead)

    filtrati.sort(key=lambda x: int(x.get("punteggio", 0) or 0), reverse=True)

    a, b, c, d = st.columns(4)
    a.metric("Candidati", len(risultati))
    b.metric("Visualizzati", len(filtrati))
    c.metric("Top A", sum(1 for x in risultati if x.get("priorita", "").startswith("A —")))
    d.metric("Verificati", sum(
        1 for x in risultati
        if x.get("stato_abbrevia") not in ("Da verificare", "Non trovato", "")
    ))

    st.markdown("### Operatività")
    a1, a2, a3 = st.columns(3)
    with a1:
        if st.button("Verifica i migliori con Abbrevia", use_container_width=True):
            verificati = []
            progress = st.progress(0)
            for i, lead in enumerate(filtrati[:10], 1):
                updated, _ = verifica_lead_con_abbrevia(dict(lead))
                verificati.append(updated)
                progress.progress(i / max(1, min(10, len(filtrati))))
            by_id = {x["id"]: x for x in risultati}
            for x in verificati:
                by_id[x["id"]] = x
            st.session_state.lead_search_results = sorted(
                by_id.values(), key=lambda x: int(x.get("punteggio", 0) or 0), reverse=True
            )
            st.success("Verifica completata.")
            st.rerun()

    with a2:
        if st.button("Importa risultati nel CRM", use_container_width=True):
            esistenti = {normalizza_testo(x.get("piva") or x.get("azienda")) for x in st.session_state.leads}
            nuovi = []
            for lead in filtrati:
                key = normalizza_testo(lead.get("piva") or lead.get("azienda"))
                if key not in esistenti:
                    nuovi.append(lead)
                    esistenti.add(key)
            aggiungi_leads(nuovi)
            st.success(f"Importati {len(nuovi)} nuovi lead nel CRM.")

    with a3:
        df_export = pd.DataFrame(filtrati)
        if not df_export.empty:
            st.download_button(
                "⬇️ Scarica lista CSV",
                export_csv_bytes(df_export),
                "friul_filiere_lead_search.csv",
                "text/csv",
                use_container_width=True,
            )

    if not filtrati:
        st.warning("Nessun candidato soddisfa i filtri.")
        return

    rows = []
    for lead in filtrati:
        rows.append({
            "Score": lead.get("punteggio", ""),
            "Priorità": lead.get("priorita", ""),
            "Azienda": lead.get("azienda", ""),
            "Settore": lead.get("settore", ""),
            "Comune": lead.get("comune", ""),
            "Provincia": lead.get("provincia", ""),
            "ATECO": lead.get("ateco", "") or "—",
            "Abbrevia": lead.get("stato_abbrevia", "Da verificare"),
            "Prossima azione": lead.get("prossima_azione", ""),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown("### Schede lead")
    for i, lead in enumerate(filtrati):
        titolo = (
            f"{lead.get('priorita', '⚪')}  {lead.get('azienda', 'Azienda')} "
            f"· Score {lead.get('punteggio', 0)}"
        )
        with st.expander(titolo):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.write(f"**Profilo cercato:** {lead.get('profilo_cercato') or lead.get('settore')}")
                st.write(f"**Fit:** {lead.get('motivo_fit', 'Da qualificare')}")
                st.write(f"**Tecnologia potenziale:** {lead.get('tecnologia_target')}")
            with c2:
                st.write(f"**ATECO:** {lead.get('ateco') or 'Da verificare'}")
                st.write(f"**P.IVA:** {lead.get('piva') or 'Da verificare'}")
                st.write(f"**Stato Abbrevia:** {lead.get('stato_abbrevia', 'Da verificare')}")
            with c3:
                st.write(f"**Telefono:** {lead.get('telefono', '')}")
                st.write(f"**Sito:** {lead.get('sito_web', '')}")
                st.write(f"**Azione:** {lead.get('prossima_azione', '')}")

            b1, b2 = st.columns(2)
            with b1:
                if lead.get("piva") and st.button(
                    "📊 InfoCheck Abbrevia",
                    key=f"info_lead_{i}_{lead.get('piva')}"
                ):
                    with st.spinner("Recupero InfoCheck..."):
                        info, info_err = abbrevia_get_infocheck(lead["piva"])
                    if info_err:
                        st.error(info_err)
                    else:
                        lead = aggiorna_score_da_infocheck(lead, info)
                        # aggiorna anche la copia in sessione
                        for idx, saved in enumerate(st.session_state.lead_search_results):
                            if saved.get("id") == lead.get("id"):
                                st.session_state.lead_search_results[idx] = lead
                                break
                        st.success("InfoCheck acquisito e score aggiornato.")
                        st.json(info)
            with b2:
                if st.button("📥 Aggiungi al CRM", key=f"crm_lead_{i}_{lead.get('id')}"):
                    esistenti = {
                        normalizza_testo(x.get("piva") or x.get("azienda"))
                        for x in st.session_state.leads
                    }
                    key = normalizza_testo(lead.get("piva") or lead.get("azienda"))
                    if key in esistenti:
                        st.warning("Lead già presente nel CRM.")
                    else:
                        aggiungi_leads([lead])
                        st.success("Lead aggiunto al CRM.")

            st.caption(lead.get("note", ""))



def pagina_dossier():
    st.markdown('<div class="ffe-header"><h1>📄 Dossier Tecnico Commerciale</h1><p>Generazione personalizzata con focus tecnologico Friul Filiere</p></div>', unsafe_allow_html=True)
    df = df_leads()
    if df.empty:
        st.warning("Genera o importa prima dei lead nel CRM.")
        return
    idx = st.selectbox("Seleziona Azienda", df["id"].tolist(), format_func=lambda x: f"#{x} - {df[df['id']==x]['azienda'].values[0]}")
    lead = next(l for l in st.session_state.leads if l["id"] == idx)
    lingua = st.selectbox("Lingua", ["Italiano", "Inglese", "Tedesco", "Francese"])
    if st.button("Genera Dossier"):
        testo = ottieni_dossier(lead, lingua)
        st.text_area("Dossier", testo, height=300)
        st.download_button("⬇️ Scarica PDF", export_pdf_dossier(lead, testo), file_name=f"dossier_{lead['azienda']}.pdf", mime="application/pdf")


def pagina_outreach():
    st.markdown('<div class="ffe-header"><h1>✉️ Sequenze Outreach Email</h1><p>Pianificazione messaggi di contatto commerciale</p></div>', unsafe_allow_html=True)
    df = df_leads()
    if df.empty:
        st.warning("Genera o importa prima dei lead.")
        return
    idx = st.selectbox("Seleziona Lead", df["id"].tolist(), format_func=lambda x: f"#{x} - {df[df['id']==x]['azienda'].values[0]}")
    lead = next(l for l in st.session_state.leads if l["id"] == idx)
    lingua = st.selectbox("Lingua", ["Italiano", "Inglese", "Tedesco", "Francese"])
    if st.button("Crea sequenza 3 email"):
        seq = genera_sequenza_email(lead, lingua)
        for s in seq:
            st.markdown(f"**Step {s['step']} ({s['giorno_invio']})** - Oggetto: *{s['oggetto']}*")
            st.text_area(f"Testo Step {s['step']}", s["corpo"], height=100)


def pagina_crm():
    st.markdown(
        '<div class="ffe-header"><h1>🗂️ CRM Commerciale</h1>'
        '<p>Priorità, stato, prossima azione ed export dei lead</p></div>',
        unsafe_allow_html=True,
    )
    df = df_leads()
    if df.empty:
        st.info("Nessun lead presente nella sessione corrente. Importa lead dalla Lead Search.")
        return

    # KPI commerciali
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Lead", len(df))
    c2.metric("Da contattare", int((df["stato"] == "Nuovo").sum()))
    c3.metric("In trattativa", int((df["stato"] == "In trattativa").sum()))
    c4.metric("Qualificati", int((df["stato"] == "Qualificato").sum()))

    st.markdown("### Pipeline")
    filtro_stato = st.selectbox("Filtra stato", ["Tutti"] + STATI_LEAD)
    vista = df if filtro_stato == "Tutti" else df[df["stato"] == filtro_stato]

    cols = [
        c for c in [
            "id", "azienda", "priorita", "punteggio", "stato",
            "prossima_azione", "owner", "settore", "paese",
            "ateco", "piva", "telefono", "sito_web"
        ] if c in vista.columns
    ]
    st.dataframe(vista[cols], use_container_width=True, hide_index=True)

    st.markdown("### Aggiorna un lead")
    ids = vista["id"].tolist()
    if ids:
        selected = st.selectbox(
            "Lead",
            ids,
            format_func=lambda x: f"#{x} — {vista[vista['id'] == x]['azienda'].iloc[0]}"
        )
        lead = next(l for l in st.session_state.leads if l["id"] == selected)

        c1, c2, c3 = st.columns(3)
        with c1:
            nuovo_stato = st.selectbox(
                "Stato",
                STATI_LEAD,
                index=STATI_LEAD.index(lead.get("stato", "Nuovo"))
                if lead.get("stato", "Nuovo") in STATI_LEAD else 0,
            )
        with c2:
            nuova_priorita = st.selectbox(
                "Priorità",
                ["A — Alta priorità", "B — Da qualificare", "C — Monitorare"],
                index=(
                    ["A — Alta priorità", "B — Da qualificare", "C — Monitorare"].index(
                        lead.get("priorita", "B — Da qualificare")
                    )
                    if lead.get("priorita") in [
                        "A — Alta priorità", "B — Da qualificare", "C — Monitorare"
                    ] else 1
                ),
            )
        with c3:
            nuova_azione = st.selectbox(
                "Prossima azione",
                [
                    "Verificare anagrafica Abbrevia",
                    "Richiedere InfoCheck",
                    "Individuare referente",
                    "Preparare primo contatto",
                    "Inviare email",
                    "Telefonare",
                    "Programmare call",
                    "Inviare proposta",
                    "Follow-up",
                    "Nurturing",
                ],
                index=(
                    [
                        "Verificare anagrafica Abbrevia",
                        "Richiedere InfoCheck",
                        "Individuare referente",
                        "Preparare primo contatto",
                        "Inviare email",
                        "Telefonare",
                        "Programmare call",
                        "Inviare proposta",
                        "Follow-up",
                        "Nurturing",
                    ].index(lead.get("prossima_azione", "Verificare anagrafica Abbrevia"))
                    if lead.get("prossima_azione") in [
                        "Verificare anagrafica Abbrevia",
                        "Richiedere InfoCheck",
                        "Individuare referente",
                        "Preparare primo contatto",
                        "Inviare email",
                        "Telefonare",
                        "Programmare call",
                        "Inviare proposta",
                        "Follow-up",
                        "Nurturing",
                    ] else 0
                ),
            )

        note = st.text_area("Note commerciali", value=lead.get("note", ""), height=120)
        if st.button("💾 Salva aggiornamento", use_container_width=True):
            lead["stato"] = nuovo_stato
            lead["priorita"] = nuova_priorita
            lead["prossima_azione"] = nuova_azione
            lead["note"] = note
            st.success("Lead aggiornato.")
            st.rerun()

    st.markdown("### Export")
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "⬇️ Esporta CSV",
            export_csv_bytes(vista),
            "lead_friul_filiere.csv",
            "text/csv",
            use_container_width=True,
        )
    with c2:
        st.download_button(
            "⬇️ Esporta PDF",
            export_pdf_lista_lead(vista),
            "lead_friul_filiere.pdf",
            "application/pdf",
            use_container_width=True,
        )

    if st.button("🗑️ Svuota CRM"):
        st.session_state.leads = []
        st.rerun()


# =========================================================================
# MODULI OPERATIVI AGGIUNTIVI — SENZA API A PAGAMENTO
# =========================================================================

FIERE_FRIUL = [
    {"fiera":"K","citta":"Düsseldorf","paese":"Germania","settori":"Plastica, estrusione, trasformazione","uso":"Alta","nota":"Fiera di riferimento; verificare edizione e date sui canali ufficiali."},
    {"fiera":"Fakuma","citta":"Friedrichshafen","paese":"Germania","settori":"Plastica, stampaggio, automazione","uso":"Alta","nota":"Rilevante per trasformazione plastica e tecnologie di processo."},
    {"fiera":"PLAST","citta":"Milano","paese":"Italia","settori":"Plastica, gomma, estrusione","uso":"Alta","nota":"Riferimento italiano; verificare prossima edizione e calendario ufficiale."},
    {"fiera":"Chinaplas","citta":"Cina","paese":"Cina","settori":"Plastica, estrusione, automazione","uso":"Media","nota":"Scouting internazionale e competitor/partner."},
    {"fiera":"NPE","citta":"USA","paese":"Stati Uniti","settori":"Plastica, processing, automazione","uso":"Media","nota":"Utile per mercato Nord America; verificare prossima edizione."},
    {"fiera":"PLASTPOL","citta":"Kielce","paese":"Polonia","settori":"Plastica, gomma, macchine","uso":"Media","nota":"Utile per Europa centro-orientale."},
]

def pagina_fiere():
    st.markdown('<div class="ffe-header"><h1>🎪 Ricerca Fiere</h1><p>Selezione fiere utili per scouting commerciale e presidio dei mercati</p></div>', unsafe_allow_html=True)
    st.info("Questo modulo costruisce un piano commerciale; non sostituisce il calendario ufficiale. Date, espositori e partecipazioni vanno verificati sui siti delle fiere.")
    settore=st.selectbox("Filtro settore",["Tutti"]+SETTORI)
    rows=FIERE_FRIUL if settore=="Tutti" else [x for x in FIERE_FRIUL if settore.lower() in x["settori"].lower() or settore in ("Automotive","Medicale") and "Plastica" in x["settori"]]
    st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
    fiera=st.selectbox("Fiera da presidiare",[x["fiera"] for x in FIERE_FRIUL])
    obiettivo=st.selectbox("Obiettivo",["Scouting prospect","Incontri con clienti","Partner / agenti","Competitor intelligence"])
    note=st.text_area("Note commerciali")
    if st.button("Aggiungi al piano fiere",use_container_width=True):
        st.session_state.setdefault("piano_fiere",[]).append({"Fiera":fiera,"Obiettivo":obiettivo,"Note":note,"Stato":"Da pianificare"})
        st.success("Fiera aggiunta al piano.")
    if st.session_state.get("piano_fiere"):
        st.dataframe(pd.DataFrame(st.session_state.piano_fiere),use_container_width=True,hide_index=True)

def pagina_investimenti():
    st.markdown('<div class="ffe-header"><h1>📈 Progetti di Investimento</h1><p>Segnali disponibili nei dati InfoCheck per decidere quali aziende approfondire</p></div>',unsafe_allow_html=True)
    if not st.session_state.leads:
        st.info("Importa prima alcuni lead nel CRM."); return
    opzioni=[x for x in st.session_state.leads if x.get("info_check")]
    if not opzioni:
        st.info("Nessun lead con InfoCheck acquisito. Il modulo non inventa progetti di investimento: usa solo dati realmente presenti."); return
    for lead in opzioni:
        info=st.session_state.infocheck_cache.get(lead.get("piva"),{})
        bilanci=info.get("bilanci",[]) if isinstance(info,dict) else []
        occup=info.get("datiOccupazionali",[]) if isinstance(info,dict) else []
        st.markdown(f"### {lead.get('azienda')} — Score {lead.get('punteggio',0)}")
        c1,c2,c3=st.columns(3); c1.metric("Bilanci disponibili","Sì" if bilanci else "No"); c2.metric("Dati occupazionali","Sì" if occup else "No"); c3.metric("Esito","Da approfondire" if bilanci or occup else "Non disponibile")
        st.caption("La presenza di dati non dimostra un investimento: serve verifica con il referente aziendale.")

def pagina_lookalike():
    st.markdown('<div class="ffe-header"><h1>👥 Analisi Lookalike</h1><p>Confronto interno tra aziende già presenti nel CRM</p></div>',unsafe_allow_html=True)
    df=df_leads()
    if len(df)<2: st.info("Servono almeno 2 lead nel CRM."); return
    seed_id=st.selectbox("Azienda di riferimento",df["id"].tolist(),format_func=lambda x:f"#{x} — {df.loc[df['id']==x,'azienda'].iloc[0]}")
    seed=next(x for x in st.session_state.leads if x.get("id")==seed_id)
    def sim(x):
        score=0
        if seed.get("settore") and x.get("settore")==seed.get("settore"): score+=35
        if seed.get("ateco") and x.get("ateco")==seed.get("ateco"): score+=35
        if seed.get("provincia") and x.get("provincia")==seed.get("provincia"): score+=10
        a=_token_set(seed.get("descrizione_ateco","")+" "+seed.get("profilo_cercato","")); b=_token_set(x.get("descrizione_ateco","")+" "+x.get("profilo_cercato",""))
        if a and b: score+=min(20,len(a&b)*5)
        return score
    rows=[]
    for x in st.session_state.leads:
        if x.get("id")==seed_id: continue
        rows.append({"Azienda":x.get("azienda"),"Lookalike":sim(x),"Settore":x.get("settore"),"ATECO":x.get("ateco"),"Provincia":x.get("provincia")})
    st.dataframe(pd.DataFrame(rows).sort_values("Lookalike",ascending=False),use_container_width=True,hide_index=True)
    st.caption("È un confronto interno al CRM: non dichiara similarità di aziende esterne senza dati verificati.")

def pagina_radar():
    st.markdown('<div class="ffe-header"><h1>🛰️ Radar Espansione & Organico</h1><p>Disponibilità di segnali da InfoCheck utili alla qualificazione</p></div>',unsafe_allow_html=True)
    rows=[]
    for lead in st.session_state.leads:
        info=st.session_state.infocheck_cache.get(lead.get("piva"),{})
        rows.append({"Azienda":lead.get("azienda"),"Score":lead.get("punteggio"),"InfoCheck":bool(info),"Occupazione":bool(info.get("datiOccupazionali")) if isinstance(info,dict) else False,"Bilanci":bool(info.get("bilanci")) if isinstance(info,dict) else False,"Prossima azione":lead.get("prossima_azione")})
    if not rows: st.info("Nessun lead nel CRM."); return
    st.dataframe(pd.DataFrame(rows).sort_values(["InfoCheck","Score"],ascending=[False,False]),use_container_width=True,hide_index=True)
    st.caption("Il radar segnala dati disponibili; non interpreta crescita o investimenti come fatti se il dato non è presente.")

def pagina_sales_twin():
    st.markdown('<div class="ffe-header"><h1>🎯 Sales Twin Verticale</h1><p>Checklist commerciale specifica per il settore</p></div>',unsafe_allow_html=True)
    settore=st.selectbox("Verticale",SETTORI); tecnologia=MAPPA_TECNOLOGIA_SETTORE.get(settore,"Soluzione di estrusione da qualificare")
    st.markdown(f"### {settore}"); st.write(f"**Tecnologia da verificare:** {tecnologia}")
    st.write("**Verificare in chiamata:** prodotto estruso, materiale, geometria/profilo, portata, linea attuale, colli di bottiglia, automazione e piano di investimento.")
    st.write("**Segnali di fit:** produzione interna, estrusione, coestrusione/calibrazione/downstream, retrofit o nuova linea.")
    if st.session_state.leads: st.info(f"Lead disponibili nel CRM: {len(st.session_state.leads)}. Per la singola azienda usa Preparazione al contatto.")

# =========================================================================
# ROUTING
# =========================================================================

def main():
    sidebar()
    p = st.session_state.pagina
    if p == "Dashboard":
        pagina_dashboard()
    elif p == "🏢 Dati Ufficiali Imprese (Abbrevia X)":
        pagina_abbrevia()
    elif p == "🎯 Lead Search — Potenziali Clienti":
        pagina_ricerca_settore()
    elif p == "🎪 Ricerca Fiere":
        pagina_fiere()
    elif p == "📈 Progetti di Investimento":
        pagina_investimenti()
    elif p == "👥 Analisi Lookalike":
        pagina_lookalike()
    elif p == "🛰️ Radar Espansione & Organico":
        pagina_radar()
    elif p == "🎯 Sales Twin Verticale":
        pagina_sales_twin()
    elif p == "📄 Dossier Tecnico AI":
        pagina_dossier()
    elif p == "Valutazione commerciale":
        pagina_sales_intelligence()
    elif p == "✉️ Sequenze Outreach":
        pagina_outreach()
    elif p == "🗂️ CRM & Database Lead":
        pagina_crm()
    else:
        st.info(
            "Questo modulo è presente nel menu ma non è ancora implementato "
            "in questa versione dell'app."
        )


if __name__ == "__main__":
    main()