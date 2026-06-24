import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import requests

# 1. Descargar datos del NASDAQ-100
print("Descargando datos del Nasdaq-100 desde Yahoo Finance...")
nasdaq = yf.download("QQQ", start="2020-01-01", end="2025-01-01")

# Aplanamos el encabezado doble de Yahoo y renombramos la columna
nasdaq_close = nasdaq['Close'].copy()
nasdaq_close.columns = ['NASDAQ_100']

# 2. Descargar datos del Risky Norris (Con User-Agent para evitar bloqueos)
print("Descargando datos del Risky Norris desde la API de Fintual...")
url_fintual = "https://fintual.cl/api/real_assets/186/days"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

respuesta = requests.get(url_fintual, headers=headers)

# Verificamos si la conexión fue exitosa
if respuesta.status_code != 200:
    print(f"¡Error al conectar con Fintual! Código: {respuesta.status_code}")
else:
    print("¡Datos de Fintual descargados con éxito!")
    datos_fintual = respuesta.json()['data']

    # Convertimos el JSON de Fintual a un formato que Pandas entienda
    fechas = [dia['attributes']['date'] for dia in datos_fintual]
    valores_cuota = [dia['attributes']['price'] for dia in datos_fintual]

    # Creamos la tabla del fondo
    risky = pd.DataFrame({'Risky_Norris': valores_cuota}, index=pd.to_datetime(fechas))
    
    # Hacemos que la zona horaria coincida (Yahoo Finance viene con zona horaria)
    risky.index = risky.index.tz_localize(nasdaq_close.index.tz)

    # 3. Unir y Limpiar los Datos (Ahora ambas tablas tienen 1 solo nivel)
    df_comparacion = pd.merge(nasdaq_close, risky, left_index=True, right_index=True, how='inner')

    # 4. Normalizar a Base 100
    df_normalizado = (df_comparacion / df_comparacion.iloc[0]) * 100

    # 5. Visualización de los Resultados
    plt.figure(figsize=(12, 6))
    plt.plot(df_normalizado.index, df_normalizado['NASDAQ_100'], label='NASDAQ-100 (QQQ)', color='blue')
    plt.plot(df_normalizado.index, df_normalizado['Risky_Norris'], label='Risky Norris', color='orange')

    plt.title('Comparación de Rendimiento Base 100: NASDAQ-100 vs Risky Norris (2020-2025)', fontsize=14)
    plt.xlabel('Fecha', fontsize=12)
    plt.ylabel('Crecimiento del Capital (Base 100)', fontsize=12)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)

    # Mostrar el gráfico en pantalla
    plt.show()