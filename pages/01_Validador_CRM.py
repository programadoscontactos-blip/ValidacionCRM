import streamlit as st
import pandas as pd
import sqlite3

from datetime import datetime, time

# =====================================
# CONFIGURACION
# =====================================

st.set_page_config(
    page_title="Validador CRM",
    page_icon="📋",
    layout="wide"
    
)


# =====================================
# LOGIN
# =====================================

USUARIOS = {
    "Micaela": "1234",
    "Salome": "1234",
    "Paloma": "1234",
    "Backoffice": "admin"
}

if "usuario" not in st.session_state:
    st.session_state["usuario"] = None

if st.session_state["usuario"] is None:

    st.title("📋 Validador CRM")

    usuario_seleccionado = st.selectbox(
        "Usuario",
        list(USUARIOS.keys())
    )

    password = st.text_input(
        "Contraseña",
        type="password"
    )

    if st.button("Ingresar"):

        if password == USUARIOS[usuario_seleccionado]:

            st.session_state["usuario"] = usuario_seleccionado
            st.rerun()

        else:

            st.error(
                "Contraseña incorrecta"
            )

    st.stop()

usuario = st.session_state["usuario"]

# =====================================
# CABECERA
# =====================================

col1, col2 = st.columns([8, 1])

with col1:

    st.title(
        f"📋 Validador CRM - {usuario}"
    )

with col2:

    if st.button("Salir"):

        st.session_state["usuario"] = None
        st.rerun()
# =====================================
# RELOJ Y CUENTA REGRESIVA
# =====================================

from datetime import datetime
from zoneinfo import ZoneInfo

ahora = datetime.now(
    ZoneInfo("America/Argentina/Buenos_Aires")
)

st.info(
    f"🕒 Hora actual del servidor: {ahora.strftime('%d/%m/%Y %H:%M:%S')}"
)

# =====================================
# LEER HISTORICO
# =====================================

try:

    conn = sqlite3.connect(
        "historico.db"
    )

    df = pd.read_sql_query(
        """
        SELECT *
        FROM historico_casos
        """,
        conn
    )
    st.write(df.columns.tolist())

    conn.close()

except Exception:

    st.error(
        "No se encontró historico.db"
    )

    st.stop()

# =====================================
# FILTRO OPERADOR
# =====================================

if usuario != "Backoffice":

    df = df[
        df["operador"] == usuario
    ].copy()

# =====================================
# METRICAS
# =====================================

pendientes = len(
    df[
        df["estado"] == "PENDIENTE"
    ]
)

validados = len(
    df[
        df["estado"] == "VALIDADO"
    ]
)

c1, c2, c3 = st.columns(3)

with c1:

    st.metric(
        "Pendientes",
        pendientes
    )

with c2:

    st.metric(
        "Validados",
        validados
    )

with c3:

    st.metric(
        "Total Casos",
        len(df)
    )

# =====================================
# FILTRO ESTADO
# =====================================

st.divider()

estado_filtro = st.selectbox(
    "Estado",
    [
        "Todos",
        "PENDIENTE",
        "VALIDADO"
    ]
)

df_filtrado = df.copy()

if estado_filtro != "Todos":

    df_filtrado = df_filtrado[
        df_filtrado["estado"]
        == estado_filtro
    ]

# =====================================
# TABLA
# =====================================
# =====================================
# BANDEJA DE TRABAJO
# =====================================
if st.session_state.get("archivo_validado"):

    st.success(
        "✅ Archivo validado"
    )

    st.session_state["archivo_validado"] = False

st.subheader(
    "Casos asignados"
)

cab1, cab2, cab3, cab4 = st.columns(
    [3, 2, 2, 1]
)

cab1.markdown("**Caso**")
cab2.markdown("**Fecha**")
cab3.markdown("**Estado**")
cab4.markdown("**Acción**")

st.divider()

for _, fila in df_filtrado.iterrows():

    c1, c2, c3, c4 = st.columns(
        [3, 2, 2, 1]
    )

    with c1:
        st.write(
            fila["nro_caso"]
        )

    with c2:
        st.write(
            fila["fecha_reparto"]
        )

    with c3:

        if fila["estado"] == "VALIDADO":

            st.markdown(
                "🟢 **VALIDADO**"
            )

        else:

            st.markdown(
                "🟡 **PENDIENTE**"
            )

    with c4:

        if fila["estado"] == "PENDIENTE":

            if st.button(
                "Validar",
                key=f"validar_{fila['nro_caso']}"
            ):

                conn = sqlite3.connect(
                    "historico.db"
                )

                conn.execute(
                    """
                    UPDATE historico_casos
                    SET estado='VALIDADO'
                    WHERE nro_caso=?
                    """,
                    (
                        fila["nro_caso"],
                    )
                )

                conn.commit()
                conn.close()

                st.session_state["archivo_validado"] = True
                st.rerun()

        else:

            st.write("✔")
# =====================================
# DESCARGA
# =====================================

csv = df_filtrado.to_csv(
    index=False,
    sep=";"
).encode("utf-8")

st.download_button(
    "📥 Descargar mis casos",
    csv,
    file_name=f"{usuario}_casos.csv",
    mime="text/csv"
)