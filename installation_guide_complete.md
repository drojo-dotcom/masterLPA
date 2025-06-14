# 🚀 Instalación - Sistema Completo de Gestión

## ✨ **Nuevas Características Implementadas**

### 🎭 **Sistema de Permisos Mejorado:**
- **👑 Administrador**: Control total (incluyendo eliminar nadadores)
- **🏋️ Entrenador**: Administra TODOS los nadadores (excepto eliminar)
- **👀 Asistente**: Solo visualización

### 🌐 **Excel Online (Google Sheets):**
- ✅ Conexión directa con Google Sheets
- ✅ Actualización en tiempo real
- ✅ Acceso desde cualquier lugar
- ✅ Múltiples usuarios simultáneos

### 📅 **Gestión de Temporadas:**
- ✅ Cada hoja del Excel = una temporada
- ✅ Selector dinámico de temporadas
- ✅ Datos organizados por años

### 🔄 **Conversor de Tiempos Integrado:**
- ✅ Conversión 25m ↔ 50m
- ✅ Tablas oficiales FINA
- ✅ Todos los estilos y distancias
- ✅ Guardar tiempos convertidos

---

## 📦 **Instalación Rápida**

### **Paso 1: Instalar dependencias**
```bash
pip install streamlit pandas openpyxl xlrd requests
```

### **Paso 2: Ejecutar aplicación**
```bash
streamlit run nadadores_completo.py
```

### **Paso 3: Acceder al sistema**
- 🌐 **URL**: http://localhost:8501
- 👤 **Usuarios disponibles**:
  - `admin` / `admin123` (Administrador)
  - `entrenador` / `entrenador123` (Entrenador)
  - `asistente` / `asistente123` (Asistente)

---

## 🏊‍♂️ **Cómo Usar el Sistema**

### **1. 🔐 Iniciar Sesión**
- Selecciona tu tipo de usuario
- Ingresa credenciales
- Revisa tus permisos en pantalla

### **2. 📊 Conectar Datos**

**Opción A: Archivo Local**
- Sube archivo Excel (.xlsx)
- Cada hoja = temporada diferente

**Opción B: Google Sheets Online**
- Configura permisos públicos
- Pega URL completa
- Sincronización automática

### **3. 📅 Seleccionar Temporada**
- Ve las temporadas disponibles
- Selecciona la temporada activa
- Carga los datos

### **4. 🏊‍♂️ Gestionar Nadadores**

**Como Entrenador o Admin:**
- ✅ Ver todos los nadadores
- ✅ Editar información personal
- ✅ Añadir/editar tiempos
- ✅ Convertir tiempos entre piscinas
- ✅ Descargar datos actualizados

**Solo Admin puede:**
- 🗑️ Eliminar nadadores

**Como Asistente:**
- 👁️ Solo visualización
- 📊 Ver estadísticas

### **5. 🔄 Conversor de Tiempos**
- Selecciona prueba a convertir
- Ingresa tiempo original
- Elige piscina origen/destino
- Obtén conversión automática
- Guarda resultado si deseas

---

## 📱 **Despliegue Online**

### **Streamlit Cloud (Gratis)**
1. Sube código a GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta repositorio
4. ¡App online 24/7!

### **Archivos necesarios:**
```
tu-repositorio/
├── nadadores_completo.py
├── requirements.txt
└── README.md
```

---

## 🎯 **Casos de Uso**

### **📋 Gestión Diaria del Entrenador:**
1. **Login** como entrenador
2. **Conecta** Google Sheets del club
3. **Selecciona** temporada actual
4. **Busca** nadador específico
5. **Añade** nuevos tiempos de entrenamiento
6. **Convierte** tiempos para diferentes competencias
7. **Descarga** datos actualizados

### **👑 Administración Completa:**
1. **Login** como admin
2. **Gestiona** múltiples temporadas
3. **Añade/elimina** nadadores
4. **Configura** fuentes de datos
5. **Supervisa** todo el sistema

### **👀 Consulta de Asistentes:**
1. **Login** como asistente
2. **Visualiza** datos de nadadores
3. **Consulta** estadísticas
4. **Revisa** tiempos registrados

---

## 🔧 **Configuración Avanzada**

### **Cambiar Contraseñas:**
Edita en `nadadores_completo.py`:
```python
USERS = {
    "admin": {
        "password": hash_password("TU_NUEVA_CONTRASEÑA"),
        # ...
    }
}
```

### **Añadir Nuevos Usuarios:**
```python
USERS["nuevo_entrenador"] = {
    "password": hash_password("contraseña_segura"),
    "role": "entrenador",
    "name": "Nuevo Entrenador"
}
```

### **Personalizar Pruebas:**
Edita la lista de pruebas en la clase `TimeConverter`:
```python
self.pruebas = [
    "50m Libre", "100m Libre", 
    # Añade o quita pruebas aquí
]
```

---

## 📊 **Estructura de Datos Requerida**

### **Columnas Obligatorias:**
- `Nombre`: Nombre del nadador
- `Disponible`: TRUE/FALSE
- `Sexo`: M/F  
- `AñoNacimiento`: YYYY
- `Edad`: Número (calculado automáticamente)

### **Columnas de Tiempos:**
Por cada prueba (ej: "50m Libre"):
- `50m Libre`: Tiempo (mm:ss.cc)
- `50m LibrePiscina`: 25m o 50m
- `50m LibreFecha`: YYYY-MM-DD

---

## 🎉 **¡Listo para Usar!**

Tu sistema completo incluye:
- ✅ **3 niveles de usuario** con permisos específicos
- ✅ **Excel online** con Google Sheets
- ✅ **Múltiples temporadas** en una sola aplicación
- ✅ **Conversor de tiempos** integrado
- ✅ **Interfaz moderna** y responsive
- ✅ **Sincronización automática**

**¡Perfecto para la gestión profesional de un club de natación!** 🏊‍♂️🏆