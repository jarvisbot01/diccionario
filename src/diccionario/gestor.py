import json
import os
from typing import Dict, Any, Optional, List


class DiccionarioJSON:
    """
    Gestor de diccionario con almacenamiento persistente en archivos JSON.
    Permite crear, consultar, modificar, eliminar y listar términos y sus definiciones.
    """

    def __init__(self, ruta_archivo: Optional[str] = None) -> None:
        if ruta_archivo is None:
            directorio_actual = os.path.dirname(os.path.abspath(__file__))
            self.ruta_archivo = os.path.join(directorio_actual, "diccionario.json")
        else:
            self.ruta_archivo = ruta_archivo

        self.datos: Dict[str, Dict[str, Any]] = {}
        self.cargar_datos()

    def cargar_datos(self) -> Dict[str, Dict[str, Any]]:
        """Carga las palabras y definiciones desde el archivo JSON."""
        if not os.path.exists(self.ruta_archivo):
            self.datos = {}
            self.guardar_datos()
            return self.datos

        try:
            with open(self.ruta_archivo, "r", encoding="utf-8") as archivo:
                self.datos = json.load(archivo)
        except (json.JSONDecodeError, OSError):
            self.datos = {}
        return self.datos

    def guardar_datos(self) -> None:
        """Guarda los datos actuales en el archivo JSON con formato legible."""
        directorio = os.path.dirname(self.ruta_archivo)
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio, exist_ok=True)

        with open(self.ruta_archivo, "w", encoding="utf-8") as archivo:
            json.dump(self.datos, archivo, ensure_ascii=False, indent=4)

    def _normalizar_clave(self, palabra: str) -> str:
        """Normaliza la palabra a minúsculas y sin espacios adicionales."""
        return palabra.strip().lower()

    def agregar(
        self,
        palabra: str,
        definicion: str,
        categoria: str = "General",
        ejemplos: Optional[List[str]] = None,
        sinonimos: Optional[List[str]] = None,
    ) -> bool:
        """
        Agrega una nueva palabra al diccionario.
        Retorna True si se agregó con éxito, False si la palabra ya existía.
        """
        palabra_limpia = palabra.strip()
        clave = self._normalizar_clave(palabra_limpia)

        if not clave:
            raise ValueError("La palabra no puede estar vacía.")

        if clave in self.datos:
            return False

        self.datos[clave] = {
            "palabra": palabra_limpia,
            "definicion": definicion.strip(),
            "categoria": categoria.strip() if categoria else "General",
            "ejemplos": [e.strip() for e in (ejemplos or []) if e.strip()],
            "sinonimos": [s.strip() for s in (sinonimos or []) if s.strip()],
        }
        self.guardar_datos()
        return True

    def buscar(self, palabra: str) -> Optional[Dict[str, Any]]:
        """Busca una palabra por coincidencia exacta (no distingue mayúsculas/minúsculas)."""
        clave = self._normalizar_clave(palabra)
        return self.datos.get(clave)

    def buscar_parcial(self, termino: str) -> Dict[str, Dict[str, Any]]:
        """Busca palabras que contengan el término ingresado o cuya definición coincida."""
        termino_norm = self._normalizar_clave(termino)
        if not termino_norm:
            return {}

        resultados = {}
        for clave, info in self.datos.items():
            if (
                termino_norm in clave
                or termino_norm in info.get("definicion", "").lower()
                or any(termino_norm in s.lower() for s in info.get("sinonimos", []))
            ):
                resultados[clave] = info
        return resultados

    def editar(
        self,
        palabra: str,
        definicion: Optional[str] = None,
        categoria: Optional[str] = None,
        ejemplos: Optional[List[str]] = None,
        sinonimos: Optional[List[str]] = None,
    ) -> bool:
        """
        Actualiza los datos de una palabra existente.
        Retorna True si se actualizó, False si no se encontró la palabra.
        """
        clave = self._normalizar_clave(palabra)
        if clave not in self.datos:
            return False

        item = self.datos[clave]
        if definicion is not None:
            item["definicion"] = definicion.strip()
        if categoria is not None:
            item["categoria"] = categoria.strip() if categoria else "General"
        if ejemplos is not None:
            item["ejemplos"] = [e.strip() for e in ejemplos if e.strip()]
        if sinonimos is not None:
            item["sinonimos"] = [s.strip() for s in sinonimos if s.strip()]

        self.guardar_datos()
        return True

    def eliminar(self, palabra: str) -> bool:
        """
        Elimina una palabra del diccionario.
        Retorna True si se eliminó, False si no existía.
        """
        clave = self._normalizar_clave(palabra)
        if clave in self.datos:
            del self.datos[clave]
            self.guardar_datos()
            return True
        return False

    def listar(self, categoria: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """Lista todas las palabras o filtra por categoría."""
        if not categoria:
            return dict(sorted(self.datos.items(), key=lambda x: x[0]))

        categoria_norm = categoria.strip().lower()
        return {
            k: v
            for k, v in sorted(self.datos.items(), key=lambda x: x[0])
            if v.get("categoria", "").strip().lower() == categoria_norm
        }

    def obtener_categorias(self) -> List[str]:
        """Obtiene la lista de categorías únicas presentes en el diccionario."""
        categorias = {info.get("categoria", "General") for info in self.datos.values()}
        return sorted(list(categorias))

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Retorna estadísticas básicas sobre el diccionario."""
        total = len(self.datos)
        categorias = self.obtener_categorias()
        return {
            "total_palabras": total,
            "total_categorias": len(categorias),
            "categorias": categorias,
            "archivo": self.ruta_archivo,
        }
