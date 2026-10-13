import streamlit as st
import pandas as pd
import sqlite3

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

st.subheader(
    "Casos asignados"
)

columnas = [
    "nro_caso",
    "fecha_reparto",
    "estado"
]

st.dataframe(
    df_filtrado[columnas],
    use_container_width=True,
    hide_index=True
)

# =====================================
# VALIDAR CASO
# =====================================

pendientes_df = df[
    df["estado"] == "PENDIENTE"
]

if len(pendientes_df) > 0:

    st.divider()

    caso_validar = st.selectbox(
        "Seleccionar caso",
        pendientes_df["nro_caso"].tolist()
    )

    if st.button("✅ Marcar Validado"):

        conn = sqlite3.connect(
            "historico.db"
        )

        conn.execute(
            """
            UPDATE historico_casos
            SET estado='VALIDADO'
            WHERE nro_caso=?
            """,
            (caso_validar,)
        )

        conn.commit()
        conn.close()

        st.success(
            f"Caso {caso_validar} validado correctamente"
        )

        st.rerun()

else:

    st.success(
        "No hay casos pendientes."
    )

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