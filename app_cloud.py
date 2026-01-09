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

st.title("Dashboard Global Game Jam Arequipa 2026")
st.markdown("---")

@st.cache_data
def load_processed_data():
    df = pd.read_csv("data/processed_data.csv")
    with open("data/insights.json", 'r', encoding='utf-8') as f:
        insights = json.load(f)
    return df, insights

try:
    df, insights = load_processed_data()
    
    st.header("Resumen General")
    
    kpis = insights['kpis']
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Inscritos", int(kpis['total_inscritos']))
    
    with col2:
        st.metric("Edad Promedio", f"{kpis['edad_promedio']:.1f} años")
    
    with col3:
        st.metric("% con Portafolio", f"{kpis['porcentaje_portafolio']:.1f}%")
    
    st.markdown("---")
    
    st.header("Alertas de Roles")
    
    alerts = insights['alerts']
    
    if alerts:
        alertas_criticas = [a for a in alerts if a['nivel'] == 'CRÍTICO']
        alertas_bajas = [a for a in alerts if a['nivel'] == 'BAJO']
        
        col1, col2 = st.columns(2)
        
        with col1:
            if alertas_criticas:
                st.error("**ALERTAS CRÍTICAS**")
                for alert in alertas_criticas:
                    st.write(alert['mensaje'])
        
        with col2:
            if alertas_bajas:
                st.warning("**ALERTAS DE ATENCIÓN**")
                for alert in alertas_bajas:
                    st.write(alert['mensaje'])
    else:
        st.success("No hay déficit crítico de roles")
    
    st.markdown("---")
    
    st.header("Análisis de Inscripciones")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Roles - 1era Prioridad")
        roles_dist = df['rol_1era_prioridad'].value_counts()
        
        colors = ['#e74c3c' if v <= 3 else '#f39c12' if v <= 5 else '#27ae60' 
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
            yaxis_title="Rol"
        )
        st.plotly_chart(fig_roles, use_container_width=True)
    
    with col2:
        st.subheader("Nivel de Experiencia")
        exp_dist = df['categoria_experiencia'].value_counts()
        fig_exp = px.pie(
            values=exp_dist.values,
            names=exp_dist.index,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig_exp.update_layout(height=400)
        st.plotly_chart(fig_exp, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Distribución de Edades")
        orden = ["< 20", "20-24", "25-29", "30+", "No especificado"]
        edad_dist = df['grupo_edad'].value_counts().reindex(orden, fill_value=0)
        fig_edad = px.bar(
            x=edad_dist.index,
            y=edad_dist.values,
            labels={'x': 'Grupo de Edad', 'y': 'Cantidad'},
            color=edad_dist.values,
            color_continuous_scale='Blues'
        )
        fig_edad.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_edad, use_container_width=True)
    
    with col4:
        st.subheader("Motivaciones")
        motiv_dist = df['categoria_motivacion'].value_counts()
        fig_motiv = px.pie(
            values=motiv_dist.values,
            names=motiv_dist.index,
            color_discrete_sequence=px.colors.sequential.Greens_r
        )
        fig_motiv.update_layout(height=400)
        st.plotly_chart(fig_motiv, use_container_width=True)
    
    st.markdown("---")
    
    col5, col6 = st.columns(2)
    
    with col5:
        st.subheader("Nivel de Compromiso")
        orden_comp = ["Alto", "Medio", "Bajo"]
        comp_dist = df['compromiso'].value_counts().reindex(orden_comp, fill_value=0)
        
        colors_comp = {'Alto': '#27ae60', 'Medio': '#f39c12', 'Bajo': '#e74c3c'}
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
            xaxis_title="Nivel de Compromiso",
            yaxis_title="Cantidad"
        )
        st.plotly_chart(fig_comp, use_container_width=True)
    
    with col6:
        st.subheader("Top Skills Técnicas")
        all_skills = []
        for skills_str in df['skills'].dropna():
            if isinstance(skills_str, str):
                skills_list = eval(skills_str)
                all_skills.extend(skills_list)
        
        skills_series = pd.Series(all_skills)
        skills_dist = skills_series.value_counts().head(15)
        
        fig_skills = px.bar(
            x=skills_dist.values,
            y=skills_dist.index,
            orientation='h',
            labels={'x': 'Menciones', 'y': 'Skill'},
            color=skills_dist.values,
            color_continuous_scale='Oranges'
        )
        fig_skills.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_skills, use_container_width=True)
    
    st.markdown("---")
    
    st.header("Insights y Recomendaciones")
    
    perfil = insights['perfil']
    portafolio_analysis = insights['portafolio_analysis']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Perfil de Participantes")
        
        st.metric("Principiantes (declarado)", f"{perfil['porcentaje_principiantes']:.1f}%")
        st.metric("Principiantes (análisis Llama)", f"{perfil['porcentaje_principiantes_real']:.1f}%")
        
        st.write(f"**{perfil['porcentaje_con_jams_previas']:.1f}%** han participado en jams anteriores")
        st.write(f"Promedio de jams previas: **{perfil['promedio_jams']:.1f}**")
        st.write(f"**{perfil['compromiso_alto']:.1f}%** muestran alto compromiso")
        st.write(f"**{perfil['tiene_proyectos_pct']:.1f}%** tienen proyectos completados")
        st.write(f"Motivación principal: **{perfil['motivacion_principal']}**")
        
        st.write("\n**Top 5 Skills:**")
        for skill, count in perfil['top_skills'].items():
            st.write(f"- {skill}: {count} menciones")
    
    with col2:
        st.subheader("Análisis de Portafolios")
        st.write(f"**{portafolio_analysis['total_con_portafolio']}** participantes ({portafolio_analysis['porcentaje']:.1f}%) enviaron portafolio")
        st.write(f"**{portafolio_analysis['participantes_destacados']}** participantes destacados")
        
        if portafolio_analysis['destacados_data']:
            st.write("\n**Participantes Destacados:**")
            for p in portafolio_analysis['destacados_data'][:5]:
                with st.expander(f"{p['Nombre(s)']} {p['Apellidos(s)']} - {p['rol_1era_prioridad']}"):
                    st.write(f"**Nivel:** {p['nivel_experiencia_real']}")
                    if pd.notna(p['portafolio']) and p['portafolio']:
                        st.write(f"**Portafolio:** [{p['portafolio']}]({p['portafolio']})")
    
    st.markdown("---")
    st.subheader("Recomendaciones Accionables")
    
    recomendaciones = insights['recomendaciones']
    
    for rec in recomendaciones:
        tipo = rec['tipo']
        mensaje = rec['mensaje']
        
        if tipo == "URGENTE":
            st.error(f"**{tipo}:** {mensaje}")
        elif tipo == "IMPORTANTE":
            st.warning(f"**{tipo}:** {mensaje}")
        else:
            st.info(f"**{tipo}:** {mensaje}")
    
    st.markdown("---")
    st.caption("Dashboard con análisis precalculado de Llama 3.2.")

except FileNotFoundError as e:
    st.error(f"No se encontraron los archivos procesados: {str(e)}")
except Exception as e:
    st.error(f"Error al cargar los datos: {str(e)}")
    
    import traceback
    with st.expander("Ver detalles del error"):
        st.code(traceback.format_exc())