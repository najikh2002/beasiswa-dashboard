import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os

# Page config
st.set_page_config(
    page_title="Dashboard Beasiswa Indonesia",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .status-buka {
        background-color: #d4edda;
        color: #155724;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
    }
    .status-akan-buka {
        background-color: #fff3cd;
        color: #856404;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
    }
    .status-tutup {
        background-color: #f8d7da;
        color: #721c24;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🎓 Dashboard Timeline Beasiswa Indonesia")
st.markdown("### Master & PhD Scholarship Opportunities")
st.markdown("---")

# Load data
@st.cache_data(ttl=3600)
def load_data():
    try:
        df = pd.read_csv('/app/data/beasiswa_processed.csv')
        df['buka'] = pd.to_datetime(df['buka'])
        df['tutup'] = pd.to_datetime(df['tutup'])
        return df
    except FileNotFoundError:
        st.warning("Data belum tersedia. Menunggu Airflow pipeline berjalan...")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_stats():
    try:
        with open('/app/data/stats.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

df = load_data()
stats = load_stats()

if not df.empty:
    # Sidebar filters
    st.sidebar.header("🔍 Filter")
    
    jenjang_filter = st.sidebar.multiselect(
        "Jenjang Pendidikan",
        options=['Master', 'PhD', 'Master/PhD'],
        default=['Master', 'PhD', 'Master/PhD']
    )
    
    # Filter by jenjang
    if jenjang_filter:
        df_filtered = df[df['jenjang'].isin(jenjang_filter)]
    else:
        df_filtered = df
    
    negara_filter = st.sidebar.multiselect(
        "Negara/Region",
        options=sorted(df['negara'].unique()),
        default=[]
    )
    
    if negara_filter:
        df_filtered = df_filtered[df_filtered['negara'].isin(negara_filter)]
    
    status_filter = st.sidebar.radio(
        "Status Beasiswa",
        options=['Semua', 'Sedang Buka', 'Akan Buka', 'Sudah Tutup'],
        index=0
    )
    
    if status_filter != 'Semua':
        df_filtered = df_filtered[df_filtered['status'].str.contains(status_filter)]
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Beasiswa", len(df_filtered))
    
    with col2:
        sedang_buka = len(df_filtered[df_filtered['status'].str.contains('Sedang Buka')])
        st.metric("Sedang Buka", sedang_buka, delta="Apply Now!", delta_color="normal")
    
    with col3:
        akan_buka = len(df_filtered[df_filtered['status'].str.contains('Akan Buka')])
        st.metric("Akan Buka", akan_buka)
    
    with col4:
        sudah_tutup = len(df_filtered[df_filtered['status'].str.contains('Sudah Tutup')])
        st.metric("Sudah Tutup", sudah_tutup)
    
    st.markdown("---")
    
    # Timeline visualization
    st.subheader("📅 Timeline Beasiswa")
    
    # Prepare data for timeline
    df_timeline = df_filtered.copy()
    df_timeline['Start'] = df_timeline['buka']
    df_timeline['Finish'] = df_timeline['tutup']
    df_timeline['Task'] = df_timeline['nama']
    
    # Assign colors based on status
    color_map = {}
    for idx, row in df_timeline.iterrows():
        if 'Sedang Buka' in row['status']:
            color_map[row['nama']] = '#28a745'
        elif 'Akan Buka' in row['status']:
            color_map[row['nama']] = '#ffc107'
        else:
            color_map[row['nama']] = '#dc3545'
    
    # Create timeline using plotly express
    fig = px.timeline(
        df_timeline,
        x_start='Start',
        x_end='Finish',
        y='Task',
        color='Task',
        color_discrete_map=color_map,
        hover_data={'Task': False, 'Start': '|%d %b %Y', 'Finish': '|%d %b %Y'}
    )

    # Customize hover template
    for i, row in enumerate(df_timeline.itertuples()):
        fig.data[i].hovertemplate = (
            f"<b>{row.nama}</b><br>" +
            f"Jenjang: {row.jenjang}<br>" +
            f"Negara: {row.negara}<br>" +
            f"Buka: {row.buka.strftime('%d %b %Y')}<br>" +
            f"Tutup: {row.tutup.strftime('%d %b %Y')}<br>" +
            f"Status: {row.status}<br>" +
            "<extra></extra>"
        )
    
    # Add today line using shapes (more reliable than add_vline)
    today = datetime.now()
    fig.add_shape(
        type="line",
        x0=today,
        x1=today,
        y0=0,
        y1=1,
        yref="paper",
        line=dict(color="red", width=2, dash="dash")
    )

    # Add annotation for today
    fig.add_annotation(
        x=today,
        y=1,
        yref="paper",
        text="Hari Ini",
        showarrow=False,
        yshift=10,
        font=dict(color="red", size=12)
    )
    
    fig.update_layout(
        height=max(400, len(df_filtered) * 40),
        showlegend=False,
        xaxis_title="Timeline",
        yaxis_title="",
        hovermode='closest',
        xaxis=dict(
            tickformat='%b %Y',
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["🔥 Sedang Buka", "⏰ Akan Buka", "📊 Semua Beasiswa"])
    
    with tab1:
        st.subheader("Beasiswa yang Sedang Buka")
        df_open = df_filtered[df_filtered['status'].str.contains('Sedang Buka')].sort_values('hari_tersisa')
        
        if not df_open.empty:
            for idx, row in df_open.iterrows():
                with st.expander(f"🎓 {row['nama']} - {row['jenjang']} ({row['negara']})"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Deskripsi:** {row['deskripsi']}")
                        st.write(f"**Periode:** {row['buka'].strftime('%d %b %Y')} - {row['tutup'].strftime('%d %b %Y')}")
                        st.write(f"**Sisa Waktu:** {row['hari_tersisa']} hari")
                        st.markdown(f"**Link:** [{row['url']}]({row['url']})")
                    with col2:
                        st.markdown(f"<div class='status-buka'>{row['status']}</div>", unsafe_allow_html=True)
        else:
            st.info("Tidak ada beasiswa yang sedang buka saat ini.")
    
    with tab2:
        st.subheader("Beasiswa yang Akan Buka")
        df_upcoming = df_filtered[df_filtered['status'].str.contains('Akan Buka')].sort_values('hari_tersisa')
        
        if not df_upcoming.empty:
            for idx, row in df_upcoming.iterrows():
                with st.expander(f"🎓 {row['nama']} - {row['jenjang']} ({row['negara']})"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Deskripsi:** {row['deskripsi']}")
                        st.write(f"**Akan Buka:** {row['buka'].strftime('%d %b %Y')}")
                        st.write(f"**Akan Tutup:** {row['tutup'].strftime('%d %b %Y')}")
                        st.write(f"**Buka dalam:** {row['hari_tersisa']} hari")
                        st.markdown(f"**Link:** [{row['url']}]({row['url']})")
                    with col2:
                        st.markdown(f"<div class='status-akan-buka'>{row['status']}</div>", unsafe_allow_html=True)
        else:
            st.info("Tidak ada beasiswa yang akan buka dalam waktu dekat.")
    
    with tab3:
        st.subheader("Daftar Lengkap Beasiswa")
        
        # Display as table
        df_display = df_filtered[['nama', 'jenjang', 'negara', 'buka', 'tutup', 'status']].copy()
        df_display['buka'] = df_display['buka'].dt.strftime('%d %b %Y')
        df_display['tutup'] = df_display['tutup'].dt.strftime('%d %b %Y')
        df_display.columns = ['Nama Beasiswa', 'Jenjang', 'Negara', 'Tanggal Buka', 'Tanggal Tutup', 'Status']
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    # Statistics
    if stats:
        st.markdown("---")
        st.caption(f"Last updated: {pd.to_datetime(stats['last_update']).strftime('%d %B %Y, %H:%M')} WIB")

else:
    st.info("⏳ Menunggu data dari Airflow pipeline. Pastikan DAG 'beasiswa_scraper' sudah berjalan.")
    st.markdown("""
    ### Cara Menjalankan:
    1. Pastikan semua container Docker sudah running
    2. Akses Airflow di http://localhost:8080 (user: admin, pass: admin)
    3. Aktifkan dan trigger DAG 'beasiswa_scraper'
    4. Refresh dashboard ini setelah DAG selesai
    """)

# Sidebar info
st.sidebar.markdown("---")
st.sidebar.info("""
    **About:**
    Dashboard ini menampilkan timeline beasiswa 
    Master & PhD untuk Indonesia.
    
    Data diupdate otomatis setiap hari oleh 
    Apache Airflow.
""")

st.sidebar.markdown("---")
st.sidebar.markdown("Made with ❤️ using Streamlit")