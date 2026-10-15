import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Fulvio CF Performance Lab", page_icon="🏋️‍♂️", layout="wide"
)

# Link diretto al tuo Google Sheet su Drive
SHEET_URL = "https://docs.google.com/spreadsheets/d/1rPEext5mowZCqOdmJ7s4CHvq-SRbw-cgJI4ha08Z0Us"
SESSIONI_CSV = f"{SHEET_URL}/gviz/tq?tqx=out:csv&sheet=Sessioni"
PRS_CSV = f"{SHEET_URL}/gviz/tq?tqx=out:csv&sheet=PRs_Benchmark"


@st.cache_data(ttl=15)  # Si aggiorna ogni 15 secondi dal Cloud
def load_cloud_data():
  df_sess = pd.read_csv(SESSIONI_CSV)
  df_prs = pd.read_csv(PRS_CSV)
  return df_sess, df_prs


st.title("🏋️‍♂️ Fulvio CrossFit & Performance Lab")
st.caption(
    "Sincronizzato in Cloud con Google Sheets • Road to Donkey Challenge 2026"
)

if st.button("🔄 Sincronizza Dati Ora"):
  st.cache_data.clear()
  st.rerun()

try:
  df, df_prs = load_cloud_data()

  # Assicura che i campi numerici siano letti correttamente
  df["FC_Media"] = pd.to_numeric(df["FC_Media"], errors="coerce")
  df["Drop_FC"] = pd.to_numeric(df["Drop_FC"], errors="coerce")
  df["Z5_sec"] = pd.to_numeric(df["Z5_sec"], errors="coerce")
  df["Kcal"] = pd.to_numeric(df["Kcal"], errors="coerce")
  df["Voto_Tecnico"] = pd.to_numeric(df["Voto_Tecnico"], errors="coerce")

  # --- KPI IN ALTO ---
  c1, c2, c3, c4, c5 = st.columns(5)
  c1.metric("PR Clean", "106 kg", "08/10/2026")
  c2.metric("PR Clean & Jerk", "100 kg", "Split")
  c3.metric(
      "Media Drop FC",
      f"{int(df['Drop_FC'].mean())} bpm",
      "Target < 80 bpm",
      delta_color="inverse",
  )
  c4.metric("Media Voto Tecnico", f"{df['Voto_Tecnico'].mean():.1f} / 10")
  c5.metric("Donkey WOD 1", "4'42\" RX", "-1'18\" dal Cap")

  st.divider()

  tab1, tab2, tab3 = st.tabs([
      "📊 Grafici & Telemetria",
      "📋 Storico Sessioni",
      "🏆 PRs & Benchmark Gara",
  ])

  with tab1:
    col_g1, col_g2 = st.columns(2)
    with col_g1:
      st.subheader("❤️ FC Media vs Freno Parasimpatico (Drop Post-WOD)")
      fig_hr = go.Figure()
      fig_hr.add_trace(
          go.Scatter(
              x=df["Data"],
              y=df["FC_Media"],
              mode="lines+markers",
              name="FC Media (bpm)",
              line=dict(color="#ef4444", width=3),
          )
      )
      fig_hr.add_trace(
          go.Scatter(
              x=df["Data"],
              y=df["Drop_FC"],
              mode="lines+markers",
              name="Drop Post-WOD (bpm)",
              line=dict(color="#22c55e", width=3),
          )
      )
      fig_hr.add_hline(
          y=80,
          line_dash="dash",
          line_color="#94a3b8",
          annotation_text="Soglia Recupero Ottimale (80 bpm)",
      )
      fig_hr.update_layout(
          template="plotly_dark",
          height=360,
          margin=dict(l=20, r=20, t=30, b=20),
      )
      st.plotly_chart(fig_hr, use_container_width=True)

    with col_g2:
      st.subheader("🔥 Secondi in Zona 5 (Max) & Dispendo Calorico")
      fig_z5 = go.Figure()
      fig_z5.add_trace(
          go.Bar(
              x=df["Data"],
              y=df["Z5_sec"],
              name="Secondi in Z5",
              marker_color="#f97316",
          )
      )
      fig_z5.add_trace(
          go.Scatter(
              x=df["Data"],
              y=df["Kcal"],
              mode="lines+markers",
              name="Calorie (kcal)",
              line=dict(color="#38bdf8", width=3),
          )
      )
      fig_z5.update_layout(
          template="plotly_dark",
          height=360,
          margin=dict(l=20, r=20, t=30, b=20),
      )
      st.plotly_chart(fig_z5, use_container_width=True)

  with tab2:
    st.subheader("📋 Database Sessioni Completo")
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown(f"👉 [Apri o modifica il Google Sheet su Drive]({SHEET_URL})")

  with tab3:
    st.subheader("🏆 Massimali & Benchmark Ufficiali")
    st.dataframe(df_prs, use_container_width=True, hide_index=True)

except Exception as e:
  st.warning(
      "⚠️ Assicurati di aver impostato la condivisione del Google Sheet su"
      " 'Chiunque abbia il link -> Visualizzatore'."
  )
  st.error(f"Dettaglio: {e}")