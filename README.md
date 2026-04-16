# GDELT Økonomisk Politik Monitor

En Streamlit app der visualiserer GDELT data om økonomisk politik og globale begivenheder.

## Installation

```bash
pip install -r requirements.txt
```

## Lokal kørsel

```bash
streamlit run gdelt_app.py
```

## Deployment til Streamlit Cloud

1. **Push til GitHub:**
   - Opret et nyt repo på GitHub
   - Push alle filer (undtagen `.json` credentials-filer)

2. **Deploy på Streamlit Cloud:**
   - Gå til [share.streamlit.io](https://share.streamlit.io)
   - Login med GitHub
   - "New app" → vælg dit repo og `gdelt_app.py`
   - Under "Secrets" tilføj din JSON credentials som en secret

3. **Secrets konfiguration i Streamlit Cloud:**
   ```
   [gcp_service_account]
   credentials_path = "KEEN-DIODE-493214-V8-959E0B8E9BDD.json"
   ```
   Upload din `keen-diode-493214-v8-959e0b8e9bdd.json` fil under "Files" i app settings.
