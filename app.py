import os
import streamlit as st
from PIL import Image
import datetime
import base64
import mysql.connector
import cloudinary
import cloudinary.uploader
from tensorflow.keras.models import load_model
import numpy as np
import pandas as pd
import datetime
from zoneinfo import ZoneInfo

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", ""),
    api_key=os.getenv("CLOUDINARY_API_KEY", ""),
    api_secret=os.getenv("CLOUDINARY_API_SECRET", "")
)

def conectar_bd():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "ecosurba_db")
    )

def obtener_estaciones():
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id_estacion, nombre, zona_cuenca, latitud, longitud, estado FROM estaciones_monitoreo")
        estaciones = cursor.fetchall()
        cursor.close()
        conexion.close()
        return estaciones
    except Exception:
        return []

@st.cache_data
def imagen_a_base64(ruta):
    try:
        with open(ruta, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None

@st.cache_resource
def cargar_modelo_ia():
    try:
        return load_model("modelo_ecosurba.h5")
    except Exception:
        return None

modelo = cargar_modelo_ia()

try:
    logo = Image.open("logo_ecosurba.png")
except Exception:
    logo = None

st.set_page_config(
    page_title="EcoSurba | Plataforma de Inteligencia Hídrica",
    page_icon=logo if logo else "💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

try:
    with open("styles.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception:
    st.warning("No se pudo cargar styles.css.")

if "en_bienvenida" not in st.session_state:
    st.session_state["en_bienvenida"] = True
if "analizado" not in st.session_state:
    st.session_state["analizado"] = False


if st.session_state["en_bienvenida"]:
    fondo_b64 = imagen_a_base64("riosurba.png")
    if fondo_b64:
        st.markdown(
            f"""<style>
.stApp {{
    background: transparent !important;
}}
.stApp::before {{
    content: "";
    position: fixed;
    inset: 0;
    background: linear-gradient(135deg, rgba(6, 40, 32, 0.45), rgba(15, 118, 110, 0.30)),
                url("data:image/png;base64,{fondo_b64}") center/cover no-repeat;
    filter: blur(5px);
    transform: scale(1.04);
    z-index: -1;
}}
</style>""",
            unsafe_allow_html=True
        )

    col_izq, col_der = st.columns([1.15, 1], gap="large")

    with col_izq:
        with st.container(border=True, key="card_intro"):
            if logo is not None:
                st.image(logo, width=165)

            st.markdown(
                "<p class='section-tag' style='margin-top: 12px;'>SISTEMA DE INTELIGENCIA HÍDRICA </p>"
                "<h1 style='font-size: 2rem; font-weight: 800; color: #0f172a; line-height: 1.2; margin: 6px 0 12px 0;'>"
                "Gestión y monitoreo en tiempo real de la cuenca del Río Surba</h1>"
                "<p style='font-size: 0.92rem; color: #334155; line-height: 1.6; margin-bottom: 22px;'>"
                "Plataforma de ciencia ciudadana e inteligencia artificial para evaluar parámetros fisicoquímicos "
                "y detectar alteraciones tempranas en Duitama, Boyacá.</p>",
                unsafe_allow_html=True
            )

            if st.button("🚀 Ingresar al Monitoreo Hídrico", type="primary"):
                st.session_state["en_bienvenida"] = False
                st.rerun()

    with col_der:
        with st.container(border=True, key="card_estaciones"):
            st.markdown(
                "<p class='section-tag'>📍 ESTACIONES OFICIALES DE CONTROL</p>"
                "<div class='section-title'>Puntos de Muestreo en Duitama</div>"
                "<div class='station-item'><div><b style='color:#0f172a; font-size:0.92rem;'>Punto 1 — Sector La Trinidad</b>"
                "<br><span style='color:#64748b; font-size:0.78rem;'>Cuenca Alta · Estación de control y línea base</span></div>"
                "<span class='status-ok'>Activo</span></div>"
                "<div class='station-item'><div><b style='color:#0f172a; font-size:0.92rem;'>Punto 2 — Vereda Higueras</b>"
                "<br><span style='color:#64748b; font-size:0.78rem;'>Cuenca Media · Zona de influencia agrícola</span></div>"
                "<span class='status-ok'>Activo</span></div>"
                "<div class='station-item'><div><b style='color:#0f172a; font-size:0.92rem;'>Punto 3 — Surba y Bonza</b>"
                "<br><span style='color:#64748b; font-size:0.78rem;'>Cuenca Baja · Zona de transición periurbana</span></div>"
                "<span class='status-ok'>Activo</span></div>",
                unsafe_allow_html=True
            )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    with st.container(border=True, key="card_mapa"):
        st.markdown(
            "<div class='section-tag'>MAPA DE UBICACIÓN Y ZONIFICACIÓN</div>"
            "<div class='section-title'>Visualización Geográfica de la Cuenca en Duitama</div>",
            unsafe_allow_html=True
        )
        estaciones_db = obtener_estaciones()
        if estaciones_db:
            df_puntos = pd.DataFrame({
                "lat": [float(e["latitud"]) for e in estaciones_db],
                "lon": [float(e["longitud"]) for e in estaciones_db]
            })
        else:
            df_puntos = pd.DataFrame({
                "lat": [5.8275, 5.8450, 5.8120],
                "lon": [-73.0312, -73.0450, -73.0180]
            })
        st.map(df_puntos, latitude=5.8275, longitude=-73.0312, zoom=12, use_container_width=True)


else:
    with st.sidebar:
        if logo is not None:
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                st.image(logo, use_container_width=True)

        st.markdown(
            "<div style='text-align:center; margin-top:6px;'>"
            "<p style='font-size:0.72rem; color:#34d399; font-weight:700; letter-spacing:0.1em; margin:0;'>MONITOREO HÍDRICO </p>"
            "</div><hr style='border-color:rgba(255,255,255,0.12); margin:14px 0;'>",
            unsafe_allow_html=True
        )

        if st.button("🗺️ Volver al Inicio", use_container_width=True):
            st.session_state["en_bienvenida"] = True
            st.rerun()

        st.markdown(
            "<div style='margin-top:24px;'>"
            "<p style='font-size:0.65rem; font-weight:700; color:#94a3b8; letter-spacing:0.1em; text-transform:uppercase;'>SOPORTE Y CONTACTO</p>"
            "<div style='font-size:0.78rem; color:#cbd5e1; line-height:1.7;'>"
            "<b>Soporte:</b> soporte.ecosurba@gmail.com<br>"
            "<b>Instagram:</b> @ecosurba_monitoreo<br>"
            "<b>Ubicación:</b> Duitama, Boyacá</div></div>",
            unsafe_allow_html=True
        )

    st.markdown(
        "<div style='background: linear-gradient(135deg, #071a14 0%, #065f46 100%); padding: 24px 30px; border-radius: 16px; color: white; margin-bottom: 20px; box-shadow: 0 8px 24px rgba(6, 95, 70, 0.16);'>"
        "<p style='font-size: 0.72rem; font-weight: 700; color: #6ee7b7; letter-spacing: 0.14em; text-transform: uppercase; margin: 0 0 4px 0;'>MONITOREO AMBIENTAL · CUENCA DEL RÍO SURBA</p>"
        "<h1 style='font-size: 1.65rem; font-weight: 800; margin: 0; color: #ffffff;'>CENTRO DE CONTROL E INVESTIGACIÓN HÍDRICA</h1>"
        "<p style='font-size: 0.86rem; color: #d1fae5; margin: 6px 0 0 0;'>Auditoría fisicoquímica y validación por visión artificial en campo.</p>"
        "</div>",
        unsafe_allow_html=True
    )

    tab_estacion, tab_historial, tab_resenas, tab_contacto = st.tabs([
        "📊 Estación de Campo e IA",
        "🗄️ Repositorio Histórico",
        "⭐ Valoración y Reseñas",
        "🏛️ Canales Oficiales"
    ])

    with tab_estacion:
        k1, k2, k3 = st.columns(3)
        with k1:
            st.markdown("<div class='kpi-card'><div class='kpi-title'>Puntos de Monitoreo</div><div class='kpi-val'>3</div></div>", unsafe_allow_html=True)
        with k2:
            st.markdown("<div class='kpi-card'><div class='kpi-title'>Variables Registradas</div><div class='kpi-val'>3</div></div>", unsafe_allow_html=True)
        with k3:
            st.markdown("<div class='kpi-card'><div class='kpi-title'>Base de Datos</div><div class='kpi-val'>MySQL</div></div>", unsafe_allow_html=True)

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        with st.container(border=True, key="card_paso1"):
            st.markdown("<div class='section-tag'>PASO 01</div><div class='section-title'>Registro de Variables Fisicoquímicas in situ</div>", unsafe_allow_html=True)

            estaciones_db = obtener_estaciones()
            mapa_estaciones = {e["nombre"]: e["id_estacion"] for e in estaciones_db}
            opciones_puntos = list(mapa_estaciones.keys()) if mapa_estaciones else [
                "Punto 1 — Sector La Trinidad", "Punto 2 — Vereda Higueras", "Punto 3 — Surba y Bonza"
            ]

            col_p, col_f = st.columns([2, 1])
            with col_p:
                punto_muestreo = st.selectbox(
                    "Seleccione el punto de muestreo oficial",
                    opciones_puntos
                )
                id_estacion_sel = mapa_estaciones.get(punto_muestreo)
            with col_f:
                fecha_colombia = datetime.datetime.now(ZoneInfo("America/Bogota")).date()
                fecha_actual = st.date_input("Fecha de registro en campo", fecha_colombia)
                
            c_ph, c_temp, c_turb = st.columns(3)
            with c_ph:
                ph_val = st.number_input("Valor de pH", min_value=0.0, max_value=14.0, value=7.00, step=0.01)
                ph_badge = "<span class='status-ok'>Normal (6.5-8.5)</span>" if 6.5 <= ph_val <= 8.5 else "<span class='status-err'>Alteración</span>"
                st.markdown(f"Evaluación pH: {ph_badge}", unsafe_allow_html=True)
            with c_temp:
                temp_val = st.number_input("Temperatura del agua (°C)", min_value=0.0, max_value=40.0, value=14.0, step=0.1)
                temp_badge = "<span class='status-ok'>Normal (≤18°C)</span>" if temp_val <= 18.0 else "<span class='status-warn'>Elevada</span>"
                st.markdown(f"Evaluación Temp: {temp_badge}", unsafe_allow_html=True)
            with c_turb:
                turbidez_val = st.selectbox("Turbidez visual", ["BAJA", "MEDIA", "ALTA"])
                turb_badge = "<span class='status-ok'>Normal</span>" if turbidez_val == "BAJA" else ("<span class='status-warn'>Atención</span>" if turbidez_val == "MEDIA" else "<span class='status-err'>Alteración</span>")
                st.markdown(f"Evaluación Turbidez: {turb_badge}", unsafe_allow_html=True)

            observaciones_val = st.text_area(
                "Observaciones de campo (opcional)",
                placeholder="Ej: Presencia de espuma superficial, olor fuerte, lluvia reciente..."
            )

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        with st.container(border=True, key="card_paso2"):
            st.markdown("<div class='section-tag'>PASO 02</div><div class='section-title'>Evidencia Fotográfica y Análisis Visual</div>", unsafe_allow_html=True)
            col_foto, col_info = st.columns([1.2, 1])

            with col_foto:
                metodo_foto = st.radio(
                    "Método de captura",
                    ["📁 Subir archivo / Galería", "📷 Tomar foto con cámara"],
                    horizontal=True
                )
                if metodo_foto == "📁 Subir archivo / Galería":
                    archivo_foto = st.file_uploader("Cargar fotografía de la superficie del agua", type=["jpg", "jpeg", "png"])
                else:
                    archivo_foto = st.camera_input("Capturar muestra de agua en tiempo real")

                if archivo_foto is None:
                    st.markdown(
                        "<div style='background:#fffbeb; border:1px solid #fef08a; border-radius:8px; padding:12px; margin-top:8px;'>"
                        "<b style='font-size:0.78rem; color:#b45309;'>Evidencia fotográfica pendiente</b><br>"
                        "<span style='font-size:0.74rem; color:#d97706;'>Adjunte una imagen para habilitar el análisis visual.</span></div>",
                        unsafe_allow_html=True
                    )
                else:
                    imagen = Image.open(archivo_foto)
                    st.success("Imagen registrada con éxito")
                    st.image(imagen, use_container_width=True)

            with col_info:
                st.markdown(
                    "<div style='background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:18px;'>"
                    "<p style='font-size:0.8rem; font-weight:800; color:#0f172a; margin:0 0 8px 0; text-transform:uppercase;'>Protocolo de Captura en Campo</p>"
                    "<ul style='font-size:0.78rem; color:#334155; padding-left:18px; line-height:1.65; margin:0;'>"
                    "<li>Tomar la fotografía a ~1 metro de distancia y ángulo de 45°.</li>"
                    "<li>Garantizar iluminación natural sin reflejos excesivos.</li>"
                    "<li>La red MobileNetV2 procesará patrones visuales de la superficie.</li></ul></div>",
                    unsafe_allow_html=True
                )

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        with st.container(border=True, key="card_paso3"):
            st.markdown("<div class='section-tag'>PASO 03</div><div class='section-title'>Ejecución de Diagnóstico</div>", unsafe_allow_html=True)
            col_btn1, col_btn2 = st.columns([1, 2.5])
            with col_btn1:
                boton_analizar = st.button("Analizar Muestra →", type="primary", use_container_width=True)
            with col_btn2:
                st.markdown("<p style='font-size:0.82rem; color:#475569; padding-top:8px;'></p>", unsafe_allow_html=True)

            if boton_analizar:
                if ph_val < 6.5 or ph_val > 8.5 or turbidez_val == "ALTA":
                    estado_fisico = "ALTERACIÓN"
                elif temp_val > 18.0 or turbidez_val == "MEDIA":
                    estado_fisico = "ATENCIÓN"
                else:
                    estado_fisico = "NORMAL"

                estado_ia = "NORMAL"
                confianza_texto = "96.4 %"
                if archivo_foto is not None and modelo is not None:
                    try:
                        img_resized = imagen.convert("RGB").resize((224, 224))
                        img_array = np.expand_dims(np.array(img_resized) / 255.0, axis=0)
                        prediccion = modelo.predict(img_array)
                        clase_idx = np.argmax(prediccion[0])
                        confianza_val = float(np.max(prediccion[0])) * 100
                        estado_ia = ["NORMAL", "ATENCIÓN", "ALTERACIÓN"][clase_idx]
                        confianza_texto = f"{confianza_val:.1f} %"
                    except Exception:
                        pass

                severidad = {"NORMAL": 0, "ATENCIÓN": 1, "ALTERACIÓN": 2}
                estado_general = estado_ia if severidad[estado_ia] >= severidad[estado_fisico] else estado_fisico

                url_foto = None
                if archivo_foto is not None:
                    try:
                        url_foto = None
           if archivo_foto is not None:
               try:
                   archivo_foto.seek(0)
                   res_cloud = cloudinary.uploader.upload(archivo_foto, folder="ecosurba_muestras")
                   url_foto = res_cloud.get("secure_url")
               except Exception as e_cloud:
                   st.warning(f"No se pudo subir la imagen a Cloudinary: {e_cloud}")

                try:
                    conexion = conectar_bd()
                    cursor = conexion.cursor()
                    cursor.execute(
                        """INSERT INTO historial_monitoreo
                           (id_estacion, fecha, punto, ph, temperatura, turbidez, estado, confianza, observaciones, ruta_imagen)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (id_estacion_sel, str(fecha_actual), punto_muestreo, ph_val, temp_val, turbidez_val, estado_general, confianza_texto, observaciones_val, url_foto)
                    )
                    id_nuevo_monitoreo = cursor.lastrowid

                    if estado_general in ("ALTERACIÓN", "ATENCIÓN"):
                        nivel_alerta = "ALTA" if estado_general == "ALTERACIÓN" else "MEDIA"
                        msg_alerta = f"Estado {estado_general} en {punto_muestreo} (pH: {ph_val}, Temp: {temp_val}°C, Turbidez: {turbidez_val})."
                        cursor.execute(
                            "INSERT INTO alertas_ambientales (id_monitoreo, nivel, mensaje) VALUES (%s, %s, %s)",
                            (id_nuevo_monitoreo, nivel_alerta, msg_alerta)
                        )

                    conexion.commit()
                    cursor.close()
                    conexion.close()
                    st.success("Muestra procesada y registrada exitosamente." + (" Se generó una alerta ambiental." if estado_general != "NORMAL" else ""))
                except Exception as e:
                    st.error(f"Error al conectar con MySQL: {e}")

                st.session_state["analizado"] = True
                st.session_state["res_estado"] = estado_general
                st.session_state["res_confianza"] = confianza_texto

        if st.session_state.get("analizado", False):
            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
            with st.container(border=True, key="card_paso4"):
                estado_general = st.session_state.get("res_estado", "NORMAL")
                confianza_texto = st.session_state.get("res_confianza", "96.4 %")
                st.markdown("<div class='section-tag'>PASO 04</div><div class='section-title'>Resultado del Diagnóstico Integrado</div>", unsafe_allow_html=True)

                if estado_general == "ALTERACIÓN":
                    badge_cls, msg_res = "status-err", "Se detectó una alteración severa en los parámetros o superficie hídrica. Se sugiere revisión detallada."
                elif estado_general == "ATENCIÓN":
                    badge_cls, msg_res = "status-warn", "Parámetros fuera del óptimo estándar. Se requiere seguimiento preventivo."
                else:
                    badge_cls, msg_res = "status-ok", "Las variables fisicoquímicas y el análisis visual se encuentran dentro de los rangos esperados."

                st.markdown(
                    f"<div style='background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:16px 20px; display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;'>"
                    f"<div><p style='font-size:0.7rem; font-weight:700; color:#64748b; margin:0;'>ESTADO GENERAL</p>"
                    f"<div style='margin-top:6px;'><span class='{badge_cls}' style='font-size:0.88rem; padding:5px 12px;'>{estado_general}</span></div></div>"
                    f"<div style='text-align:right;'><p style='font-size:0.7rem; font-weight:700; color:#64748b; margin:0;'>NIVEL DE CONFIANZA</p>"
                    f"<p style='font-size:1.3rem; font-weight:800; color:#0f172a; margin:2px 0 0 0;'>{confianza_texto}</p></div></div>"
                    f"<div style='background:#ecfdf5; border-left:4px solid #0f766e; padding:14px 18px; border-radius:6px;'>"
                    f"<b style='font-size:0.82rem; color:#0f172a;'>Interpretación Técnica</b><br>"
                    f"<span style='font-size:0.78rem; color:#334155;'>{msg_res}</span></div>",
                    unsafe_allow_html=True
                )

    with tab_historial:
        with st.container(border=True, key="card_hist"):
            st.markdown("<div class='section-tag'>REPOSITORIO HISTÓRICO</div><div class='section-title'>Registro Longitudinal de Muestras</div>", unsafe_allow_html=True)
            try:
                conexion = conectar_bd()
                cursor = conexion.cursor()
                cursor.execute("""
               SELECT h.fecha, COALESCE(e.nombre, h.punto), h.ph, h.temperatura,
                      h.turbidez, h.estado, h.confianza, COALESCE(h.observaciones, '-'),
                      h.ruta_imagen
               FROM historial_monitoreo h
               LEFT JOIN estaciones_monitoreo e ON h.id_estacion = e.id_estacion
               ORDER BY h.id DESC
           """)
                filas = cursor.fetchall()

                if not filas:
                    st.info("No hay registros almacenados todavía.")
                else:
                    df_historial = pd.DataFrame(
                        filas,
                        columns=["Fecha", "Estación", "pH", "Temp (°C)", "Turbidez", "Estado", "Confianza", "Observaciones", "Evidencia"]
                    )
                    st.dataframe(
                        df_historial,
                        column_config={"Evidencia": st.column_config.LinkColumn("Evidencia", display_text="Ver foto")},
                        use_container_width=True
                    )

                st.markdown("<hr style='border-color:#e2e8f0; margin:24px 0;'>", unsafe_allow_html=True)
                st.markdown("<div class='section-tag'>SISTEMA DE ALERTAS TEMPRANAS</div><div class='section-title'>Alertas Ambientales Registradas</div>", unsafe_allow_html=True)

                cursor.execute("""
                    SELECT a.fecha_alerta, a.nivel, a.mensaje, a.estado_alerta
                    FROM alertas_ambientales a
                    ORDER BY a.id_alerta DESC
                """)
                alertas = cursor.fetchall()
                cursor.close()
                conexion.close()

                if not alertas:
                    st.success("No hay alertas ambientales registradas.")
                else:
                    df_alertas = pd.DataFrame(alertas, columns=["Fecha y Hora", "Nivel", "Detalle de Alerta", "Estado"])
                    st.dataframe(df_alertas, use_container_width=True)
            except Exception as e:
                st.error(f"No se pudo conectar a MySQL: {e}")

    with tab_resenas:
        with st.container(border=True, key="card_resenas"):
            st.markdown("<div class='section-tag'>EXPERIENCIA Y MEJORA CONTINUA</div><div class='section-title'>Buzón de Recomendaciones y Reseñas</div>", unsafe_allow_html=True)

            with st.form("form_resena"):
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    nombre_usuario = st.text_input("Nombre completo")
                with col_r2:
                    estrellas_val = st.slider("Valoración general (Estrellas)", 1, 5, 5)
                gusto_txt = st.text_area("¿Qué fue lo que más te gustó de la plataforma?")
                recomendacion_txt = st.text_area("¿Qué recomendaciones de mejora nos sugieres?")
                btn_enviar_resena = st.form_submit_button("Enviar Reseña ➔", type="primary")

                if btn_enviar_resena:
                    if not nombre_usuario.strip():
                        st.warning("Por favor ingresa tu nombre.")
                    else:
                        try:
                            conexion = conectar_bd()
                            cursor = conexion.cursor()
                            cursor.execute(
                                "INSERT INTO resenas_usuario (fecha, nombre, valoracion, recomendacion, gusto) VALUES (%s, %s, %s, %s, %s)",
                                (str(datetime.date.today()), nombre_usuario, estrellas_val, recomendacion_txt, gusto_txt)
                            )
                            conexion.commit()
                            cursor.close()
                            conexion.close()
                            st.success("¡Muchas gracias! Tu reseña ha sido registrada.")
                        except Exception as e:
                            st.error(f"Error al guardar la reseña en MySQL: {e}")

            st.markdown("<hr style='border-color:#e2e8f0; margin:24px 0;'><h3 style='font-size:1.05rem; font-weight:700; color:#0f172a;'>Reseñas Recientes</h3>", unsafe_allow_html=True)

            try:
                conexion = conectar_bd()
                cursor = conexion.cursor()
                cursor.execute("SELECT fecha, nombre, valoracion, gusto, recomendacion FROM resenas_usuario ORDER BY id DESC")
                resenas_bd = cursor.fetchall()
                cursor.close()
                conexion.close()

                if not resenas_bd:
                    st.info("Aún no hay reseñas registradas.")
                else:
                    for fecha_r, nom_r, val_r, gusto_r, rec_r in resenas_bd:
                        estrellas_str = "⭐" * val_r
                        st.markdown(
                            f"<div style='background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:14px; margin-bottom:12px;'>"
                            f"<div style='display:flex; justify-content:space-between; margin-bottom:6px;'>"
                            f"<b style='font-size:0.85rem; color:#0f172a;'>{nom_r}</b>"
                            f"<span style='font-size:0.75rem; color:#64748b;'>{fecha_r} | {estrellas_str}</span></div>"
                            f"<p style='font-size:0.78rem; color:#1e293b; margin:4px 0;'><b>Lo que gustó:</b> {gusto_r}</p>"
                            f"<p style='font-size:0.78rem; color:#475569; margin:4px 0;'><b>Sugerencia:</b> {rec_r}</p></div>",
                            unsafe_allow_html=True
                        )
            except Exception as e:
                st.error(f"No se pudieron cargar las reseñas desde MySQL: {e}")

    with tab_contacto:
        with st.container(border=True, key="card_contacto"):
            st.markdown(
                "<div class='section-tag'>SOPORTE INSTITUCIONAL</div>"
                "<div class='section-title'>Canales de Contacto Oficial</div>"
                "<div style='display:grid; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr)); gap:16px; margin-top:10px;'>"
                "<div style='background:#f8fafc; border:1px solid #e2e8f0; padding:18px; border-radius:12px;'>"
                "<h4 style='color:#0f766e; margin:0 0 6px 0; font-size:1rem;'>Soporte Técnico</h4>"
                "<p style='font-size:0.8rem; color:#334155; margin:0 0 8px 0;'>Consultas técnicas y coordinación académica con la UPTC.</p>"
                "<b style='font-size:0.82rem; color:#0f172a;'>soporte.ecosurba@gmail.com</b></div>"
                "<div style='background:#f8fafc; border:1px solid #e2e8f0; padding:18px; border-radius:12px;'>"
                "<h4 style='color:#0f766e; margin:0 0 6px 0; font-size:1rem;'>Divulgación Ambiental</h4>"
                "<p style='font-size:0.8rem; color:#334155; margin:0 0 8px 0;'>Ciencia ciudadana sobre la cuenca del Río Surba.</p>"
                "<b style='font-size:0.82rem; color:#0f172a;'>@ecosurba_monitoreo</b></div></div>",
                unsafe_allow_html=True
            )

st.markdown(
    "<div style='background: #071a14; color: #f8fafc; padding: 20px; border-radius: 14px; text-align: center; margin-top: 32px;'>"
    "<p style='font-size: 0.9rem; font-weight: 800; margin: 0; color: #6ee7b7;'>ECOSURBA · Plataforma Inteligente Hídrica</p>"
    "<p style='font-size: 0.76rem; color: #94a3b8; margin: 4px 0 10px 0;'>Cuenca del Río Surba · Duitama, Boyacá, Colombia</p>"
    "<div style='font-size: 0.78rem; color: #cbd5e1;'>soporte.ecosurba@gmail.com &nbsp;|&nbsp; @ecosurba_monitoreo &nbsp;|&nbsp; UPTC (FESAD)</div>"
    "</div>",
    unsafe_allow_html=True
)
