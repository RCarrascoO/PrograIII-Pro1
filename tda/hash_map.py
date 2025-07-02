class HashMap:
    def __init__(self, size=10):
        self.size = size
        self.buckets = [[] for _ in range(size)]
    
    def _hash(self, key):
        return hash(key) % self.size
    
    def put(self, key, value):
        h = self._hash(key)
        bucket = self.buckets[h]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
    
    def get(self, key):
        h = self._hash(key)
        for k, v in self.buckets[h]:
            if k == key:
                return v
        return None
    
    #len 
    def __len__(self):
        return sum(len(bucket) for bucket in self.buckets)
    
    # Nuevos métodos útiles para los controladores
    def remove(self, key):
        """
        Elimina un par clave-valor
        
        Args:
            key: La clave a eliminar
            
        Returns:
            True si se eliminó correctamente, False si no existía
        """
        h = self._hash(key)
        bucket = self.buckets[h]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                return True
        return False
    
    def keys(self):
        """
        Obtiene todas las claves en el mapa
        
        Returns:
            Lista de claves
        """
        result = []
        for bucket in self.buckets:
            for k, v in bucket:
                result.append(k)
        return result
    
    def values(self):
        """
        Obtiene todos los valores en el mapa
        
        Returns:
            Lista de valores
        """
        result = []
        for bucket in self.buckets:
            for k, v in bucket:
                result.append(v)
        return result
    
    def items(self):
        """
        Obtiene todos los pares clave-valor
        
        Returns:
            Lista de tuplas (clave, valor)
        """
        result = []
        for bucket in self.buckets:
            result.extend(bucket)
        return result

# Crear un alias para que Map sea igual a HashMap
Map = HashMap