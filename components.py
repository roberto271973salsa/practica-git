from config import AÑOS_EDICION
from nicegui import ui


def crear_dialogo_almanaque(input_target):
    with ui.dialog() as dialogo, ui.card().classes("w-full max-w-2xl p-4"):
        ui.label("SELECCIONAR AÑO DE EDICIÓN").classes("text-xl font-bold mb-2")

        def seleccionar_opcion(val):
            input_target.value = val
            dialogo.close()

        ui.button(
            "SIN DATO", on_click=lambda: seleccionar_opcion("SIN DATO")
        ).props("color=warning w-full mb-4")

        with ui.scroll_area().classes("h-64 w-full border p-2"):
            with ui.grid(columns=6).classes("gap-2 w-full"):
                for anio in AÑOS_EDICION:
                    ui.button(
                        anio, on_click=lambda a=anio: seleccionar_opcion(a)
                    ).props("flat color=primary")

        ui.button("CANCELAR", on_click=dialogo.close).props(
            "flat color=grey mt-2"
        )

    return dialogo