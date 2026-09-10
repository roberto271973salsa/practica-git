from config import COLUMNAS_TABLA, DEPARTAMENTOS_POR_PROVINCIA
from database import eliminar_registros_por_ids, obtener_registros
from nicegui import ui

# Construir opciones de departamentos discriminados por provincia (ej: "LAS HERAS (MENDOZA)")
OPCIONES_DEPARTAMENTOS = {}
for prov, deptos in DEPARTAMENTOS_POR_PROVINCIA.items():
    for d in sorted(deptos):
        OPCIONES_DEPARTAMENTOS[d] = f"{d} ({prov})"


def pagina_busqueda():
    # Encabezado con botón de regreso
    with ui.row().classes("w-full justify-between items-center mb-4"):
        ui.label("BÚSQUEDA Y ELIMINACIÓN DE REGISTROS").classes(
            "text-2xl font-bold"
        )
        ui.button(
            "VOLVER AL MENÚ PRINCIPAL", on_click=lambda: ui.navigate.to("/")
        ).props("outline color=primary")

    with ui.card().classes("w-full max-w-5xl p-4 mb-4"):
        ui.label("CRITERIOS DE BÚSQUEDA").classes("text-lg font-semibold mb-2")

        # Layout superior: Filtros a la izquierda | Tarjeta de Ubicación a la derecha
        with ui.row().classes("w-full gap-6 items-start"):

            # COLUMNA IZQUIERDA: Filtros de Búsqueda
            with ui.column().classes("flex-grow gap-2"):
                input_nombre = ui.input(
                    "BUSCAR POR NOMBRE", placeholder="Ej: LAS HERAS"
                ).classes("w-full")
                input_num_hoja = ui.input(
                    "BUSCAR POR N° DE HOJA", placeholder="Ej: 3560-12"
                ).classes("w-full")

                select_depto = (
                    ui.select(
                        options=OPCIONES_DEPARTAMENTOS,
                        label="BUSCAR POR DEPARTAMENTO",
                        with_input=True,
                    )
                    .classes("w-full")
                    .props("clearable")
                )

                input_anio = ui.input(
                    "BUSCAR POR AÑO DE EDICIÓN",
                    placeholder="Ej: 1998 o SIN DATO",
                ).classes("w-full")

            # COLUMNA DERECHA: Visor de Ubicación Destacado
            with ui.card().classes(
                "p-4 bg-blue-50 border-2 border-blue-400 rounded-lg min-w-[280px] text-center shadow-sm"
            ):
                ui.label("📍 UBICACIÓN").classes(
                    "text-lg font-bold text-blue-800 mb-1"
                )
                label_ubicacion = ui.label("REALICE UNA BÚSQUEDA").classes(
                    "text-2xl font-black text-blue-950 tracking-wide break-words"
                )

        # TABLA DE RESULTADOS (Inicia vacía para no mostrar toda la base de datos)
        tabla = ui.table(
            columns=COLUMNAS_TABLA,
            rows=[],
            row_key="id",
            selection="single",
        ).classes("w-full mt-4")

        # EVENTO AL SELECCIONAR UNA FILA MANUALMENTE
        def al_seleccionar_fila(e):
            args = e.args
            rows = args if isinstance(args, list) else args.get("rows", [])

            if rows:
                registro = rows[0]
                # Dejamos visible ÚNICAMENTE la fila seleccionada
                tabla.rows = [registro]
                tabla.selected = [registro]

                ubicacion_valor = str(
                    registro.get("ubicacion") or ""
                ).strip()
                label_ubicacion.text = (
                    ubicacion_valor.upper()
                    if ubicacion_valor
                    else "SIN UBICACIÓN ASIGNADA"
                )
                tabla.update()
            else:
                label_ubicacion.text = "SELECCIONE UN REGISTRO"

        tabla.on("selection", al_seleccionar_fila)

        # FUNCIÓN DE FILTRADO DE LA TABLA
        def filtrar_registros():
            nombre = (
                input_nombre.value.strip().upper() if input_nombre.value else ""
            )
            num_hoja = (
                input_num_hoja.value.strip().upper()
                if input_num_hoja.value
                else ""
            )
            depto = select_depto.value if select_depto.value else ""
            anio = (
                input_anio.value.strip().upper() if input_anio.value else ""
            )

            # Si no hay criterios escritos, la tabla se mantiene oculta/vacía
            if not any([nombre, num_hoja, depto, anio]):
                tabla.rows = []
                tabla.selected.clear()
                label_ubicacion.text = "REALICE UNA BÚSQUEDA"
                tabla.update()
                return

            todos = obtener_registros()
            filtrados = []

            for r in todos:
                cumple_nombre = (
                    not nombre
                    or nombre in str(r.get("nombre_hoja", "")).upper()
                )
                cumple_num = (
                    not num_hoja
                    or num_hoja in str(r.get("numero_hoja", "")).upper()
                )
                cumple_depto = (
                    not depto
                    or depto.upper() == str(r.get("departamento", "")).upper()
                )
                cumple_anio = (
                    not anio or anio in str(r.get("edicion", "")).upper()
                )

                if (
                    cumple_nombre
                    and cumple_num
                    and cumple_depto
                    and cumple_anio
                ):
                    filtrados.append(r)

            # Si arroja un único resultado, se selecciona y muestra de forma individual
            if len(filtrados) == 1:
                registro_unico = filtrados[0]
                tabla.rows = [registro_unico]
                tabla.selected = [registro_unico]

                ubicacion_valor = str(
                    registro_unico.get("ubicacion") or ""
                ).strip()
                label_ubicacion.text = (
                    ubicacion_valor.upper()
                    if ubicacion_valor
                    else "SIN UBICACIÓN ASIGNADA"
                )
            elif len(filtrados) > 1:
                # Si hay varios resultados, mostramos la lista breve para elegir uno
                tabla.rows = filtrados
                tabla.selected.clear()
                label_ubicacion.text = "SELECCIONE UN REGISTRO"
            else:
                # Sin coincidencias
                tabla.rows = []
                tabla.selected.clear()
                label_ubicacion.text = "NO SE ENCONTRARON REGISTROS"

            tabla.update()

        # Vinculación de eventos a los controles
        input_nombre.on("update:model-value", filtrar_registros)
        input_num_hoja.on("update:model-value", filtrar_registros)
        select_depto.on_value_change(filtrar_registros)
        input_anio.on("update:model-value", filtrar_registros)

        def fn_eliminar_busqueda():
            if not tabla.selected:
                ui.notify(
                    "POR FAVOR, SELECCIONA EL REGISTRO QUE DESEAS ELIMINAR.",
                    type="warning",
                )
                return

            ids = [row["id"] for row in tabla.selected]
            eliminar_registros_por_ids(ids)

            ui.notify(
                "SE HA ELIMINADO EL REGISTRO CORRECTAMENTE.",
                type="positive",
            )

            tabla.selected.clear()
            fn_limpiar_filtros()

        def fn_limpiar_filtros():
            input_nombre.value = ""
            input_num_hoja.value = ""
            select_depto.value = None
            input_anio.value = ""
            filtrar_registros()

        # Botones de Acción
        with ui.row().classes("mt-4 gap-2"):
            ui.button("LIMPIAR FILTROS", on_click=fn_limpiar_filtros).props(
                "outline color=secondary"
            )
            ui.button(
                "ELIMINAR SELECCIONADO", on_click=fn_eliminar_busqueda
            ).props("color=negative")