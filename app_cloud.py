import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json

st.set_page_config(
    page_title="Dashboard GGJ Arequipa 2026",
    page_icon="🎮",
    layout="wide"
)

st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #f5e6d3 0%, #d4e7e5 50%, #a8c9c3 100%);
    }
    
    .stApp {
        background: transparent;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a3a52;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .welcome-card {
        background: linear-gradient(135deg, #f5c5c5 0%, #f5a5a5 100%);
        padding: 3rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
    
    .welcome-title {
        font-size: 1.2rem;
        color: #1a3a52;
        margin-bottom: 0.5rem;
    }
    
    .welcome-name {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a3a52;
        margin-bottom: 1rem;
    }
    
    .location-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.6);
        padding: 0.5rem 1.5rem;
        border-radius: 20px;
        font-size: 0.9rem;
        color: #1a3a52;
    }
    
    .alert-critical {
        background: #fee2e2;
        border-left: 4px solid #ef4444;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    
    .alert-warning {
        background: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    
    .alert-success {
        background: #d1fae5;
        border-left: 4px solid #10b981;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    
    .insight-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin-bottom: 1rem;
    }
    
    .insight-title {
        font-size: 1rem;
        font-weight: 600;
        color: #1a3a52;
        margin-bottom: 1rem;
    }
    
    .recommendation-urgent {
        background: #fee2e2;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        display: flex;
        gap: 1rem;
    }
    
    .recommendation-important {
        background: #fef3c7;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        display: flex;
        gap: 1rem;
    }
    
    .recommendation-info {
        background: #dbeafe;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        display: flex;
        gap: 1rem;
    }
    
    .badge-urgent {
        background: #ef4444;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
    }
    
    .badge-important {
        background: #f59e0b;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
    }
    
    .badge-info {
        background: #3b82f6;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="welcome-card">
    <div class="welcome-title">Dashboard de Inscripciones</div>
    <div class="welcome-name">Global Game Jam Arequipa 2026</div>
    <div class="location-badge">Arequipa, Perú</div>
</div>
""", unsafe_allow_html=True)

@st.cache_data
def load_processed_data():
    df = pd.read_csv("data/processed_data.csv")
    with open("data/insights.json", 'r', encoding='utf-8') as f:
        insights = json.load(f)
    return df, insights

try:
    df, insights = load_processed_data()
    
    st.markdown("## Resumen General")
    
    kpis = insights['kpis']
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Inscritos", int(kpis['total_inscritos']))
    
    with col2:
        st.metric("Edad Promedio", f"{kpis['edad_promedio']:.1f} años")
    
    with col3:
        st.metric("Con Portafolio", f"{kpis['porcentaje_portafolio']:.0f}%")
    
    st.markdown("---")
    
    st.markdown("## Alertas de Roles")
    
    alerts = insights['alerts']
    
    if alerts:
        alertas_criticas = [a for a in alerts if a['nivel'] == 'CRÍTICO']
        alertas_bajas = [a for a in alerts if a['nivel'] == 'BAJO']
        
        col1, col2 = st.columns(2)
        
        with col1:
            if alertas_criticas:
                for alert in alertas_criticas:
                    st.markdown(f"""
                    <div class="alert-critical">
                        <strong>{alert['nivel']}</strong><br>
                        {alert['mensaje']}
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            if alertas_bajas:
                for alert in alertas_bajas:
                    st.markdown(f"""
                    <div class="alert-warning">
                        <strong>{alert['nivel']}</strong><br>
                        {alert['mensaje']}
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-success">
            <strong>Todo en orden</strong><br>
            No hay déficit crítico de roles
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("## Análisis de Inscripciones")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Roles - 1era Prioridad")
        roles_dist = df['rol_1era_prioridad'].value_counts()
        
        colors = ['#ef4444' if v <= 3 else '#f59e0b' if v <= 5 else '#10b981' 
                  for v in roles_dist.values]
        
        fig_roles = go.Figure(go.Bar(
            x=roles_dist.values,
            y=roles_dist.index,
            orientation='h',
            marker_color=colors,
            text=roles_dist.values,
            textposition='outside'
        ))
        fig_roles.update_layout(
            showlegend=False, 
            height=400,
            xaxis_title="Cantidad",
            yaxis_title="",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_roles, use_container_width=True)
    
    with col2:
        st.subheader("Nivel de Experiencia (1-5)")
        exp_counts = df['categoria_experiencia'].value_counts()
        orden_exp = ['1', '2', '3', '4', '5']
        exp_ordenado = exp_counts.reindex(orden_exp, fill_value=0)
        
        fig_exp = px.bar(
            x=exp_ordenado.index,
            y=exp_ordenado.values,
            labels={'x': 'Nivel', 'y': 'Cantidad'},
            color=exp_ordenado.values,
            color_continuous_scale='RdYlGn'
        )
        fig_exp.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        st.plotly_chart(fig_exp, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Distribución de Edades")
        orden = ["< 20", "20-24", "25-29", "30+"]
        edad_dist = df['grupo_edad'].value_counts().reindex(orden, fill_value=0)
        fig_edad = px.bar(
            x=edad_dist.index,
            y=edad_dist.values,
            labels={'x': 'Grupo de Edad', 'y': 'Cantidad'},
            color=edad_dist.values,
            color_continuous_scale='Blues'
        )
        fig_edad.update_layout(
            showlegend=False, 
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_edad, use_container_width=True)
    
    with col4:
        st.subheader("Motivaciones")
        motiv_dist = df['categoria_motivacion'].value_counts()
        fig_motiv = px.pie(
            values=motiv_dist.values,
            names=motiv_dist.index,
            color_discrete_sequence=px.colors.sequential.Greens_r
        )
        fig_motiv.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_motiv, use_container_width=True)
    
    st.markdown("---")
    
    col5, col6 = st.columns(2)
    
    with col5:
        st.subheader("Nivel de Compromiso")
        orden_comp = ["Alto", "Medio", "Bajo"]
        comp_dist = df['compromiso'].value_counts().reindex(orden_comp, fill_value=0)
        
        colors_comp = {'Alto': '#10b981', 'Medio': '#f59e0b', 'Bajo': '#ef4444'}
        fig_comp = go.Figure(go.Bar(
            x=comp_dist.index,
            y=comp_dist.values,
            marker_color=[colors_comp.get(x, '#95a5a6') for x in comp_dist.index],
            text=comp_dist.values,
            textposition='outside'
        ))
        fig_comp.update_layout(
            showlegend=False,
            height=400,
            xaxis_title="",
            yaxis_title="Cantidad",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_comp, use_container_width=True)
    
    with col6:
        st.subheader("Skills Técnicas Mencionadas")
        all_skills = []
        for skills_str in df['skills'].dropna():
            if isinstance(skills_str, str) and skills_str.startswith('['):
                try:
                    skills_list = eval(skills_str)
                    if isinstance(skills_list, list):
                        all_skills.extend(skills_list)
                except:
                    pass
        
        if all_skills:
            skills_series = pd.Series(all_skills)
            skills_dist = skills_series.value_counts().head(10)
            
            fig_skills = px.bar(
                x=skills_dist.values,
                y=skills_dist.index,
                orientation='h',
                labels={'x': 'Menciones', 'y': ''},
                color=skills_dist.values,
                color_continuous_scale='Oranges'
            )
            fig_skills.update_layout(
                showlegend=False, 
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_skills, use_container_width=True)
        else:
            st.info("No se encontraron skills técnicas mencionadas explícitamente en las respuestas.")
    
    st.markdown("---")
    
    st.markdown("## Insights y Análisis")
    
    perfil = insights['perfil']
    portafolio_analysis = insights['portafolio_analysis']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="insight-card">
            <div class="insight-title">Perfil de Participantes</div>
        """, unsafe_allow_html=True)
        st.write(f"Nivel 1-2 (declarado): **{perfil['porcentaje_principiantes']:.1f}%**")
        st.write(f"Principiantes (análisis): **{perfil['porcentaje_principiantes_real']:.1f}%**")
        st.write(f"Con experiencia en jams: **{perfil['porcentaje_con_jams_previas']:.1f}%**")
        st.write(f"Promedio de jams: **{perfil['promedio_jams']:.1f}**")
        st.write(f"Alto compromiso: **{perfil['compromiso_alto']:.1f}%**")
        st.write(f"Con proyectos: **{perfil['tiene_proyectos_pct']:.1f}%**")
        st.write(f"Motivación principal: **{perfil['motivacion_principal']}**")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="insight-card">
            <div class="insight-title">Top Skills Mencionadas</div>
        """, unsafe_allow_html=True)
        if perfil['top_skills']:
            for skill, count in perfil['top_skills'].items():
                st.write(f"• {skill}: {count} menciones")
        else:
            st.write("No se encontraron skills mencionadas")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="insight-card">
            <div class="insight-title">Análisis de Portafolios</div>
        """, unsafe_allow_html=True)
        st.write(f"Total con portafolio: **{portafolio_analysis['total_con_portafolio']}** ({portafolio_analysis['porcentaje']:.1f}%)")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("## Recomendaciones Accionables")
    
    recomendaciones = insights['recomendaciones']
    
    for rec in recomendaciones:
        tipo = rec['tipo']
        mensaje = rec['mensaje']
        
        if tipo == "URGENTE":
            st.markdown(f"""
            <div class="recommendation-urgent">
                <span class="badge-urgent">{tipo}</span>
                <span>{mensaje}</span>
            </div>
            """, unsafe_allow_html=True)
        elif tipo == "IMPORTANTE":
            st.markdown(f"""
            <div class="recommendation-important">
                <span class="badge-important">{tipo}</span>
                <span>{mensaje}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="recommendation-info">
                <span class="badge-info">{tipo}</span>
                <span>{mensaje}</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("Dashboard con análisis precalculado de Llama 3.2")

except FileNotFoundError as e:
    st.error(f"No se encontraron los archivos procesados: {str(e)}")
except Exception as e:
    st.error(f"Error al cargar los datos: {str(e)}")
    
    import traceback
    with st.expander("Ver detalles del error"):
        st.code(traceback.format_exc())