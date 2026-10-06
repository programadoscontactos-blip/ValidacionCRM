import streamlit as st
import pandas as pd
import re

# =====================================================
# CONFIGURACION
# =====================================================

st.set_page_config(
    page_title="Repartidor Automático",
    page_icon="🚑",
    layout="wide"
)

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
    accept_multiple_files=True
)

if archivos:

    st.info(
        f"📁 Archivos cargados: {len(archivos)}"
    )

# =====================================================
# PROCESAR
# =====================================================

if st.button("🚀 Procesar Reparto"):

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

            df["FECHA"] = fechas
            df["HORA"] = horas
            df["ALERTA"] = alertas

            # =====================================
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
            # REPARTO ORIGINAL COLAB
            # =====================================

            df_validos = df[
                df["ALERTA"] == "OK"
            ].copy()

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

            operador1 = []
            operador2 = []
            operador3 = []

            contador_global = 0

            for fecha, grupo in df_validos.groupby(
                "FECHA_ORDEN"
            ):

                grupo = grupo.sort_values(
                    "HORA"
                )

                for _, fila in grupo.iterrows():

                    fila = fila.copy()

                    if contador_global % 3 == 0:

                        fila["OPERADOR"] = "Micaela"
                        operador1.append(fila)

                    elif contador_global % 3 == 1:

                        fila["OPERADOR"] = "Salome"
                        operador2.append(fila)

                    else:

                        fila["OPERADOR"] = "Paloma"
                        operador3.append(fila)

                    contador_global += 1

            df1 = pd.DataFrame(
                operador1
            )

            df2 = pd.DataFrame(
                operador2
            )

            df3 = pd.DataFrame(
                operador3
            )

            cant_micaela = len(df1)
            cant_salome = len(df2)
            cant_paloma = len(df3)

            df_reparto = pd.concat(
                [df1, df2, df3],
                ignore_index=True
            )

            # =====================================
            # RESULTADO
            # =====================================

            st.subheader(
                "✅ Resultado del procesamiento"
            )

            c1, c2, c3, c4, c5 = st.columns(5)

            with c1:
                st.metric(
                    "Registros",
                    total_registros
                )

            with c2:
                st.metric(
                    "Casos válidos",
                    casos_validos
                )

            with c3:
                st.metric(
                    "Sin fecha",
                    sin_fecha
                )

            with c4:
                st.metric(
                    "Múltiples fechas",
                    multiples_fechas
                )

            with c5:
                st.metric(
                    "Duplicados",
                    duplicados
                )

            st.subheader(
                "🎯 Reparto"
            )
            
            r1, r2, r3 = st.columns(3)

            with r1:
                st.metric(
                    "Micaela",
                    cant_micaela
                )

            with r2:
                st.metric(
                    "Salome",
                    cant_salome
                )

            with r3:
                st.metric(
                    "Paloma",
                    cant_paloma
                )

            st.success(
                "Reparto generado correctamente."
            )
        except Exception as e:
               st.error(
                f"Error: {e}"
                )