import pandas as pd
import numpy as np
from llm_classifier import LlamaAnalyzer
import json
import os

class DataProcessor:
    
    def __init__(self, csv_path: str, use_cache: bool = True):
        self.df = pd.read_csv(csv_path)
        self.analyzer = LlamaAnalyzer(model_name="llama3.2")
        self.cache_file = "data/llm_cache.json"
        self.cache = self._load_cache() if use_cache else {}
        
        print(f"\nCargados {len(self.df)} registros")
        print("Limpiando datos...")
        self._clean_data()
        
        print("Procesando respuestas con Llama 3.2...")
        self._process_text_fields()
        
        if use_cache:
            self._save_cache()
        
        self._save_processed_data()
        print("Procesamiento completado\n")
    
    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    if all(key in cache for key in ['motivaciones', 'experiencias', 'compromisos', 'skills']):
                        return cache
            except:
                pass
        return {
            "motivaciones": {},
            "experiencias": {},
            "compromisos": {},
            "skills": {}
        }
    
    def _save_cache(self):
        os.makedirs('data', exist_ok=True)
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)
    
    def _save_processed_data(self):
        processed_file = "data/processed_data.csv"
        self.df.to_csv(processed_file, index=False, encoding='utf-8')
        print(f"Datos procesados guardados en {processed_file}")
        
        insights_file = "data/insights.json"
        insights = {
            "kpis": self.get_kpis(),
            "perfil": self.get_perfil_participantes(),
            "portafolio_analysis": self.get_portafolio_analysis(),
            "alerts": self.get_deficit_alerts(),
            "recomendaciones": self.generate_recommendations()
        }
        
        with open(insights_file, 'w', encoding='utf-8') as f:
            json.dump(insights, f, ensure_ascii=False, indent=2)
        print(f"Insights guardados en {insights_file}")
    
    def _clean_data(self):
        self.df['Edad'] = pd.to_numeric(self.df['Edad'], errors='coerce')
        self.df['nivel_experiencia'] = pd.to_numeric(self.df['nivel_experiencia'], errors='coerce')
        self.df['tiene_portafolio'] = self.df['portafolio'].notna() & (self.df['portafolio'] != '')
        
        def mapear_nivel(valor):
            if pd.isna(valor):
                return "No especificado"
            elif valor == 1:
                return "1"
            elif valor == 2:
                return "2"
            elif valor == 3:
                return "3"
            elif valor == 4:
                return "4"
            elif valor == 5:
                return "5"
            else:
                return "No especificado"
        
        self.df['categoria_experiencia'] = self.df['nivel_experiencia'].apply(mapear_nivel)
        
        def grupo_edad(edad):
            if pd.isna(edad):
                return "No especificado"
            elif edad < 20:
                return "< 20"
            elif edad < 25:
                return "20-24"
            elif edad < 30:
                return "25-29"
            else:
                return "30+"
        
        self.df['grupo_edad'] = self.df['Edad'].apply(grupo_edad)
    
    def _process_text_fields(self):
        print("\nAnalizando motivaciones...")
        motivaciones = self.df['motivacion'].fillna("").tolist()
        self.df['categoria_motivacion'] = self.analyzer.procesar_batch_con_cache(
            motivaciones, "motivacion", self.cache['motivaciones']
        )
        
        print("\nAnalizando experiencia en juegos...")
        experiencias = self.df['experiencia_juegos'].fillna("").tolist()
        exp_results = self.analyzer.procesar_batch_con_cache(
            experiencias, "experiencia", self.cache['experiencias']
        )
        
        self.df['tiene_proyectos'] = [r['tiene_proyectos'] for r in exp_results]
        self.df['jams_previas'] = [r['jams_previas'] for r in exp_results]
        self.df['nivel_experiencia_real'] = [r['nivel_real'] for r in exp_results]
        
        print("\nAnalizando nivel de compromiso...")
        textos_compromiso = [
            f"{str(row['motivacion'])} {str(row['experiencia_juegos'])}"
            for _, row in self.df.iterrows()
        ]
        self.df['compromiso'] = self.analyzer.procesar_batch_con_cache(
            textos_compromiso, "compromiso", self.cache['compromisos']
        )
        
        print("\nExtrayendo skills técnicas...")
        textos_skills = [
            f"{str(row['experiencia_juegos'])} {str(row['experiencia_profesional'])}"
            for _, row in self.df.iterrows()
        ]
        self.df['skills'] = self.analyzer.procesar_batch_con_cache(
            textos_skills, "skills", self.cache['skills']
        )
    
    def get_kpis(self) -> dict:
        return {
            "total_inscritos": int(len(self.df)),
            "edad_promedio": float(self.df['Edad'].mean()),
            "porcentaje_portafolio": float((self.df['tiene_portafolio'].sum() / len(self.df)) * 100)
        }
    
    def get_roles_distribution(self):
        return self.df['rol_1era_prioridad'].value_counts()
    
    def get_experiencia_distribution(self):
        return self.df['categoria_experiencia'].value_counts()
    
    def get_edad_distribution(self):
        orden = ["< 20", "20-24", "25-29", "30+", "No especificado"]
        dist = self.df['grupo_edad'].value_counts()
        return dist.reindex(orden, fill_value=0)
    
    def get_motivacion_distribution(self):
        return self.df['categoria_motivacion'].value_counts()
    
    def get_compromiso_distribution(self):
        orden = ["Alto", "Medio", "Bajo"]
        dist = self.df['compromiso'].value_counts()
        return dist.reindex(orden, fill_value=0)
    
    def get_skills_distribution(self):
        all_skills = []
        for skills_list in self.df['skills']:
            if isinstance(skills_list, list) and len(skills_list) > 0:
                all_skills.extend(skills_list)
        
        if not all_skills:
            return pd.Series(dtype=int)
        
        skills_series = pd.Series(all_skills)
        return skills_series.value_counts().head(15)
    
    def get_deficit_alerts(self) -> list:
        roles_counts = self.get_roles_distribution()
        alerts = []
        
        UMBRAL_CRITICO = 3
        UMBRAL_BAJO = 5
        
        for rol, count in roles_counts.items():
            if count <= UMBRAL_CRITICO:
                alerts.append({
                    "nivel": "CRÍTICO",
                    "rol": rol,
                    "cantidad": int(count),
                    "mensaje": f"CRÍTICO: Solo {count} persona(s) en {rol}"
                })
            elif count <= UMBRAL_BAJO:
                alerts.append({
                    "nivel": "BAJO",
                    "rol": rol,
                    "cantidad": int(count),
                    "mensaje": f"BAJO: Solo {count} personas en {rol}"
                })
        
        return alerts
    
    def get_perfil_participantes(self) -> dict:
        skills_dist = self.get_skills_distribution()
        top_skills = {str(k): int(v) for k, v in skills_dist.head(5).to_dict().items()} if len(skills_dist) > 0 else {}
        
        return {
            "porcentaje_principiantes": float((self.df['categoria_experiencia'].isin(['1', '2'])).sum() / len(self.df) * 100),
            "porcentaje_principiantes_real": float((self.df['nivel_experiencia_real'] == "Principiante").sum() / len(self.df) * 100),
            "porcentaje_con_jams_previas": float((self.df['jams_previas'] > 0).sum() / len(self.df) * 100),
            "promedio_jams": float(self.df['jams_previas'].mean()),
            "top_skills": top_skills,
            "motivacion_principal": str(self.df['categoria_motivacion'].mode()[0] if len(self.df['categoria_motivacion'].mode()) > 0 else "No especificado"),
            "compromiso_alto": float((self.df['compromiso'] == "Alto").sum() / len(self.df) * 100),
            "tiene_proyectos_pct": float((self.df['tiene_proyectos'] == True).sum() / len(self.df) * 100)
        }
    
    def get_portafolio_analysis(self) -> dict:
        con_portafolio = self.df[self.df['tiene_portafolio']]
        
        return {
            "total_con_portafolio": int(len(con_portafolio)),
            "porcentaje": float((len(con_portafolio) / len(self.df)) * 100)
        }
    
    def generate_recommendations(self) -> list:
        recomendaciones = []
        alerts = self.get_deficit_alerts()
        perfil = self.get_perfil_participantes()
        
        if alerts:
            roles_criticos = [a['rol'] for a in alerts if a['nivel'] == 'CRÍTICO']
            roles_bajos = [a['rol'] for a in alerts if a['nivel'] == 'BAJO']
            
            if roles_criticos:
                recomendaciones.append({
                    "tipo": "URGENTE",
                    "mensaje": f"Hacer campaña de reclutamiento para: {', '.join(roles_criticos)}"
                })
            
            if roles_bajos:
                recomendaciones.append({
                    "tipo": "IMPORTANTE",
                    "mensaje": f"Reforzar reclutamiento en: {', '.join(roles_bajos)}"
                })
        
        if perfil['porcentaje_principiantes_real'] > 60:
            recomendaciones.append({
                "tipo": "EDUCATIVO",
                "mensaje": f"{perfil['porcentaje_principiantes_real']:.0f}% son principiantes. Considerar talleres introductorios y mentores."
            })
        
        if perfil['top_skills'] and len(perfil['top_skills']) > 0:
            top_skill = list(perfil['top_skills'].keys())[0]
            recomendaciones.append({
                "tipo": "TÉCNICO",
                "mensaje": f"{top_skill} es la herramienta más mencionada. Asegurar soporte técnico."
            })
        
        if perfil['motivacion_principal'] == 'Networking':
            recomendaciones.append({
                "tipo": "SOCIAL",
                "mensaje": "Motivación principal es Networking. Fortalecer espacios de socialización."
            })
        elif perfil['motivacion_principal'] == 'Aprendizaje':
            recomendaciones.append({
                "tipo": "EDUCATIVO",
                "mensaje": "Motivación principal es Aprendizaje. Reforzar contenido educativo y workshops."
            })
        
        if perfil['porcentaje_con_jams_previas'] < 30:
            recomendaciones.append({
                "tipo": "LOGÍSTICO",
                "mensaje": f"Solo {perfil['porcentaje_con_jams_previas']:.0f}% tienen experiencia en jams. Preparar orientación detallada."
            })
        
        if perfil['compromiso_alto'] < 40:
            recomendaciones.append({
                "tipo": "COMUNICACIÓN",
                "mensaje": f"Solo {perfil['compromiso_alto']:.0f}% muestran alto compromiso. Reforzar comunicación sobre expectativas."
            })
        
        return recomendaciones