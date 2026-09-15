from nicegui import ui
import re
from busqueda import pagina_busqueda
from components import crear_dialogo_almanaque
from config import (
    COLUMNAS_TABLA,
    DEPARTAMENTOS_POR_PROVINCIA,
    OPCIONES_ESCALA,
    OPCIONES_PROVINCIA,
    OPCIONES_TIPO,
)
from database import (
    crear_tabla,
    guardar_registro,
    obtener_registros,
)
from nicegui import ui

def procesar_saludo(texto):
    return texto.strip().upper()

# 3. Lectura del archivo saludo.txt
with open("saludo.txt", "r", encoding="utf-8") as archivo:
    contenido = archivo.read()

# 4. Uso del contenido leído
print("El contenido del archivo es:")
print(contenido)


# 1. Función para validar las credenciales
def intentar_login():
    if input_user.value == "admin" and input_pass.value == "1234":
        contenedor_login.visible = False
        contenedor_contenido.visible = True
        cargar_archivo()
    else:
        ui.notify('Usuario o contraseña incorrectos', type='negative')

# 2. Función para leer el archivo saludo.txt
def cargar_archivo():
    try:
        with open("saludo.txt", "r", encoding="utf-8") as archivo:
            lbl_texto.text = archivo.read()
    except FileNotFoundError:
        lbl_texto.text = "Error: No se encontró el archivo 'saludo.txt'"

# 3. Interfaz de Inicio de Sesión
with ui.card().classes('absolute-center w-80 p-4') as contenedor_login:
    ui.label('Inicio de Sesión').classes('text-h6')
    input_user = ui.input('Usuario')
    input_pass = ui.input('Contraseña', password=True, password_toggle_button=True)
    ui.button('Ingresar', on_click=intentar_login).classes('w-full mt-4')

# 4. Interfaz de Contenido (Oculta hasta iniciar sesión)
with ui.card().classes('absolute-center w-96 p-4') as contenedor_contenido:
    contenedor_contenido.visible = False
    ui.label('Contenido de saludo.txt:').classes('text-h6 mb-2')
    lbl_texto = ui.label('')

# 5. Arrancar la aplicación
ui.run(title='Mi geocatalogo', port=8080)



def validar_numero_hoja(numero):
    return bool(re.match(r"^\d{4}-\d{2}$", numero))


# 1. RUTA Y VENTANA PRINCIPAL
@ui.page("/")
def main_page():
    crear_tabla()  # Asegura que la tabla de SQLite esté lista

    ui.label("GESTIÓN DE HOJAS CARTOGRÁFICAS").classes(
        "text-2xl font-bold mb-4"
    )

    with ui.card().classes("w-full max-w-4xl p-4 mb-4"):
        ui.label("INGRESAR DATOS").classes("text-lg font-semibold mb-2")

        # DIBUJO DE CAMPOS
        with ui.grid(columns=2).classes("w-full gap-4"):
            input_nombre = ui.input(
                "NOMBRE DE LA HOJA*", placeholder="Ej: LAS HERAS"
            )
            input_num_hoja = ui.input(
                "NÚMERO DE HOJA (0000-00)*", placeholder="3560-12"
            )

            input_provincia = ui.select(
                options=OPCIONES_PROVINCIA,
                label="PROVINCIA",
                value="MENDOZA",
            )

            input_depto = ui.select(
                options=DEPARTAMENTOS_POR_PROVINCIA["MENDOZA"],
                label="DEPARTAMENTO",
                value=DEPARTAMENTOS_POR_PROVINCIA["MENDOZA"][0],
            )

            def actualizar_departamentos(e):
                prov_seleccionada = e.value
                nuevos_deptos = DEPARTAMENTOS_POR_PROVINCIA[prov_seleccionada]
                input_depto.options = nuevos_deptos
                input_depto.value = nuevos_deptos[0]
                input_depto.update()

            input_provincia.on_value_change(actualizar_departamentos)

            input_edicion = ui.input(
                "EDICIÓN (AÑO)", value="SIN DATO"
            ).props("readonly")
            dialogo_almanaque = crear_dialogo_almanaque(input_edicion)
            input_edicion.on("click", dialogo_almanaque.open)

            input_tipo = ui.select(
                options=OPCIONES_TIPO,
                label="TIPO",
                value=OPCIONES_TIPO[0],
            )

            input_escala = ui.select(
                options=OPCIONES_ESCALA,
                label="ESCALA",
                value=OPCIONES_ESCALA[0],
            )

            input_ubicacion = ui.input(
                "UBICACIÓN", placeholder="Ej: MUEBLE 2 - CAJÓN 3"
            )

            input_cantidad = ui.number(
                "CANTIDAD*",
                value=1,
                min=1,
                max=15,
                step=1,
                format="%d",
            )

            input_obs = ui.input("OBSERVACIONES")

        # TABLA DE CONSULTA RÁPIDA
        tabla = ui.table(
            columns=COLUMNAS_TABLA,
            rows=obtener_registros(),
            row_key="id",
        ).classes("w-full mt-4")

        # LÓGICA DE GUARDADO
        def fn_guardar():
            nombre = (
                input_nombre.value.strip().upper()
                if input_nombre.value
                else ""
            )
            num_hoja = (
                input_num_hoja.value.strip().upper()
                if input_num_hoja.value
                else ""
            )
            depto = input_depto.value.upper() if input_depto.value else ""
            edicion = input_edicion.value.upper() if input_edicion.value else ""
            tipo = input_tipo.value.upper() if input_tipo.value else ""
            escala = input_escala.value.upper() if input_escala.value else ""
            provincia = (
                input_provincia.value.upper() if input_provincia.value else ""
            )
            ubicacion = (
                input_ubicacion.value.strip().upper()
                if input_ubicacion.value
                else ""
            )
            cantidad_val = input_cantidad.value
            obs = input_obs.value.strip().upper() if input_obs.value else ""

            if not nombre:
                ui.notify(
                    "EL NOMBRE DE LA HOJA ES OBLIGATORIO.", type="warning"
                )
                return

            if not validar_numero_hoja(num_hoja):
                ui.notify(
                    "EL NÚMERO DE HOJA DEBE TENER EL FORMATO 0000-00 (4 DÍGITOS, GUION Y 2 DÍGITOS).",
                    type="negative",
                )
                return

            if cantidad_val is None or not (1 <= int(cantidad_val) <= 15):
                ui.notify(
                    "LA CANTIDAD DEBE SER UN NÚMERO ENTRE 1 Y 15.",
                    type="negative",
                )
                return

            guardar_registro(
                nombre,
                num_hoja,
                depto,
                edicion,
                tipo,
                escala,
                provincia,
                ubicacion,
                int(cantidad_val),
                obs,
            )
            ui.notify("REGISTRO GUARDADO CON ÉXITO", type="positive")

            tabla.rows = obtener_registros()
            tabla.update()
            fn_limpiar()

        # LÓGICA DE LIMPIEZA
        def fn_limpiar():
            input_nombre.value = ""
            input_num_hoja.value = ""
            input_provincia.value = "MENDOZA"
            input_depto.options = DEPARTAMENTOS_POR_PROVINCIA["MENDOZA"]
            input_depto.value = DEPARTAMENTOS_POR_PROVINCIA["MENDOZA"][0]
            input_edicion.value = "SIN DATO"
            input_tipo.value = OPCIONES_TIPO[0]
            input_escala.value = OPCIONES_ESCALA[0]
            input_ubicacion.value = ""
            input_cantidad.value = 1
            input_obs.value = ""

        # BOTONES
        with ui.row().classes("mt-4 gap-2"):
            ui.button("GUARDAR REGISTRO", on_click=fn_guardar).props(
                "color=primary"
            )
            ui.button("LIMPIAR CAMPOS", on_click=fn_limpiar).props(
                "outline color=secondary"
            )
            ui.button(
                "BÚSQUEDA Y ELIMINACIÓN",
                on_click=lambda: ui.navigate.to("/busqueda"),
            ).props("color=accent")


# 2. VINCULACIÓN CON LA RUTA DE BÚSQUEDA
@ui.page("/busqueda")
def busqueda_page():
    pagina_busqueda()


# 3. EJECUCIÓN DEL SERVIDOR
ui.run(title="Gestión de Hojas Cartográficas", port=8080)
ui.run(title="Gestión de Hojas Cartográficas", port=8085)