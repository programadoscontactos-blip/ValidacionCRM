import streamlit as st
import pandas as pd
import re
import sqlite3
from datetime import datetime

# =====================================================
# CONFIGURACION
# =====================================================

st.set_page_config(
    page_title="Repartidor Automático",
    page_icon="🚑",
    layout="wide"
)
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# =====================================================
# FUNCION ANALIZAR DESCRIPCION
# =====================================================


def analizar_descripcion(texto):

    texto = str(texto)

    fechas = re.findall(
        r"(\d{1,2}/\d{1,2}/\d{2,4})",
        texto,
        flags=re.IGNORECASE
    )

    horas = re.findall(
        r"(\d{1,2}[:\.]\d{2})",
        texto
    )

    if len(fechas) == 0:

        return {
            "fecha": None,
            "hora": "00:00",
            "alerta": "SIN_FECHA"
        }

    elif len(fechas) > 1:

        return {
            "fecha": fechas[0],
            "hora": horas[0].replace(".", ":") if horas else "00:00",
            "alerta": "MULTIPLES_FECHAS"
        }

    else:

        return {
            "fecha": fechas[0],
            "hora": horas[0].replace(".", ":") if horas else "00:00",
            "alerta": "OK"
        }

# =====================================================
# TITULO
# =====================================================
# =====================================
# HISTORICO SQLITE
# =====================================

def crear_historico():

    conn = sqlite3.connect("historico.db")

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico_casos (
            nro_caso TEXT PRIMARY KEY,
            fecha_traslado TEXT,
            fecha_reparto TEXT,
            operador TEXT,
            archivo_origen TEXT,
            estado TEXT DEFAULT 'PENDIENTE',
            fecha_validacion TEXT,
            hora_validacion TEXT,
            usuario_validacion TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS operadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE,
            password TEXT,
            activo INTEGER DEFAULT 1,
            recibe_reparto INTEGER DEFAULT 1,
            es_backoffice INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        INSERT OR IGNORE INTO operadores
        (
            usuario,
            password,
            activo,
            recibe_reparto,
            es_backoffice
        )
        VALUES
        (
            'Micaela',
            '1234',
            1,
            1,
            0
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO operadores
        (
            usuario,
            password,
            activo,
            recibe_reparto,
            es_backoffice
        )
        VALUES
        (
            'Salome',
            '1234',
            1,
            1,
            0
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO operadores
        (
            usuario,
            password,
            activo,
            recibe_reparto,
            es_backoffice
        )
        VALUES
        (
            'Paloma',
            '1234',
            1,
            1,
            0
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO operadores
        (
            usuario,
            password,
            activo,
            recibe_reparto,
            es_backoffice
        )
        VALUES
        (
            'Backoffice',
            'admin',
            1,
            0,
            1
        )
    """)
    conn.commit()
    conn.close()

crear_historico()
conn = sqlite3.connect("historico.db")

operadores = pd.read_sql_query(
    "SELECT * FROM operadores",
    conn
)

conn.close()




conn.close()

st.title(
    "🚑 Repartidor Automático de Traslados"
)

st.caption(
    "Sistema de reparto automático de traslados."
)

# =====================================================
# CARGA
# =====================================================

archivos = st.file_uploader(
    "Seleccione uno o varios CSV",
    type=["csv"],
    accept_multiple_files=True,
    key=f"uploader_{st.session_state.uploader_key}"
)

if archivos:

    st.info(
        f"📁 Archivos cargados: {len(archivos)}"
    )

# =====================================================
# PROCESAR
# =====================================================

c1, c2 = st.columns(2)

with c1:
    procesar = st.button("🚀 Procesar Reparto")

with c2:
    if st.button("🗑️ Borrar carga y resultados"):

        st.session_state.uploader_key += 1

        st.rerun()
if procesar:

    if not archivos:

        st.error(
            "Debe cargar al menos un archivo."
        )

    else:

        try:

            # =====================================
            # UNIFICAR ARCHIVOS
            # =====================================

            dataframes = []

            for archivo in archivos:

                df_temp = pd.read_csv(
                    archivo,
                    sep=";",
                    dtype=str,
                    encoding="utf-8"
                )

                dataframes.append(
                    df_temp
                )

            df = pd.concat(
                dataframes,
                ignore_index=True
            )

            # =====================================
            # BUSCAR DESCRIPCION
            # =====================================

            descripcion_col = None

            for c in df.columns:

                if "descrip" in c.lower():

                    descripcion_col = c
                    break

            if descripcion_col is None:

                st.error(
                    "No encontré la columna Descripción."
                )

                st.stop()

            # =====================================
            # ANALISIS
            # =====================================

            fechas = []
            horas = []
            alertas = []

            for texto in df[
                descripcion_col
            ].fillna("").astype(str):

                resultado = analizar_descripcion(
                    texto
                )

                fechas.append(
                    resultado["fecha"]
                )

                horas.append(
                    resultado["hora"]
                )

                alertas.append(
                    resultado["alerta"]
                )
            df["FECHA"] = (
                pd.Series(fechas)
                .fillna("")
                .astype(str)
                .str.strip()
                .str.replace(
                    r"^(\d{2}/\d{2}/)(\d{2})$",
                    r"\g<1>20\g<2>",
                    regex=True
)
            )

            df["HORA"] = horas
            df["ALERTA"] = alertas

            # ===================================
            # METRICAS
            # =====================================

            total_registros = len(df)

            sin_fecha = len(
                df[
                    df["ALERTA"] == "SIN_FECHA"
                ]
            )

            multiples_fechas = len(
                df[
                    df["ALERTA"] == "MULTIPLES_FECHAS"
                ]
            )

            casos_validos = len(
                df[
                    df["ALERTA"] == "OK"
                ]
            )

            # =====================================
            # DUPLICADOS
            # =====================================

            duplicados = 0

            caso_col = None

            for c in df.columns:

                if "caso" in c.lower():

                    caso_col = c
                    break

            if caso_col:

                df["DUPLICADO"] = df.duplicated(
                    subset=[caso_col],
                    keep=False
                )
                

                duplicados = len(
                    df[
                        df["DUPLICADO"]
                    ]
                )
            # =====================================
            # HISTORICO
            # =====================================

            conn_hist = sqlite3.connect(
                "historico.db"
            )

            historico = pd.read_sql_query(
                "SELECT nro_caso FROM historico_casos",
                conn_hist
            )

            conn_hist.close()

            casos_historicos = set(
                historico["nro_caso"].astype(str)
            )

            df["NRO_CASO_TMP"] = (
                df[caso_col].astype(str)
            )

            df_enviados_previamente = df[
                df["NRO_CASO_TMP"].isin(
                    casos_historicos
                )
            ].copy()

            df_para_repartir = df[
                ~df["NRO_CASO_TMP"].isin(
                    casos_historicos
                )
            ].copy()

            enviados_previamente = len(
                df_enviados_previamente
            )
            # =====================================
            # REPARTO ORIGINAL COLAB
            # =====================================

            df_validos = df_para_repartir.copy()
            
            df_validos = df_validos.drop_duplicates(
                subset=[caso_col],
                keep="first"
            )
            df_validos["HORA"] = (
                df_validos["HORA"]
                .fillna("00:00")
            )

            df_validos["FECHA_ORDEN"] = (
                pd.to_datetime(
                    df_validos["FECHA"],
                    format="%d/%m/%Y",
                    errors="coerce"
                )
                .fillna(
                    pd.Timestamp("2099-12-31")
                )
            )

            df_validos = df_validos.sort_values(
                ["FECHA_ORDEN", "HORA"]
            )
            conn_operadores = sqlite3.connect(
                "historico.db"
            )

            operadores_df = pd.read_sql_query(
                """
                SELECT usuario
                FROM operadores
                WHERE activo = 1
                AND recibe_reparto = 1
                AND es_backoffice = 0
                """,
                conn_operadores
            )

            conn_operadores.close()

            operadores_activos = (
                operadores_df["usuario"]
                .tolist()
            )

            st.write(
    "Operadores activos:",
    operadores_activos
)

            # =====================================
            # OPERADORES ACTIVOS
            # =====================================

            conn_operadores = sqlite3.connect(
                "historico.db"
            )

            operadores_df = pd.read_sql_query(
                """
                SELECT usuario
                FROM operadores
                WHERE activo = 1
                AND recibe_reparto = 1
                AND es_backoffice = 0
                """,
                conn_operadores
            )

            conn_operadores.close()

            operadores_activos = (
                operadores_df["usuario"]
                .tolist()
            )

            if len(operadores_activos) == 0:

                st.error(
                    "No hay operadores habilitados para reparto."
                )

                st.stop()

            # =====================================
            # REPARTO DINAMICO
            # =====================================

            casos_por_operador = {
                operador: []
                for operador in operadores_activos
            }

            contador_global = 0

            for fecha, grupo in df_validos.groupby(
                "FECHA_ORDEN"
            ):

                grupo = grupo.sort_values(
                    "HORA"
                )

                for _, fila in grupo.iterrows():

                    fila = fila.copy()

                    operador_asignado = (
                        operadores_activos[
                            contador_global
                            % len(operadores_activos)
                        ]
                    )

                    fila["OPERADOR"] = (
                        operador_asignado
                    )

                    casos_por_operador[
                        operador_asignado
                    ].append(fila)

                    contador_global += 1

            df_reparto = pd.concat(
                [
                    pd.DataFrame(casos)
                    for casos in casos_por_operador.values()
                ],
                ignore_index=True
            )
            
            conn = sqlite3.connect(
                "historico.db"
            )

            fecha_reparto = datetime.now().strftime(
                "%d/%m/%Y"
            )

            conn.commit()
            conn.close()

            csv_reparto = df_reparto.to_csv(
                index=False,
                sep=";"
            ).encode("utf-8")

            st.download_button(
                label="📥 Descargar Reparto CSV",
                data=csv_reparto,
                file_name=f"reparto_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )  
            # =====================================
            # GUARDAR HISTORICO
            # =====================================

            conn = sqlite3.connect("historico.db")

            fecha_reparto = datetime.now().strftime("%d/%m/%Y")

            for _, fila in df_reparto.iterrows():

                try:
                    conn.execute(
                        """
                        INSERT INTO historico_casos
                        (
                            nro_caso,
                            fecha_traslado,
                            fecha_reparto,
                            operador,
                            archivo_origen,
                            estado
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            str(fila[caso_col]),
                            fila["FECHA"],
                            fecha_reparto,
                            fila["OPERADOR"],
                            "STREAMLIT",
                            "PENDIENTE"
                        )
                    )

                except sqlite3.IntegrityError:
                    pass

            conn.commit()
            conn.close()

           
            # =====================================
            # RESULTADO
            # =====================================

            c1, c2, c3 = st.columns(3)

            with c1:
                    st.metric(
                        "Casos Cargados",
                        total_registros
                    )

            with c2:
                    st.metric(
                        "Casos Repartidos",
                        len(df_reparto)
                    )

            with c3:
                    st.metric(
                        "Enviados Previamente",
                        enviados_previamente
                    )

            st.subheader(
                "👩‍💼 Distribución de Casos Reparto"
            )

            columnas = st.columns(
                len(operadores_activos)
            )

            for i, operador in enumerate(
                operadores_activos
            ):

                with columnas[i]:

                    st.metric(
                        operador,
                        len(
                            casos_por_operador[
                                operador
                            ]
                        )
            )
        except Exception as e:
            st.error(f"Error: {e}")