import streamlit as st
import pandas as pd
from datetime import datetime
import re
import io
import hashlib
import requests
from urllib.parse import urlparse
import json

# Configuración de la página
st.set_page_config(
    page_title="🏊‍♂️ Gestión Nadadores C.N.L.P",
    page_icon="🏊‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============== CONFIGURACIÓN ==============

def hash_password(password):
    """Hashea la contraseña para almacenamiento seguro"""
    return hashlib.sha256(password.encode()).hexdigest()

# USUARIOS Y PERMISOS - Inicialización
def initialize_users():
    if 'users_data' not in st.session_state:
        st.session_state.users_data = {
            "admin": {
                "password": hash_password("admin123"),
                "role": "admin",
                "name": "Administrador Principal",
                "active": True
            },
            "entrenador": {
                "password": hash_password("entrenador123"),
                "role": "entrenador", 
                "name": "Entrenador Principal",
                "active": True
            },
            "asistente": {
                "password": hash_password("asistente123"),
                "role": "asistente",
                "name": "Asistente",
                "active": True
            }
        }

# TABLA DE CONVERSIÓN DE TIEMPOS
CONVERSION_DATA = {
    "increments": {
        "Libre": 80, "Espalda": 60, "Braza": 100, "Mariposa": 70, "Estilos": 80
    },
    "multipliers": {
        50: 1, 100: 2, 200: 4, 400: 8, 800: 16, 1500: 30, 3000: 60
    },
    "special": {800: 1280, 1500: 2400}
}

# Lista de pruebas
PRUEBAS = [
    "50m Libre", "100m Libre", "200m Libre", "400m Libre", 
    "800m Libre", "1500m Libre", "3000m Libre",
    "50m Espalda", "100m Espalda", "200m Espalda",
    "50m Braza", "100m Braza", "200m Braza",
    "50m Mariposa", "100m Mariposa", "200m Mariposa",
    "100m Estilos", "200m Estilos"
]

# ============== AUTENTICACIÓN Y GESTIÓN DE USUARIOS ==============

def check_authentication():
    """Sistema de autenticación"""
    initialize_users()
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        show_login()
        return False
    else:
        show_user_info()
        return True

def show_login():
    """Formulario de login"""
    st.markdown("# 🏊‍♂️ Club Natación Las Palmas")
    st.markdown("### 🔐 Sistema Integral de Gestión")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("#### Iniciar Sesión")
        
        username = st.text_input("👤 Usuario")
        password = st.text_input("🔑 Contraseña", type="password")
        
        if st.button("🚀 Entrar", type="primary"):
            users = st.session_state.users_data
            if username in users and users[username].get('active', True):
                hashed_password = hash_password(password)
                if hashed_password == users[username]["password"]:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.user_role = users[username]["role"]
                    st.session_state.user_name = users[username]["name"]
                    st.success("✅ Acceso correcto")
                    st.rerun()
                else:
                    st.error("❌ Contraseña incorrecta")
            elif username in users and not users[username].get('active', True):
                st.error("❌ Usuario desactivado")
            else:
                st.error("❌ Usuario no encontrado")
    
    with st.expander("👥 Usuarios del Sistema"):
        users = st.session_state.users_data
        for username, user_data in users.items():
            if user_data.get('active', True):
                st.markdown(f"""
                **{user_data['name']}** (`{username}`)
                - Rol: {user_data['role'].title()}
                - Estado: {'🟢 Activo' if user_data.get('active', True) else '🔴 Inactivo'}
                """)

def show_user_info():
    """Información del usuario en sidebar"""
    with st.sidebar:
        st.success(f"👤 **{st.session_state.user_name}**")
        role_icons = {"admin": "👑", "entrenador": "🏋️", "asistente": "👀"}
        icon = role_icons.get(st.session_state.user_role, "👤")
        st.info(f"{icon} **{st.session_state.user_role.title()}**")
        
        if st.button("🚪 Cerrar Sesión"):
            for key in ['authenticated', 'username', 'user_role', 'user_name']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

def has_permission(action):
    """Sistema de permisos"""
    if not st.session_state.get('authenticated', False):
        return False
    
    role = st.session_state.get('user_role', 'asistente')
    
    permissions = {
        'admin': ['view', 'edit', 'delete', 'upload', 'download', 'convert', 'user_management'],
        'entrenador': ['view', 'edit', 'upload', 'download', 'convert'],
        'asistente': ['view']
    }
    
    return action in permissions.get(role, [])

def show_user_management():
    """Panel de gestión de usuarios (solo admin)"""
    if not has_permission('user_management'):
        st.error("❌ Sin permisos para gestión de usuarios")
        return
    
    st.header("👥 Gestión de Usuarios")
    
    # Lista de usuarios actuales
    st.subheader("📋 Usuarios Actuales")
    users_df = []
    for username, user_data in st.session_state.users_data.items():
        users_df.append({
            'Usuario': username,
            'Nombre': user_data['name'],
            'Rol': user_data['role'].title(),
            'Estado': '🟢 Activo' if user_data.get('active', True) else '🔴 Inactivo'
        })
    
    if users_df:
        st.dataframe(pd.DataFrame(users_df), use_container_width=True)
    
    # Gestión por pestañas
    tab1, tab2, tab3 = st.tabs(["🔑 Cambiar Contraseñas", "➕ Nuevo Usuario", "⚙️ Modificar Usuario"])
    
    with tab1:
        st.markdown("**🔑 Cambiar Contraseña de Usuario**")
        
        with st.form("change_password"):
            col1, col2 = st.columns(2)
            
            with col1:
                target_user = st.selectbox("Usuario", list(st.session_state.users_data.keys()))
                new_password = st.text_input("Nueva Contraseña", type="password")
            
            with col2:
                confirm_password = st.text_input("Confirmar Contraseña", type="password")
                st.write("") # Espaciado
                st.write("") # Espaciado
            
            if st.form_submit_button("🔄 Cambiar Contraseña", type="primary"):
                if new_password and new_password == confirm_password:
                    if len(new_password) >= 6:
                        st.session_state.users_data[target_user]["password"] = hash_password(new_password)
                        st.success(f"✅ Contraseña cambiada para {target_user}")
                        st.rerun()
                    else:
                        st.error("❌ La contraseña debe tener al menos 6 caracteres")
                else:
                    st.error("❌ Las contraseñas no coinciden")
    
    with tab2:
        st.markdown("**➕ Crear Nuevo Usuario**")
        
        with st.form("new_user"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input("Nombre de Usuario")
                new_name = st.text_input("Nombre Completo")
                new_role = st.selectbox("Rol", ["admin", "entrenador", "asistente"])
            
            with col2:
                new_pass = st.text_input("Contraseña", type="password")
                confirm_new_pass = st.text_input("Confirmar Contraseña", type="password")
                new_active = st.checkbox("Usuario Activo", value=True)
            
            if st.form_submit_button("➕ Crear Usuario", type="primary"):
                if new_username and new_name and new_pass:
                    if new_username not in st.session_state.users_data:
                        if new_pass == confirm_new_pass and len(new_pass) >= 6:
                            st.session_state.users_data[new_username] = {
                                "password": hash_password(new_pass),
                                "role": new_role,
                                "name": new_name,
                                "active": new_active
                            }
                            st.success(f"✅ Usuario {new_username} creado exitosamente")
                            st.rerun()
                        else:
                            st.error("❌ Contraseñas no coinciden o muy cortas (mín. 6 caracteres)")
                    else:
                        st.error("❌ El usuario ya existe")
                else:
                    st.error("❌ Todos los campos son obligatorios")
    
    with tab3:
        st.markdown("**⚙️ Modificar Usuario Existente**")
        
        with st.form("modify_user"):
            col1, col2 = st.columns(2)
            
            with col1:
                modify_user = st.selectbox("Seleccionar Usuario", list(st.session_state.users_data.keys()))
                if modify_user:
                    current_data = st.session_state.users_data[modify_user]
                    modify_name = st.text_input("Nombre Completo", value=current_data['name'])
                    modify_role = st.selectbox("Rol", ["admin", "entrenador", "asistente"], 
                                             index=["admin", "entrenador", "asistente"].index(current_data['role']))
            
            with col2:
                if modify_user:
                    modify_active = st.checkbox("Usuario Activo", value=current_data.get('active', True))
                    st.warning("⚠️ Cambiar el rol o desactivar un usuario afectará sus permisos")
            
            col_update, col_delete = st.columns([3, 1])
            
            with col_update:
                if st.form_submit_button("💾 Actualizar Usuario", type="primary"):
                    if modify_user and modify_name:
                        st.session_state.users_data[modify_user]["name"] = modify_name
                        st.session_state.users_data[modify_user]["role"] = modify_role
                        st.session_state.users_data[modify_user]["active"] = modify_active
                        st.success(f"✅ Usuario {modify_user} actualizado")
                        st.rerun()
                    else:
                        st.error("❌ Nombre es obligatorio")
            
            with col_delete:
                if st.form_submit_button("🗑️ Eliminar", type="secondary"):
                    if modify_user != "admin":  # Proteger cuenta admin principal
                        if st.session_state.get('confirm_user_delete', '') == modify_user:
                            del st.session_state.users_data[modify_user]
                            st.success(f"✅ Usuario {modify_user} eliminado")
                            st.rerun()
                        else:
                            st.session_state.confirm_user_delete = modify_user
                            st.warning("⚠️ Haz clic otra vez para confirmar eliminación")
                    else:
                        st.error("❌ No se puede eliminar la cuenta admin principal")

# ============== GESTIÓN DE DATOS ==============

def load_google_sheets(url):
    """Cargar datos desde Google Sheets"""
    try:
        if 'docs.google.com/spreadsheets' in url:
            doc_id = url.split('/d/')[1].split('/')[0]
            csv_url = f"https://docs.google.com/spreadsheets/d/{doc_id}/export?format=xlsx"
            
            response = requests.get(csv_url)
            if response.status_code == 200:
                return pd.ExcelFile(io.BytesIO(response.content))
            else:
                raise Exception(f"Error al acceder a Google Sheets: {response.status_code}")
        else:
            raise Exception("URL no válida de Google Sheets")
    except Exception as e:
        raise Exception(f"Error al cargar Google Sheets: {str(e)}")

def load_data_source():
    """Gestión unificada de fuentes de datos"""
    st.header("📊 Fuente de Datos")
    
    source_type = st.radio(
        "Selecciona la fuente de datos:",
        ["📁 Archivo Local", "🌐 Google Sheets Online"],
        horizontal=True
    )
    
    excel_file = None
    
    if source_type == "📁 Archivo Local":
        uploaded_file = st.file_uploader(
            "Selecciona archivo Excel",
            type=['xlsx', 'xls'],
            help="Archivo Excel con múltiples hojas (temporadas)"
        )
        if uploaded_file:
            excel_file = pd.ExcelFile(uploaded_file)
            
    else:  # Google Sheets
        if has_permission('upload'):
            st.markdown("**📋 Instrucciones para Google Sheets:**")
            st.markdown("1. Abre tu Google Sheets")
            st.markdown("2. Ve a **Archivo → Compartir → Compartir con otros**")
            st.markdown("3. Cambia a **'Cualquier persona con el enlace puede ver'**")
            st.markdown("4. Copia y pega la URL completa aquí")
            
            sheets_url = st.text_input(
                "🔗 URL de Google Sheets",
                placeholder="https://docs.google.com/spreadsheets/d/tu-id-aqui/edit...",
                help="Pega la URL completa de tu Google Sheets"
            )
            
            if sheets_url and st.button("🔄 Conectar con Google Sheets", type="primary"):
                with st.spinner("Conectando con Google Sheets..."):
                    try:
                        excel_file = load_google_sheets(sheets_url)
                        st.session_state.sheets_url = sheets_url
                        st.success("✅ Conectado exitosamente con Google Sheets")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        
            if 'sheets_url' in st.session_state and st.button("🔄 Actualizar desde Google Sheets"):
                with st.spinner("Actualizando datos..."):
                    try:
                        excel_file = load_google_sheets(st.session_state.sheets_url)
                        st.success("✅ Datos actualizados desde Google Sheets")
                    except Exception as e:
                        st.error(f"❌ Error al actualizar: {str(e)}")
        else:
            st.warning("⚠️ Sin permisos para conectar fuentes externas")
    
    return excel_file

# ============== CONVERSOR DE TIEMPOS MASIVO ==============

class TimeConverter:
    """Conversor de tiempos entre piscinas"""
    
    def time_to_centesimas(self, time_str):
        """Convierte tiempo a centésimas"""
        try:
            time_str = str(time_str).strip().replace(',', '.')
            if ':' in time_str:
                parts = time_str.split(':')
                if len(parts) == 3:  # hh:mm:ss.cc
                    hours, minutes, seconds = int(parts[0]), int(parts[1]), float(parts[2])
                    return int((hours * 3600 + minutes * 60 + seconds) * 100)
                else:  # mm:ss.cc
                    minutes, seconds = int(parts[0]), float(parts[1])
                    return int((minutes * 60 + seconds) * 100)
            else:  # ss.cc
                return int(float(time_str) * 100)
        except:
            return None
    
    def centesimas_to_time(self, centesimas):
        """Convierte centésimas a tiempo"""
        try:
            total_seconds = centesimas / 100
            minutes = int(total_seconds // 60)
            seconds = total_seconds % 60
            return f"{minutes:02d}:{seconds:05.2f}"
        except:
            return None
    
    def get_style_distance(self, prueba):
        """Extrae estilo y distancia de la prueba"""
        try:
            parts = prueba.split(' ')
            distance = int(parts[0].replace('m', ''))
            style = parts[1]
            return style, distance
        except:
            return "Libre", 50
    
    def convert_time(self, time_original, pool_from, pool_to, style, distance):
        """Convierte tiempo entre piscinas"""
        if pool_from == pool_to:
            return time_original
        
        centesimas = self.time_to_centesimas(time_original)
        if centesimas is None:
            return time_original
        
        base_increment = CONVERSION_DATA["increments"].get(style, 80)
        
        if distance in CONVERSION_DATA["special"]:
            total_increment = CONVERSION_DATA["special"][distance]
        else:
            multiplier = CONVERSION_DATA["multipliers"].get(distance, 1)
            total_increment = base_increment * multiplier
        
        if pool_from == "25m" and pool_to == "50m":
            converted_centesimas = centesimas + total_increment
        elif pool_from == "50m" and pool_to == "25m":
            converted_centesimas = centesimas - total_increment
        else:
            return time_original
        
        return self.centesimas_to_time(converted_centesimas) or time_original

def show_mass_conversion():
    """Sistema de conversión masiva"""
    if not has_permission('convert'):
        st.error("❌ Sin permisos para conversión de tiempos")
        return
    
    if 'df' not in st.session_state:
        st.warning("⚠️ Carga primero una temporada para convertir tiempos")
        return
    
    st.header("🔄 Conversión Masiva de Tiempos")
    st.markdown("### Convierte todos los tiempos de todos los nadadores de una vez")
    
    converter = TimeConverter()
    df = st.session_state.df.copy()
    
    # Configuración de conversión
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚙️ Configuración")
        target_pool = st.selectbox(
            "🏊‍♂️ Convertir todos los tiempos a:",
            ["50m (Piscina Larga)", "25m (Piscina Corta)"],
            help="Se convertirán todos los tiempos que no estén ya en esta piscina"
        )
        
        target_pool_type = "50m" if "50m" in target_pool else "25m"
        
        # Detectar qué tiempos se pueden convertir
        convertible_times = 0
        total_times = 0
        
        for prueba in PRUEBAS:
            if prueba in df.columns:
                piscina_col = f"{prueba}Piscina"
                for idx, row in df.iterrows():
                    tiempo = row.get(prueba, '')
                    piscina = row.get(piscina_col, '')
                    
                    if pd.notna(tiempo) and str(tiempo).strip():
                        total_times += 1
                        if pd.notna(piscina) and str(piscina).strip():
                            piscina_str = str(piscina).strip()
                            if ("25" in piscina_str and target_pool_type == "50m") or \
                               ("50" in piscina_str and target_pool_type == "25m"):
                                convertible_times += 1
        
        st.info(f"📊 **Análisis:**")
        st.info(f"• Total de tiempos: {total_times}")
        st.info(f"• Convertibles: {convertible_times}")
        st.info(f"• Ya en {target_pool_type}: {total_times - convertible_times}")
    
    with col2:
        st.subheader("📋 Vista Previa")
        
        if st.checkbox("🔍 Mostrar tiempos que se convertirán"):
            preview_data = []
            
            for prueba in PRUEBAS[:5]:  # Solo mostrar las primeras 5 pruebas como ejemplo
                if prueba in df.columns:
                    piscina_col = f"{prueba}Piscina"
                    for idx, row in df.iterrows():
                        tiempo = row.get(prueba, '')
                        piscina = row.get(piscina_col, '')
                        nombre = row.get('Nombre', 'Sin nombre')
                        
                        if pd.notna(tiempo) and str(tiempo).strip() and pd.notna(piscina):
                            piscina_str = str(piscina).strip()
                            if ("25" in piscina_str and target_pool_type == "50m") or \
                               ("50" in piscina_str and target_pool_type == "25m"):
                                style, distance = converter.get_style_distance(prueba)
                                converted_time = converter.convert_time(
                                    str(tiempo), piscina_str, target_pool_type, style, distance
                                )
                                
                                preview_data.append({
                                    'Nadador': nombre,
                                    'Prueba': prueba,
                                    'Tiempo Original': f"{tiempo} ({piscina_str})",
                                    'Tiempo Convertido': f"{converted_time} ({target_pool_type})"
                                })
                                
                                if len(preview_data) >= 10:  # Limitar vista previa
                                    break
                    if len(preview_data) >= 10:
                        break
            
            if preview_data:
                st.dataframe(pd.DataFrame(preview_data), use_container_width=True)
                if len(preview_data) >= 10:
                    st.info("... y más (mostrando solo los primeros 10)")
            else:
                st.info("No hay tiempos para convertir")
    
    # Botón de conversión
    st.markdown("---")
    
    if convertible_times > 0:
        col_convert, col_info = st.columns([2, 1])
        
        with col_convert:
            if st.button(f"🔄 Convertir {convertible_times} tiempos a {target_pool_type}", 
                        type="primary", use_container_width=True):
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                converted_count = 0
                total_to_convert = convertible_times
                
                # Crear DataFrame convertido
                df_converted = df.copy()
                
                for i, prueba in enumerate(PRUEBAS):
                    if prueba in df_converted.columns:
                        piscina_col = f"{prueba}Piscina"
                        
                        for idx, row in df_converted.iterrows():
                            tiempo = row.get(prueba, '')
                            piscina = row.get(piscina_col, '')
                            
                            if pd.notna(tiempo) and str(tiempo).strip() and pd.notna(piscina):
                                piscina_str = str(piscina).strip()
                                
                                # Determinar si necesita conversión
                                needs_conversion = False
                                if ("25" in piscina_str and target_pool_type == "50m") or \
                                   ("50" in piscina_str and target_pool_type == "25m"):
                                    needs_conversion = True
                                
                                if needs_conversion:
                                    style, distance = converter.get_style_distance(prueba)
                                    converted_time = converter.convert_time(
                                        str(tiempo), piscina_str, target_pool_type, style, distance
                                    )
                                    
                                    # Actualizar datos
                                    df_converted.at[idx, prueba] = converted_time
                                    df_converted.at[idx, piscina_col] = target_pool_type
                                    
                                    converted_count += 1
                                    
                                    # Actualizar progreso
                                    progress = converted_count / total_to_convert
                                    progress_bar.progress(progress)
                                    status_text.text(f"Convirtiendo: {converted_count}/{total_to_convert}")
                
                # Guardar resultado en session state
                st.session_state.df_converted = df_converted
                st.session_state.conversion_info = {
                    'target_pool': target_pool_type,
                    'converted_count': converted_count,
                    'total_times': total_times,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                progress_bar.progress(1.0)
                status_text.text("✅ Conversión completada")
                
                st.success(f"🎉 **Conversión exitosa!**")
                st.success(f"✅ {converted_count} tiempos convertidos a {target_pool_type}")
                st.info("📥 Ahora puedes descargar el Excel con los tiempos convertidos")
        
        with col_info:
            st.info("ℹ️ **Información:**")
            st.markdown("• La conversión no modifica los datos originales")
            st.markdown("• Se crea una nueva versión con tiempos convertidos")
            st.markdown("• Puedes descargar el resultado como Excel")
    else:
        st.info(f"ℹ️ No hay tiempos para convertir a {target_pool_type}")
    
    # Sección de descarga de resultados convertidos
    if 'df_converted' in st.session_state:
        st.markdown("---")
        st.header("📥 Descargar Resultados Convertidos")
        
        info = st.session_state.conversion_info
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.success(f"✅ **Conversión realizada:** {info['timestamp']}")
            st.info(f"🔄 **A piscina:** {info['target_pool']}")
            st.info(f"📊 **Tiempos convertidos:** {info['converted_count']}")
            
            # Crear archivo Excel con datos convertidos
            output = io.BytesIO()
            try:
                current_sheet = st.session_state.get('current_sheet', 'Temporada')
                
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    st.session_state.df_converted.to_excel(
                        writer, 
                        index=False, 
                        sheet_name=f"{current_sheet}_Convertido_{info['target_pool']}"
                    )
                
                output.seek(0)
                
                filename = f"nadadores_convertidos_{info['target_pool']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                
                st.download_button(
                    label=f"📥 Descargar Excel Convertido a {info['target_pool']}",
                    data=output.getvalue(),
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"❌ Error al crear archivo: {str(e)}")
        
        with col2:
            # Comparación rápida
            st.subheader("📊 Comparación")
            original_times = len([t for prueba in PRUEBAS if prueba in st.session_state.df.columns 
                                for t in st.session_state.df[prueba] if pd.notna(t) and str(t).strip()])
            converted_times = len([t for prueba in PRUEBAS if prueba in st.session_state.df_converted.columns 
                                 for t in st.session_state.df_converted[prueba] if pd.notna(t) and str(t).strip()])
            
            st.metric("Tiempos Originales", original_times)
            st.metric("Tiempos Convertidos", converted_times)
            st.metric("Diferencia", converted_times - original_times)

# ============== VALIDADORES ==============

def validate_time_format(time_str):
    """Valida formato de tiempo"""
    if not time_str or not time_str.strip():
        return True, ""
    
    patterns = [
        r'^\d{1,2}:\d{2}\.\d{2}$',  # mm:ss.cc
        r'^\d{1,2}:\d{2},\d{2}$',   # mm:ss,cc
        r'^\d{1,3}\.\d{2}$',        # ss.cc
        r'^\d{1,2}:\d{2}$',         # mm:ss
    ]
    
    time_str = time_str.strip()
    for pattern in patterns:
        if re.match(pattern, time_str):
            return True, "✓"
    
    return False, "✗"

def normalize_time(time_str):
    """Normaliza formato de tiempo"""
    if not time_str or not time_str.strip():
        return ""
    
    time_str = time_str.strip().replace(',', '.')
    
    try:
        if re.match(r'^\d{1,3}\.\d{2}$', time_str):
            seconds = float(time_str)
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes:02d}:{remaining_seconds:05.2f}"
        
        elif re.match(r'^\d{1,2}:\d{2}$', time_str):
            return time_str + ".00"
        
        elif re.match(r'^\d{1,2}:\d{2}\.\d{2}$', time_str):
            return time_str
        
        return time_str
    except:
        return time_str

# ============== APLICACIÓN PRINCIPAL ==============

def main():
    initialize_users()
    
    # Verificar autenticación
    if not check_authentication():
        return
    
    # Inicializar conversor
    converter = TimeConverter()
    
    # Título
    st.title("🏊‍♂️ Club Natación Las Palmas")
    st.markdown("### 🏆 Sistema Integral de Gestión de Temporadas")
    
    # Navegación principal por pestañas
    if has_permission('user_management'):
        tabs = st.tabs(["🏊‍♂️ Gestión Nadadores", "🔄 Conversión Masiva", "👥 Gestión Usuarios"])
    else:
        tabs = st.tabs(["🏊‍♂️ Gestión Nadadores", "🔄 Conversión Masiva"])
    
    # Pestaña 1: Gestión de Nadadores
    with tabs[0]:
        # Sidebar - Gestión de datos
        with st.sidebar:
            excel_file = load_data_source()
            
            # Selector de temporada
            if excel_file is not None:
                st.markdown("---")
                st.header("📅 Seleccionar Temporada")
                
                sheet_names = excel_file.sheet_names
                st.write(f"**Temporadas disponibles:** {len(sheet_names)}")
                
                selected_sheet = st.selectbox(
                    "🏆 Temporada:",
                    sheet_names,
                    help="Cada hoja representa una temporada diferente"
                )
                
                if st.button("📂 Cargar Temporada", type="primary"):
                    try:
                        df = pd.read_excel(excel_file, sheet_name=selected_sheet)
                        st.session_state.df = df
                        st.session_state.current_sheet = selected_sheet
                        st.success(f"✅ Temporada '{selected_sheet}' cargada")
                        st.success(f"📊 {len(df)} nadadores encontrados")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        
        # Verificar datos cargados
        if 'df' not in st.session_state:
            st.info("👈 **Conecta tu fuente de datos y selecciona una temporada**")
            
            # Mostrar permisos del usuario
            st.markdown("### 🎭 Tus Permisos en el Sistema:")
            role = st.session_state.get('user_role', 'asistente')
            
            if role == 'admin':
                st.success("👑 **Administrador**: Control total del sistema")
                st.markdown("- ✅ Gestión completa de nadadores")
                st.markdown("- ✅ Eliminar nadadores")
                st.markdown("- ✅ Conectar Excel online")
                st.markdown("- ✅ Conversor de tiempos masivo")
                st.markdown("- ✅ Gestión de usuarios y contraseñas")
            elif role == 'entrenador':
                st.info("🏋️ **Entrenador**: Gestión avanzada")
                st.markdown("- ✅ Administrar todos los nadadores")
                st.markdown("- ✅ Editar información y tiempos")
                st.markdown("- ✅ Conversor de tiempos masivo")
                st.markdown("- ❌ No puede eliminar nadadores")
                st.markdown("- ❌ No puede gestionar usuarios")
            else:
                st.warning("👀 **Asistente**: Solo consulta")
                st.markdown("- ✅ Visualizar datos")
                st.markdown("- ❌ Sin permisos de edición")
            
            return
        
        df = st.session_state.df
        current_sheet = st.session_state.get('current_sheet', 'Temporada')
        
        # Mostrar temporada actual
        st.info(f"📅 **Temporada Activa:** {current_sheet}")
        
        # ===== TABLA PRINCIPAL DE NADADORES (MÁS VISIBLE) =====
        st.header("📋 Lista Completa de Nadadores")
        
        # Filtros en una fila
        col_search, col_sex, col_available = st.columns([2, 1, 1])
        
        with col_search:
            search = st.text_input("🔍 Buscar nadador", placeholder="Nombre...")
        
        with col_sex:
            filter_sex = st.selectbox("Sexo", ["Todos", "M", "F"])
        
        with col_available:
            filter_available = st.selectbox("Disponibilidad", ["Todos", "Disponibles", "No disponibles"])
        
        # Aplicar filtros
        df_filtered = df.copy()
        
        if search:
            df_filtered = df_filtered[df_filtered['Nombre'].str.contains(search, case=False, na=False)]
        
        if filter_sex != "Todos":
            df_filtered = df_filtered[df_filtered['Sexo'] == filter_sex]
        
        if filter_available == "Disponibles":
            df_filtered = df_filtered[df_filtered['Disponible'] == True]
        elif filter_available == "No disponibles":
            df_filtered = df_filtered[df_filtered['Disponible'] == False]
        
        # Preparar datos para mostrar con información más visible
        if len(df_filtered) > 0:
            # Crear DataFrame para mostrar con columnas más informativas
            display_df = df_filtered.copy()
            
            # Formatear columnas para mejor visualización
            display_df['Disponible'] = display_df['Disponible'].apply(lambda x: '✅ Sí' if x else '❌ No')
            display_df['Edad'] = display_df.apply(lambda row: datetime.now().year - row.get('AñoNacimiento', 2000), axis=1)
            
            # Contar tiempos por nadador
            tiempos_count = []
            for idx, row in display_df.iterrows():
                count = 0
                for prueba in PRUEBAS:
                    if prueba in df.columns:
                        tiempo = row.get(prueba, '')
                        if pd.notna(tiempo) and str(tiempo).strip():
                            count += 1
                tiempos_count.append(f"{count} tiempos")
            
            display_df['Tiempos Registrados'] = tiempos_count
            
            # Seleccionar columnas principales para mostrar
            columns_to_show = ['Nombre', 'Sexo', 'AñoNacimiento', 'Edad', 'Disponible', 'Tiempos Registrados']
            
            # Mostrar tabla principal más grande y clara
            st.dataframe(
                display_df[columns_to_show], 
                use_container_width=True,
                height=400,  # Altura fija para mejor visualización
                column_config={
                    "Nombre": st.column_config.TextColumn("👤 Nombre", width="large"),
                    "Sexo": st.column_config.TextColumn("⚥ Sexo", width="small"),
                    "AñoNacimiento": st.column_config.NumberColumn("📅 Año Nac.", width="medium"),
                    "Edad": st.column_config.NumberColumn("🎂 Edad", width="small"),
                    "Disponible": st.column_config.TextColumn("✅ Disponible", width="medium"),
                    "Tiempos Registrados": st.column_config.TextColumn("⏱️ Tiempos", width="medium")
                }
            )
            
            # Selector de nadador para editar
            if has_permission('edit'):
                st.markdown("---")
                st.subheader("✏️ Editar Nadador Específico")
                
                # Selector más visible
                nadador_names = [f"{row['Nombre']} ({row['Sexo']}, {row['AñoNacimiento']})" 
                               for idx, row in df_filtered.iterrows()]
                
                if nadador_names:
                    selected_idx = st.selectbox(
                        "Selecciona nadador para editar:",
                        range(len(nadador_names)),
                        format_func=lambda x: nadador_names[x]
                    )
                    
                    # Obtener índice real
                    real_idx = df_filtered.iloc[selected_idx].name
                    swimmer = df.loc[real_idx]
                    
                    # Formulario de edición expandido
                    with st.expander(f"✏️ Editando: {swimmer.get('Nombre', 'Sin nombre')}", expanded=True):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**📝 Información Personal:**")
                            
                            with st.form(f"edit_swimmer_{real_idx}"):
                                new_name = st.text_input("Nombre", value=str(swimmer.get('Nombre', '')))
                                new_available = st.checkbox("Disponible", value=bool(swimmer.get('Disponible', False)))
                                new_sex = st.selectbox("Sexo", ['M', 'F'], 
                                                     index=['M', 'F'].index(str(swimmer.get('Sexo', 'M'))) if str(swimmer.get('Sexo', 'M')) in ['M', 'F'] else 0)
                                new_year = st.number_input("Año Nacimiento", 
                                                         min_value=1950, max_value=2025, 
                                                         value=int(swimmer.get('AñoNacimiento', 2000)))
                                
                                col_save, col_delete = st.columns([3, 1])
                                
                                with col_save:
                                    if st.form_submit_button("💾 Guardar Cambios", type="primary"):
                                        df.loc[real_idx, 'Nombre'] = new_name
                                        df.loc[real_idx, 'Disponible'] = new_available
                                        df.loc[real_idx, 'Sexo'] = new_sex
                                        df.loc[real_idx, 'AñoNacimiento'] = new_year
                                        df.loc[real_idx, 'Edad'] = datetime.now().year - new_year
                                        
                                        st.session_state.df = df
                                        st.success("✅ Información actualizada")
                                        st.rerun()
                                
                                with col_delete:
                                    if has_permission('delete'):
                                        if st.form_submit_button("🗑️ Eliminar", type="secondary"):
                                            if st.session_state.get('confirm_delete_swimmer', '') == str(real_idx):
                                                df_updated = df.drop(index=real_idx).reset_index(drop=True)
                                                st.session_state.df = df_updated
                                                st.success("✅ Nadador eliminado")
                                                st.rerun()
                                            else:
                                                st.session_state.confirm_delete_swimmer = str(real_idx)
                                                st.warning("⚠️ Haz clic otra vez para confirmar")
                        
                        with col2:
                            st.markdown("**⏱️ Gestión de Tiempos:**")
                            
                            # Mostrar tiempos existentes
                            swimmer_times = []
                            for prueba in PRUEBAS:
                                tiempo = swimmer.get(prueba, '')
                                if pd.notna(tiempo) and str(tiempo).strip():
                                    piscina = swimmer.get(f"{prueba}Piscina", '')
                                    fecha = swimmer.get(f"{prueba}Fecha", '')
                                    swimmer_times.append({
                                        'Prueba': prueba,
                                        'Tiempo': str(tiempo),
                                        'Piscina': str(piscina),
                                        'Fecha': str(fecha) if pd.notna(fecha) else ''
                                    })
                            
                            if swimmer_times:
                                st.dataframe(pd.DataFrame(swimmer_times), use_container_width=True, height=200)
                            else:
                                st.info("No hay tiempos registrados")
                            
                            # Formulario para añadir tiempo
                            with st.form(f"add_time_{real_idx}"):
                                st.markdown("**➕ Añadir Nuevo Tiempo:**")
                                
                                selected_event = st.selectbox("Prueba", PRUEBAS)
                                new_time = st.text_input("Tiempo", placeholder="01:23.45")
                                
                                col_pool, col_date = st.columns(2)
                                with col_pool:
                                    new_pool = st.selectbox("Piscina", ['25m', '50m'])
                                with col_date:
                                    new_date = st.date_input("Fecha", value=datetime.now().date())
                                
                                if st.form_submit_button("💾 Guardar Tiempo", type="primary"):
                                    if new_time.strip():
                                        valid, _ = validate_time_format(new_time)
                                        if valid:
                                            normalized_time = normalize_time(new_time)
                                            
                                            df.loc[real_idx, selected_event] = normalized_time
                                            df.loc[real_idx, f"{selected_event}Piscina"] = new_pool
                                            df.loc[real_idx, f"{selected_event}Fecha"] = new_date
                                            
                                            st.session_state.df = df
                                            st.success(f"✅ Tiempo guardado: {selected_event}")
                                            st.rerun()
                                        else:
                                            st.error("❌ Formato incorrecto")
                                    else:
                                        st.error("❌ El tiempo no puede estar vacío")
            
            # Estadísticas de la temporada
            st.markdown("---")
            st.header("📊 Estadísticas de la Temporada")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("👥 Total Nadadores", len(df_filtered))
            
            with col2:
                available_count = len(df_filtered[df_filtered['Disponible'] == True])
                st.metric("✅ Disponibles", available_count)
            
            with col3:
                # Contar total de tiempos
                total_times = 0
                for prueba in PRUEBAS:
                    if prueba in df_filtered.columns:
                        total_times += df_filtered[prueba].notna().sum()
                st.metric("⏱️ Tiempos Totales", total_times)
            
            with col4:
                # Promedio de edad
                avg_age = df_filtered.apply(lambda row: datetime.now().year - row.get('AñoNacimiento', 2000), axis=1).mean()
                st.metric("🎂 Edad Promedio", f"{avg_age:.1f}")
        
        else:
            st.warning("No se encontraron nadadores con los filtros aplicados")
        
        # Botón de descarga
        if has_permission('download'):
            st.markdown("---")
            st.header("📥 Descargar Datos")
            
            output = io.BytesIO()
            try:
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name=current_sheet)
                
                output.seek(0)
                
                st.download_button(
                    label=f"📥 Descargar {current_sheet}",
                    data=output.getvalue(),
                    file_name=f"nadadores_{current_sheet}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )
                
            except Exception as e:
                st.error(f"Error al crear archivo: {str(e)}")
    
    # Pestaña 2: Conversión Masiva
    with tabs[1]:
        show_mass_conversion()
    
    # Pestaña 3: Gestión de Usuarios (solo admin)
    if has_permission('user_management') and len(tabs) > 2:
        with tabs[2]:
            show_user_management()

if __name__ == "__main__":
    main()