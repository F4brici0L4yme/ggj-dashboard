import pandas as pd

df = pd.read_csv('./data/Fillout GGJ26_INSCRIPCION results.csv')

columnas_eliminar = [
    'Submission ID',
    'Status',
    'Current step',
    'Created records',
    'id',
    'Errors',
    'Url',
    'Network ID'
]

df = df.drop(columns=columnas_eliminar, errors='ignore')

renombrar = {
    '¿Cómo calificarías tu nivel de experiencia en desarrollo de juegos?': 'nivel_experiencia',
    '1era prioridad (¿En qué área(s) podrías desempeñarte durante el Game Jam? (Marca 3, en orden de prioridad))': 'rol_1era_prioridad',
    '2nda prioridad (¿En qué área(s) podrías desempeñarte durante el Game Jam? (Marca 3, en orden de prioridad))': 'rol_2nda_prioridad',
    '3era prioridad (¿En qué área(s) podrías desempeñarte durante el Game Jam? (Marca 3, en orden de prioridad))': 'rol_3era_prioridad',
    '¿Por qué deseas participar en la Global Game Jam Arequipa?': 'motivacion',
    '¿Cuentanos sobre tu experiencia en desarrollo de juegos?': 'experiencia_juegos',
    'Cuéntanos brevemente sobre tu experiencia como estudiante y/o profesional': 'experiencia_profesional',
    'Portafolio / experiencia (opcional):Adjunta enlaces a trabajos previos (Paginas de portafolio, GitHub, itch.io, Drive, etc.)': 'portafolio'
}

df = df.rename(columns=renombrar)

df.to_csv('./data/inscripciones.csv', index=False)

print(f"Procesamiento completado. Total de registros: {len(df)}")
print(f"Columnas finales: {list(df.columns)}")