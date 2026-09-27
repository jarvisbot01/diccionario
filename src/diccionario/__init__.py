import sys
from typing import Optional
from .gestor import DiccionarioJSON

__all__ = ["DiccionarioJSON", "main"]


def imprimir_termino(info: dict) -> None:
    palabra = info.get("palabra", "")
    categoria = info.get("categoria", "General")
    definicion = info.get("definicion", "")
    ejemplos = info.get("ejemplos", [])
    sinonimos = info.get("sinonimos", [])

    print(f"\n📖 \033[1;36m{palabra.upper()}\033[0m  [\033[33m{categoria}\033[0m]")
    print(f"    \033[1mDefinición:\033[0m {definicion}")
    if sinonimos:
        print(f"    \033[1mSinónimos:\033[0m {', '.join(sinonimos)}")
    if ejemplos:
        print(f"    \033[1mEjemplos:\033[0m")
        for ej in ejemplos:
            print(f"      • \"{ej}\"")


def menu_agregar(diccionario: DiccionarioJSON) -> None:
    print("\n--- ➕ AGREGAR NUEVO TÉRMINO ---")
    palabra = input("Palabra o término: ").strip()
    if not palabra:
        print("❌ La palabra no puede estar vacía.")
        return

    existente = diccionario.buscar(palabra)
    if existente:
        print(f"⚠️ El término '{palabra}' ya existe en el diccionario.")
        return

    definicion = input("Definición: ").strip()
    if not definicion:
        print("❌ La definición es obligatoria.")
        return

    categoria = input("Categoría (opcional, default 'General'): ").strip()
    if not categoria:
        categoria = "General"

    sinonimos_str = input("Sinónimos separados por coma (opcional): ").strip()
    sinonimos = [s.strip() for s in sinonimos_str.split(",") if s.strip()] if sinonimos_str else []

    ejemplo_str = input("Ejemplo de uso (opcional): ").strip()
    ejemplos = [ejemplo_str] if ejemplo_str else []

    exito = diccionario.agregar(
        palabra=palabra,
        definicion=definicion,
        categoria=categoria,
        ejemplos=ejemplos,
        sinonimos=sinonimos,
    )

    if exito:
        print(f"✅ ¡'{palabra}' agregada exitosamente al diccionario JSON!")
    else:
        print("❌ No se pudo agregar el término.")


def menu_buscar(diccionario: DiccionarioJSON) -> None:
    print("\n--- 🔍 BUSCAR TÉRMINO ---")
    termino = input("Ingresa la palabra a buscar: ").strip()
    if not termino:
        print("❌ Por favor escribe un término para buscar.")
        return

    exacto = diccionario.buscar(termino)
    if exacto:
        print("\nResultado exacto encontrado:")
        imprimir_termino(exacto)
        return

    parciales = diccionario.buscar_parcial(termino)
    if parciales:
        print(f"\nNo hubo coincidencia exacta, pero se encontraron {len(parciales)} resultado(s) relacionados:")
        for res in parciales.values():
            imprimir_termino(res)
    else:
        print(f"❌ No se encontraron coincidencias para '{termino}'.")


def menu_listar(diccionario: DiccionarioJSON) -> None:
    print("\n--- 📚 LISTAR TÉRMINOS ---")
    categorias = diccionario.obtener_categorias()
    print("Categorías disponibles: Todas, " + ", ".join(categorias))
    filtro = input("Filtrar por categoría (presiona Enter para listar todas): ").strip()

    categoria_filtro: Optional[str] = filtro if filtro else None
    resultados = diccionario.listar(categoria=categoria_filtro)

    if not resultados:
        print("ℹ️ No hay términos que coincidan con el criterio seleccionado.")
        return

    print(f"\nTotal: {len(resultados)} término(s) encontrado(s)")
    for info in resultados.values():
        imprimir_termino(info)


def menu_editar(diccionario: DiccionarioJSON) -> None:
    print("\n--- ✏️ EDITAR TÉRMINO ---")
    palabra = input("Palabra a editar: ").strip()
    actual = diccionario.buscar(palabra)

    if not actual:
        print(f"❌ No se encontró '{palabra}' en el diccionario.")
        return

    print("\nDatos actuales:")
    imprimir_termino(actual)
    print("\n(Presiona Enter para mantener el valor actual)")

    nueva_def = input(f"Nueva definición [{actual['definicion']}]: ").strip()
    nueva_cat = input(f"Nueva categoría [{actual['categoria']}]: ").strip()
    nuevos_sin = input(f"Nuevos sinónimos ({', '.join(actual.get('sinonimos', []))}): ").strip()

    definicion_final = nueva_def if nueva_def else actual["definicion"]
    categoria_final = nueva_cat if nueva_cat else actual["categoria"]
    sinonimos_final = [s.strip() for s in nuevos_sin.split(",") if s.strip()] if nuevos_sin else actual.get("sinonimos", [])

    diccionario.editar(
        palabra=palabra,
        definicion=definicion_final,
        categoria=categoria_final,
        sinonimos=sinonimos_final,
    )
    print(f"✅ ¡'{palabra}' actualizada correctamente!")


def menu_eliminar(diccionario: DiccionarioJSON) -> None:
    print("\n--- 🗑️ ELIMINAR TÉRMINO ---")
    palabra = input("Palabra a eliminar: ").strip()
    actual = diccionario.buscar(palabra)

    if not actual:
        print(f"❌ No se encontró '{palabra}' en el diccionario.")
        return

    confirmacion = input(f"¿Estás seguro de que deseas eliminar '{actual['palabra']}'? (s/n): ").strip().lower()
    if confirmacion == "s":
        diccionario.eliminar(palabra)
        print(f"✅ Término '{palabra}' eliminado correctamente.")
    else:
        print("Operación cancelada.")


def menu_estadisticas(diccionario: DiccionarioJSON) -> None:
    stats = diccionario.obtener_estadisticas()
    print("\n--- 📊 ESTADÍSTICAS DEL DICCIONARIO ---")
    print(f"📁 Archivo de datos: {stats['archivo']}")
    print(f"📖 Total de palabras: {stats['total_palabras']}")
    print(f"🏷️ Total de categorías: {stats['total_categorias']}")
    print(f"📌 Lista de categorías: {', '.join(stats['categorias'])}")


def main() -> None:
    diccionario = DiccionarioJSON()

    try:
        while True:
            print("\n" + "=" * 45)
            print("       📘 GESTOR DE DICCIONARIO JSON")
            print("=" * 45)
            print("  1. 🔍 Buscar palabra")
            print("  2. ➕ Agregar nueva palabra")
            print("  3. 📚 Listar todas las palabras")
            print("  4. ✏️ Editar palabra")
            print("  5. 🗑️ Eliminar palabra")
            print("  6. 📊 Ver estadísticas")
            print("  7. 🚪 Salir")
            print("=" * 45)

            opcion = input("Selecciona una opción (1-7): ").strip()

            if opcion == "1":
                menu_buscar(diccionario)
            elif opcion == "2":
                menu_agregar(diccionario)
            elif opcion == "3":
                menu_listar(diccionario)
            elif opcion == "4":
                menu_editar(diccionario)
            elif opcion == "5":
                menu_eliminar(diccionario)
            elif opcion == "6":
                menu_estadisticas(diccionario)
            elif opcion == "7":
                print("\n👋 ¡Hasta luego!")
                sys.exit(0)
            else:
                print("❌ Opción no válida. Por favor selecciona un número del 1 al 7.")
    except (KeyboardInterrupt, EOFError):
        print("\n\n👋 Sesión finalizada. ¡Hasta pronto!")
        sys.exit(0)


if __name__ == "__main__":
    main()
