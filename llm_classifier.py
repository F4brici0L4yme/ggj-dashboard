import ollama
import json
import re
from typing import Dict, List
import pandas as pd

class LlamaAnalyzer:
    
    def __init__(self, model_name: str = "llama3.2"):
        self.model_name = model_name
        print(f"Inicializando analizador con modelo: {model_name}")
        
    def _query_llama(self, prompt: str, max_tokens: int = 100) -> str:
        try:
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    'temperature': 0.1,
                    'num_predict': max_tokens
                }
            )
            return response['response'].strip()
        except Exception as e:
            print(f"Error al consultar Llama: {e}")
            return ""
    
    def clasificar_motivacion(self, texto: str) -> str:
        if not texto or pd.isna(texto):
            return "No especificado"
        
        prompt = f"""Analiza esta respuesta sobre por qué alguien quiere participar en un Game Jam:

"{texto}"

Clasifícala en UNA de estas categorías exactas:
- Aprendizaje
- Networking
- Reto_personal
- Pasion_videojuegos
- Experiencia_profesional
- General

Responde SOLO con el nombre de la categoría, sin explicaciones adicionales."""
        
        respuesta = self._query_llama(prompt, max_tokens=20)
        
        categorias_validas = [
            "Aprendizaje", "Networking", "Reto_personal", 
            "Pasion_videojuegos", "Experiencia_profesional", "General"
        ]
        
        for cat in categorias_validas:
            if cat.lower() in respuesta.lower():
                return cat
        
        return "General"
    
    def extraer_experiencia(self, texto: str) -> Dict[str, any]:
        if not texto or pd.isna(texto):
            return {
                "tiene_proyectos": False,
                "jams_previas": 0,
                "nivel_real": "Principiante"
            }
        
        prompt = f"""Analiza esta descripción de experiencia en desarrollo de videojuegos:

"{texto}"

Extrae la siguiente información y responde SOLO en formato JSON:
{{
    "tiene_proyectos": true/false (si menciona haber completado proyectos de juegos),
    "jams_previas": número (cuántas jams/hackathons ha participado, 0 si no menciona),
    "nivel_real": "Principiante"/"Intermedio"/"Avanzado" (evalúa el nivel real basado en lo que describe)
}}

Responde SOLO con el JSON, sin texto adicional."""
        
        respuesta = self._query_llama(prompt, max_tokens=150)
        
        try:
            json_match = re.search(r'\{.*\}', respuesta, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return {
                    "tiene_proyectos": bool(data.get("tiene_proyectos", False)),
                    "jams_previas": int(data.get("jams_previas", 0)),
                    "nivel_real": data.get("nivel_real", "Principiante")
                }
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"Error parseando JSON de Llama: {e}")
        
        return self._fallback_experiencia(texto)
    
    def _fallback_experiencia(self, texto: str) -> Dict[str, any]:
        texto_lower = texto.lower()
        
        tiene_proyectos = bool(re.search(r'(proyecto|game|juego|desarrollo|creé|hice|desarrollé|completé)', texto_lower))
        
        jams_match = re.search(r'(\d+)\s*(jam|hackathon)', texto_lower)
        jams_previas = int(jams_match.group(1)) if jams_match else (1 if 'jam' in texto_lower else 0)
        
        indicadores_avanzado = ['varios proyectos', 'años', 'profesional', 'publicado', 'comercial']
        indicadores_intermedio = ['proyecto', 'jam', 'universidad', 'curso', 'bootcamp']
        
        if any(ind in texto_lower for ind in indicadores_avanzado):
            nivel_real = "Avanzado"
        elif any(ind in texto_lower for ind in indicadores_intermedio):
            nivel_real = "Intermedio"
        else:
            nivel_real = "Principiante"
        
        return {
            "tiene_proyectos": tiene_proyectos,
            "jams_previas": jams_previas,
            "nivel_real": nivel_real
        }
    
    def analizar_compromiso(self, texto: str) -> str:
        if not texto or pd.isna(texto):
            return "Bajo"
        
        prompt = f"""Analiza estas respuestas de un participante a un Game Jam:

"{texto}"

Evalúa su nivel de compromiso basándote en:
- Detalle y profundidad de las respuestas
- Entusiasmo y motivación expresada
- Especificidad de lo que puede aportar

Clasifica en UNA de estas categorías:
- Alto (respuestas detalladas, específicas, muestra compromiso claro)
- Medio (respuestas completas pero genéricas)
- Bajo (respuestas vagas, cortas o poco específicas)

Responde SOLO con: Alto, Medio o Bajo"""
        
        respuesta = self._query_llama(prompt, max_tokens=20)
        
        if "alto" in respuesta.lower():
            return "Alto"
        elif "medio" in respuesta.lower():
            return "Medio"
        else:
            return "Bajo"
    
    def extraer_skills(self, texto: str) -> List[str]:
        if not texto or pd.isna(texto):
            return []
        
        prompt = f"""Analiza este texto sobre experiencia en desarrollo de videojuegos:

"{texto}"

Identifica y lista TODAS las herramientas, tecnologías y skills técnicas mencionadas.
Incluye: game engines, lenguajes de programación, software de arte/audio, frameworks, etc.

Ejemplos: Unity, Unreal, Godot, C#, Python, Blender, Photoshop, Git, etc.

Responde SOLO con una lista separada por comas, sin numeración ni texto adicional.
Ejemplo: Unity, C#, Blender"""
        
        respuesta = self._query_llama(prompt, max_tokens=100)
        
        skills = [s.strip() for s in respuesta.split(',')]
        
        skills_limpias = []
        for skill in skills:
            if len(skill) < 30 and not any(word in skill.lower() for word in ['ejemplo', 'respuesta', 'texto', 'sin', 'etc']):
                skills_limpias.append(skill)
        
        return skills_limpias[:15]

    def procesar_batch_con_cache(self, textos: List[str], tipo: str, cache: Dict = None) -> List:
        if cache is None:
            cache = {}
        
        resultados = []
        for i, texto in enumerate(textos):
            texto_key = str(texto) if texto else "none"
            
            if texto_key in cache:
                resultados.append(cache[texto_key])
                print(f"✓ {tipo} {i+1}/{len(textos)} (cached)")
            else:
                if tipo == "motivacion":
                    resultado = self.clasificar_motivacion(texto)
                elif tipo == "experiencia":
                    resultado = self.extraer_experiencia(texto)
                elif tipo == "compromiso":
                    resultado = self.analizar_compromiso(texto)
                elif tipo == "skills":
                    resultado = self.extraer_skills(texto)
                else:
                    resultado = None
                
                resultados.append(resultado)
                cache[texto_key] = resultado
                print(f"✓ {tipo} {i+1}/{len(textos)} procesado")
        
        return resultados