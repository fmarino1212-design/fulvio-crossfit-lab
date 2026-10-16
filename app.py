import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Fulvio CF Performance Lab Pro", page_icon="🏋️‍♂️", layout="wide"
)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1rPEext5mowZCqOdmJ7s4CHvq-SRbw-cgJI4ha08Z0Us"
SESSIONI_CSV = f"{SHEET_URL}/gviz/tq?tqx=out:csv&sheet=Sessioni"
PRS_CSV = f"{SHEET_URL}/gviz/tq?tqx=out:csv&sheet=PRs_Benchmark"


@st.cache_data(ttl=10)
def load_data():
  df_s = pd.read_csv(SESSIONI_CSV)
  df_p = pd.read_csv(PRS_CSV)

  # Pulizia e conversioni tipi
  df_s["Data"] = pd.to_datetime(df_s["Data"]).dt.strftime("%Y-%m-%d")
  df_s["FC_Media"] = pd.to_numeric(df_s["FC_Media"], errors="coerce")
  df_s["Drop_FC"] = pd.to_numeric(df_s["Drop_FC"], errors="coerce")
  df_s["Z5_sec"] = pd.to_numeric(df_s["Z5_sec"], errors="coerce")
  df_s["Kcal"] = pd.to_numeric(df_s["Kcal"], errors="coerce")
  df_s["Voto_Tecnico"] = pd.to_numeric(df_s["Voto_Tecnico"], errors="coerce")

  df_p["Data"] = pd.to_datetime(df_p["Data"]).dt.strftime("%Y-%m-%d")
  df_p["Carico_Valore"] = pd.to_numeric(
      df_p["Valore_Score"].astype(str).str.extract(r"(\d+)")[0], errors="coerce"
  )

  return df_s, df_p


# Header Principale
st.title("🏋️‍♂️ Fulvio CF Pro Analytics")
st.caption(
    "Cloud Sync Google Sheets • Telemetria Polar • Road to Donkey Challenge"
    " 2026"
)

c_top1, c_top2 = st.columns([4, 1])
with c_top2:
  if st.button("🔄 Sincronizza Cloud Ora", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

try:
  df_s, df_p = load_data()

  # KPI in evidenza
  clean_max = df_p[df_p["Esercizio_WOD"] == "Clean"]["Carico_Valore"].max()
  cj_max = df_p[df_p["Esercizio_WOD"] == "Clean & Jerk"]["Carico_Valore"].max()
  best_drop = df_s["Drop_FC"].min()
  avg_vote = df_s["Voto_Tecnico"].mean()

  k1, k2, k3, k4, k5 = st.columns(5)
  k1.metric("PR Clean", f"{int(clean_max)} kg", "08/10/2026")
  k2.metric("PR Clean & Jerk", f"{int(cj_max)} kg", "3 Cifre Split")
  k3.metric(
      "Miglior Drop Post-WOD",
      f"{int(best_drop)} bpm",
      "WOD 4 (Top Recupero)",
      delta_color="inverse",
  )
  k4.metric("Media Voto Tecnico", f"{avg_vote:.1f} / 10")
  k5.metric("Donkey WOD 4", "06:06 RX", "-1'54\" dal Cap 8'")

  st.divider()

  # Sezioni Principali
  t_pr, t_cardio, t_best, t_comp, t_log = st.tabs([
      "📈 Progressione PRs & Date",
      "🫀 Statistiche Cardio & Freno Parasimpatico",
      "⭐ Hall of Fame (Top Allenamenti)",
      "⚔️ Confronto WOD Simili",
      "📋 Storico Completo",
  ])

  # --- 1. PROGRESSIONE PRS CON DATE ---
  with t_pr:
    st.subheader("📈 Analisi Temporale dei Carichi & Massimali")
    wl_exercises = (
        df_p[df_p["Categoria"] != "Benchmark Gara"]["Esercizio_WOD"]
        .unique()
        .tolist()
    )

    c_sel1, c_sel2 = st.columns([1, 2])
    with c_sel1:
      selected_move = st.selectbox(
          "Seleziona Movimento da analizzare:",
          wl_exercises,
          index=wl_exercises.index("Clean") if "Clean" in wl_exercises else 0,
      )
      df_move = df_p[df_p["Esercizio_WOD"] == selected_move].sort_values("Data")
      curr_pr = df_move["Carico_Valore"].max()
      first_pr = df_move["Carico_Valore"].iloc[0]
      diff = curr_pr - first_pr
      st.metric(
          f"Massimale Attuale {selected_move}",
          f"{int(curr_pr)} kg",
          f"+{int(diff)} kg storici",
      )
      st.dataframe(
          df_move[["Data", "Valore_Score", "Dettagli_Note"]],
          use_container_width=True,
          hide_index=True,
      )

    with c_sel2:
      fig_pr = px.line(
          df_move,
          x="Data",
          y="Carico_Valore",
          markers=True,
          text="Carico_Valore",
          title=f"Trend Storico: {selected_move} (kg nel tempo)",
      )
      fig_pr.update_traces(
          line_color="#f59e0b",
          line_width=3,
          marker_size=10,
          textposition="top center",
      )
      fig_pr.update_layout(
          template="plotly_dark", height=380, yaxis_title="Carico (kg)"
      )
      st.plotly_chart(fig_pr, use_container_width=True)

  # --- 2. STATISTICHE CARDIO, RECUPERO E CALORIE ---
  with t_cardio:
    st.subheader("🫀 Frequenza Cardiaca, Freno Parasimpatico e Intensità")

    sc1, sc2, sc3, sc4 = st.columns(4)
    sc1.metric("FC Media Globale", f"{int(df_s['FC_Media'].mean())} bpm")
    sc2.metric("Drop Medio Post-WOD", f"{int(df_s['Drop_FC'].mean())} bpm")
    sc3.metric("Tempo Medio Z5 / Seduta", f"{int(df_s['Z5_sec'].mean())} sec")
    sc4.metric("Calorie Medie", f"{int(df_s['Kcal'].mean())} kcal")

    c_g1, c_g2 = st.columns(2)
    with c_g1:
      fig_hr = go.Figure()
      fig_hr.add_trace(
          go.Scatter(
              x=df_s["Data"],
              y=df_s["FC_Media"],
              mode="lines+markers",
              name="FC Media (bpm)",
              line=dict(color="#ef4444", width=3),
          )
      )
      fig_hr.add_trace(
          go.Scatter(
              x=df_s["Data"],
              y=df_s["Drop_FC"],
              mode="lines+markers",
              name="Drop Finale (bpm)",
              line=dict(color="#22c55e", width=3),
          )
      )
      fig_hr.add_hline(
          y=80,
          line_dash="dash",
          line_color="#94a3b8",
          annotation_text="Target Recupero Ottimale (< 80 bpm)",
      )
      fig_hr.update_layout(
          title="FC Media vs Freno Parasimpatico (Drop Finale)",
          template="plotly_dark",
          height=360,
      )
      st.plotly_chart(fig_hr, use_container_width=True)

    with c_g2:
      fig_burn = go.Figure()
      fig_burn.add_trace(
          go.Bar(
              x=df_s["Data"],
              y=df_s["Z5_sec"],
              name="Secondi in Z5 (Max)",
              marker_color="#f97316",
          )
      )
      fig_burn.add_trace(
          go.Scatter(
              x=df_s["Data"],
              y=df_s["Kcal"],
              mode="lines+markers",
              name="Calorie Bruciate (kcal)",
              line=dict(color="#38bdf8", width=3),
              yaxis="y2",
          )
      )
      fig_burn.update_layout(
          title="Secondi in Zona 5 vs Dispendio Calorico",
          template="plotly_dark",
          height=360,
          yaxis=dict(title="Secondi in Z5"),
          yaxis2=dict(
              title="Calorie (kcal)", overlaying="y", side="right", showgrid=False
          ),
      )
      st.plotly_chart(fig_burn, use_container_width=True)

  # --- 3. HALL OF FAME: TOP ALLENAMENTI ---
  with t_best:
    st.subheader("⭐ Hall of Fame: I Migliori Workout Affrontati")
    st.caption(
        "I workout con il voto tecnico più alto, i migliori benchmark di gara e"
        " la risposta cardiaca più efficiente."
    )

    top_wods = df_s.sort_values(
        by=["Voto_Tecnico", "Drop_FC"], ascending=[False, True]
    ).head(4)
    for idx, row in top_wods.iterrows():
      with st.expander(
          f"🏆 {row['Data']} - {row['Focus']} (Voto: {row['Voto_Tecnico']}/10)",
          expanded=True,
      ):
        c_h1, c_h2, c_h3, c_h4 = st.columns(4)
        c_h1.write(f"**Score:** {row['Volume_Score']}")
        c_h2.write(f"**Carichi:** {row['Carichi']}")
        c_h3.write(
            f"**Cardio:** FC Med {int(row['FC_Media'])} bpm | Drop"
            f" {int(row['Drop_FC'])} bpm"
        )
        c_h4.write(f"**Zona 5:** {row['Tempo_Z5']} | {int(row['Kcal'])} kcal")
        st.info(f"💡 **Note Tecniche:** {row['Note']}")

  # --- 4. CONFRONTO DIRETTO WOD SIMILI ---
  with t_comp:
    st.subheader("⚔️ Confronto Diretto tra Workout")
    st.caption(
        "Seleziona due sessioni dallo storico per confrontare telemetria,"
        " carichi e ritmo."
    )

    col_w1, col_w2 = st.columns(2)
    with col_w1:
      w1_date = st.selectbox(
          "Seleziona Workout A:",
          df_s["Data"].tolist(),
          index=len(df_s) - 2 if len(df_s) >= 2 else 0,
          key="w1",
      )
      w1 = df_s[df_s["Data"] == w1_date].iloc[0]
      st.markdown(f"### 🔵 Workout A: {w1['Data']}")
      st.write(f"**Focus:** {w1['Focus']}")
      st.write(f"**Carichi:** {w1['Carichi']}")
      st.write(f"**Score:** {w1['Volume_Score']}")
      st.metric("FC Media", f"{int(w1['FC_Media'])} bpm")
      st.metric(
          "Drop Finale", f"{int(w1['Drop_FC'])} bpm", delta_color="inverse"
      )
      st.metric("Tempo Zona 5", f"{w1['Tempo_Z5']}")
      st.metric("Calorie", f"{int(w1['Kcal'])} kcal")
      st.write(f"**Voto Tecnico:** {w1['Voto_Tecnico']}/10")
      st.caption(f"Note: {w1['Note']}")

    with col_w2:
      w2_date = st.selectbox(
          "Seleziona Workout B:",
          df_s["Data"].tolist(),
          index=len(df_s) - 1,
          key="w2",
      )
      w2 = df_s[df_s["Data"] == w2_date].iloc[0]
      st.markdown(f"### 🔴 Workout B: {w2['Data']}")
      st.write(f"**Focus:** {w2['Focus']}")
      st.write(f"**Carichi:** {w2['Carichi']}")
      st.write(f"**Score:** {w2['Volume_Score']}")
      st.metric(
          "FC Media",
          f"{int(w2['FC_Media'])} bpm",
          f"{int(w2['FC_Media'] - w1['FC_Media'])} vs A",
          delta_color="inverse",
      )
      st.metric(
          "Drop Finale",
          f"{int(w2['Drop_FC'])} bpm",
          f"{int(w2['Drop_FC'] - w1['Drop_FC'])} vs A",
          delta_color="inverse",
      )
      st.metric("Tempo Zona 5", f"{w2['Tempo_Z5']}")
      st.metric(
          "Calorie",
          f"{int(w2['Kcal'])} kcal",
          f"{int(w2['Kcal'] - w1['Kcal'])} vs A",
      )
      st.write(f"**Voto Tecnico:** {w2['Voto_Tecnico']}/10")
      st.caption(f"Note: {w2['Note']}")

  # --- 5. TABELLA COMPLETA ---
  with t_log:
    st.subheader("📋 Storico Completo Sessioni")
    st.dataframe(df_s, use_container_width=True, hide_index=True)
    st.markdown(
        f"👉 [Apri il Google Sheet Diretto su Google Drive]({SHEET_URL})"
    )

except Exception as e:
  st.warning(
      "⚠️ Impossibile caricare i dati. Assicurati che il Google Sheet sia"
      " condiviso come 'Chiunque abbia il link -> Visualizzatore'."
  )
  st.error(f"Dettaglio: {e}")