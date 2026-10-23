import streamlit as st
import pandas as pd
import sqlite3

# st.set_page_config(
#    page_title="Reasignación",
#    page_icon="🔄",
#    layout="wide"
#)

#conn = sqlite3.connect(
#    "historico.db"
#)

#usuario_actual = (
#    st.session_state.get("usuario")
#)

#permisos = pd.read_sql_query(
   # """
  #  SELECT es_backoffice
 #   FROM operadores
#    WHERE usuario = ?
  #  """,
 #   conn,
#    params=(usuario_actual,)
#)

#    conn.close()


st.title(
    "🔄 Reasignación de Servicios"
)

conn = sqlite3.connect(
    "historico.db"
)

df_casos = pd.read_sql_query(
    """
    SELECT
        nro_caso,
        fecha_traslado,
        operador,
        estado
    FROM historico_casos
    WHERE estado='PENDIENTE'
    """,
    conn
)

operadores_df = pd.read_sql_query(
    """
    SELECT usuario
    FROM operadores
    WHERE activo = 1
    AND es_backoffice = 0
    """,
    conn
)

conn.close()

operadores = (
    operadores_df["usuario"]
    .tolist()
)

st.subheader(
    "Casos pendientes"
)

reasignaciones = []

cab1, cab2, cab3, cab4 = st.columns(
    [3, 2, 2, 3]
)

cab1.markdown("**Caso**")
cab2.markdown("**Fecha Traslado**")
cab3.markdown("**Operador Actual**")
cab4.markdown("**Nuevo Operador**")

st.divider()

for _, fila in df_casos.iterrows():

    c1, c2, c3, c4 = st.columns(
        [3, 2, 2, 3]
    )

    with c1:
        st.write(
            fila["nro_caso"]
        )

    with c2:
        st.write(
            fila["fecha_traslado"]
        )

    with c3:
        st.write(
            fila["operador"]
        )

    with c4:

        nuevo_operador = st.selectbox(
            "",
            operadores,
            index=(
                operadores.index(
                    fila["operador"]
                )
                if fila["operador"] in operadores
                else 0
            ),
            key=f"op_{fila['nro_caso']}"
        )

        if nuevo_operador != fila["operador"]:

            reasignaciones.append(
                (
                    fila["nro_caso"],
                    nuevo_operador
                )
            )

if st.button(
    "💾 Aplicar reasignaciones"
):

    conn = sqlite3.connect(
        "historico.db"
    )

    for nro_caso, nuevo_operador in reasignaciones:

        conn.execute(
            """
            UPDATE historico_casos
            SET operador = ?
            WHERE nro_caso = ?
            """,
            (
                nuevo_operador,
                nro_caso
            )
        )

    conn.commit()
    conn.close()

    st.success(
        f"{len(reasignaciones)} casos reasignados"
    )

    st.rerun()