class Vertex:
    """Clase que representa un vértice (nodo) en un grafo."""
    __slots__ = '_element'

    def __init__(self, element):
        """Inicializa el vértice con el elemento dado."""
        self._element = element  # Asignar el valor del elemento recibido

    def element(self):
        """Devuelve el elemento asociado a este vértice."""
        return self._element  # Retornar el valor almacenado en _element

    def __hash__(self):
        """Permite usar el vértice como clave en diccionarios o sets."""
        return hash(self._element)  # Usar id(self) para generar un hash único

    def __str__(self):
        """Devuelve la representación en string del vértice (su contenido)."""
        return self._element  # Retornar el elemento como string

    def __repr__(self):
        """Representación oficial de la clase Vertex."""
        return f"Vertex({self._element})"  # Usar _element
