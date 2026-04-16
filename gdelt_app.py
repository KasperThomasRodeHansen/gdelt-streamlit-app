import os
import streamlit as st
import pandas as pd
import json
from google.cloud import bigquery

if "GOOGLE_APPLICATION_CREDENTIALS_JSON" in st.secrets:
    creds_dict = json.loads(st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
    with open("/tmp/credentials.json", "w") as f:
        json.dump(creds_dict, f)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/credentials.json"
else:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
        "/Users/kasperhansen/Desktop/Gdelt/Json/keen-diode-493214-v8-d8b69dbc0a80.json"
    )

client = bigquery.Client(project="keen-diode-493214-v8")

st.set_page_config(page_title="GDELT Økonomisk Politik", page_icon="📊")
st.title("GDELT - Økonomisk Politik Monitor")

st.sidebar.header("Indstillinger")
emne_filter = st.sidebar.multiselect(
    "Vælg emner",
    [
        "ECON_INFLATION",
        "ECON_INTEREST_RATES",
        "ECON_TAXATION",
        "ECON_BUDGET",
        "ECON_FISCAL",
        "ECON_MONETARY",
        "ECON_TRADE",
        "ECON_TRADE_DISPUTE",
    ],
    default=["ECON_INFLATION", "ECON_TAXATION", "ECON_BUDGET"],
)

dage = st.sidebar.slider("Antal dage tilbage", 1, 30, 7)

if st.sidebar.button("🔄 Opdater Data"):
    st.rerun()

st.header("📰 Økonomisk Politik - Artikler")
st.caption(
    f"📅 Seneste {dage} dage | Opdateret: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}"
)

with st.spinner("Henter data..."):
    theme_filter = " OR ".join([f"V2Themes LIKE '%{e}%'" for e in emne_filter])

    query = f"""
    WITH parsed AS (
      SELECT 
        SPLIT(SPLIT(V2Locations, ';')[OFFSET(0)], '#')[OFFSET(1)] as Land,
        SPLIT(TRIM(SPLIT(V2Themes, ';')[OFFSET(0)]), ',')[OFFSET(0)] as Emne,
        SPLIT(V2Persons, ';')[OFFSET(0)] as Person,
        SPLIT(V2Organizations, ';')[OFFSET(0)] as Organisation,
        DocumentIdentifier,
        DATE as Dato
      FROM `gdelt-bq.gdeltv2.gkg_partitioned`
      WHERE _PARTITIONDATE >= DATE_SUB(CURRENT_DATE(), INTERVAL {dage} DAY)
        AND ({theme_filter})
        AND V2Locations IS NOT NULL
    )
    SELECT 
        Dato,
        Land,
        Emne,
        Person,
        Organisation,
        COUNT(DISTINCT DocumentIdentifier) as Antal_Artikler
    FROM parsed
    WHERE Land IS NOT NULL AND Land != ''
    GROUP BY Dato, Land, Emne, Person, Organisation
    ORDER BY Dato DESC, Antal_Artikler DESC
    LIMIT 100
    """

    df = client.query(query).to_dataframe(create_bqstorage_client=False)
    st.dataframe(df, use_container_width=True)
    st.success(f"Fandt {len(df)} rækker")

st.header("🌍 Seneste Begivenheder (Events)")
st.caption(
    f"📅 Seneste {dage} dage | Opdateret: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}"
)

with st.spinner("Henter events..."):
    cameo_codes = {
        "010": "Besøg",
        "011": "Møde",
        "012": "Telefonsamtale",
        "020": "Gave/Donation",
        "021": "Humanitær hjælp",
        "030": "Moral/Ære",
        "031": "Ros",
        "032": "Støtte",
        "040": "Anmodning",
        "043": "Økonomisk erklæring",
        "044": "Politiske løfter",
        "050": "Træning",
        "060": "Forhandling",
        "061": "Fredsforhandling",
        "070": "Officielt besøg",
        "080": "Kooperativ produktion",
        "090": "Eksplicit reduktion",
        "100": "Mindre skænderi",
        "101": "Trussel",
        "102": "Protest",
        "110": "Demonstration",
        "120": "Mindre konflikter",
        "121": "Vold",
        "130": "Alvorlig konflikt",
        "140": "Fængsling",
        "150": "Udvikling",
        "160": "Undgå",
        "170": "Retlig handling",
        "180": "Sanctionering",
        "181": "Boykot",
        "182": "Handelsrestriktioner",
    }

    query_events = f"""
    SELECT 
        Day as Dato,
        Actor1CountryCode as Land1,
        Actor2CountryCode as Land2,
        EventCode,
        SUM(CAST(NumMentions AS INT64)) as Samlet_Mentions,
        COUNT(*) as Antal_Begivenheder
    FROM `gdelt-bq.gdeltv2.events_partitioned`
    WHERE _PARTITIONDATE >= DATE_SUB(CURRENT_DATE(), INTERVAL {dage} DAY)
      AND Actor1CountryCode IS NOT NULL
    GROUP BY Day, Actor1CountryCode, Actor2CountryCode, EventCode
    ORDER BY Dato DESC, Samlet_Mentions DESC
    LIMIT 50
    """

    df_events = client.query(query_events).to_dataframe(create_bqstorage_client=False)
    df_events["Begivenhed"] = df_events["EventCode"].map(cameo_codes).fillna("Andet")
    st.dataframe(
        df_events[
            [
                "Dato",
                "Land1",
                "Land2",
                "Begivenhed",
                "Samlet_Mentions",
                "Antal_Begivenheder",
            ]
        ],
        use_container_width=True,
    )
