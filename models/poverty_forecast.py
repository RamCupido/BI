import pandas as pd
from Config.db_config import get_connection

def load_poverty_series(conn):
    query = """
    SELECT
      dt.PERIODO,
      AVG(
        CASE
          WHEN UPPER(LTRIM(RTRIM(h.POBREZA))) = 'SI' THEN 1.0
          ELSE 0.0
        END
      ) * 100 AS pobreza_pct
    FROM hechos_enemdu h
    JOIN dim_tiempo dt
      ON h.ID_TIEMPO = dt.ID_TIEMPO
    GROUP BY dt.PERIODO
    ORDER BY dt.PERIODO;
    """
    df = pd.read_sql(query, conn)
    # Convertir PERIODO (ej. '2020') a índice datetime
    df['PERIODO'] = pd.to_datetime(df['PERIODO'], format='%Y')
    df.set_index('PERIODO', inplace=True)
    return df['pobreza_pct']
