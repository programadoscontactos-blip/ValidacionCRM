
import streamlit as st
import pandas as pd
import sqlite3
# conn = sqlite3.connect(
#    "historico.db"
#)

#usuario_actual = (
#    st.session_state.get("usuario")
#)

#permisos = pd.read_sql_query(
#    """
#    SELECT es_backoffice
#    FROM operadores
#    WHERE usuario = ?
#    """,
#    conn,
#    params=(usuario_actual,)
#)

#conn.close()

#if (
#    len(permisos) == 0
#    or
#    permisos.iloc[0]["es_backoffice"] != 1
#):

#    st.error(
#        "Acceso exclusivo para Backoffice."
#    )

#    st.stop()
st.set_page_config(
    page_title="Operadores",
    page_icon="⚙️",
    layout="wide"
)
# =====================================
# CONTROL DE ACCESO
# =====================================

usuario_actual = st.session_state.get("usuario")

if usuario_actual is None:

    st.warning(
        "Primero debe iniciar sesión desde Validador CRM."
    )

    st.stop()

conn_permiso = sqlite3.connect(
    "historico.db"
)

permiso = conn_permiso.execute(
    """
    SELECT es_backoffice
    FROM operadores
    WHERE usuario = ?
    AND activo = 1
    """,
    (
        usuario_actual,
    )
).fetchone()

conn_permiso.close()

if permiso is None or permiso[0] != 1:

    st.error(
        "Acceso exclusivo para usuarios con permiso Backoffice."
    )

    st.stop()
st.title("⚙️ Operadores")

conn = sqlite3.connect(
    "historico.db"
)
df = pd.read_sql_query(
    """
    SELECT
        id,
        usuario,
        activo,
        recibe_reparto,
        es_backoffice
    FROM operadores
    """,
    conn
)

df["activo"] = df["activo"].astype(bool)
df["recibe_reparto"] = df["recibe_reparto"].astype(bool)
df["es_backoffice"] = df["es_backoffice"].astype(bool)

editor = st.data_editor(
    df,
    hide_index=True,
    width="stretch",
    disabled=[
        "id",
        "usuario"
    ]
)
st.divider()

st.subheader("➕ Nuevo operador")

nuevo_usuario = st.text_input(
    "Usuario"
)

nueva_password = st.text_input(
    "Contraseña",
    type="password"
)

nuevo_activo = st.checkbox(
    "Activo",
    value=True
)

nuevo_reparte = st.checkbox(
    "Recibe reparto",
    value=True
)

nuevo_backoffice = st.checkbox(
    "Es Backoffice"
)

if st.button("➕ Crear operador"):

    if nuevo_usuario.strip() == "":

        st.warning(
            "Debe ingresar un usuario."
        )

    else:

        conn = sqlite3.connect(
            "historico.db"
        )

        try:

            conn.execute(
                """
                INSERT INTO operadores
                (
                    usuario,
                    password,
                    activo,
                    recibe_reparto,
                    es_backoffice
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    nuevo_usuario.strip(),
                    nueva_password,
                    int(nuevo_activo),
                    int(nuevo_reparte),
                    int(nuevo_backoffice)
                )
            )

            conn.commit()

            st.success(
                "Operador creado correctamente"
            )

            st.rerun()

        except sqlite3.IntegrityError:

            st.error(
                "Ya existe un operador con ese usuario."
            )

        conn.close()
if st.button("💾 Guardar cambios"):

    for _, fila in editor.iterrows():

        conn.execute(
            """
            UPDATE operadores
            SET
                activo=?,
                recibe_reparto=?
            WHERE id=?
            """,
            (
                int(fila["activo"]),
                int(fila["recibe_reparto"]),
                int(fila["id"])
            )
        )

    conn.commit()

    st.success(
        "Cambios guardados"
    )

conn.close()