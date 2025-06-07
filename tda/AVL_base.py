class AVLNode:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None
        self.height = 1

class AVL:
    def __init__(self):
        self.root = None
    
    def insert(self, key, value):
        self.root = self._insert(self.root, key, value)
    
    def _insert(self, node, key, value):
        if not node:
            return AVLNode(key, value)
        
        if key < node.key:
            node.left = self._insert(node.left, key, value)
        elif key > node.key:
            node.right = self._insert(node.right, key, value)
        else:
            return node  # No duplicados
        
        node.height = 1 + max(self._get_height(node.left), 
                          self._get_height(node.right))
        
        balance = self._get_balance(node)
        
        # Casos de rotación
        if balance > 1 and key < node.left.key:
            return self._right_rotate(node)
        if balance < -1 and key > node.right.key:
            return self._left_rotate(node)
        if balance > 1 and key > node.left.key:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)
        if balance < -1 and key < node.right.key:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)
        
        return node
    
    def search(self, key):
        return self._search(self.root, key)
    
    def _search(self, node, key):
        if not node:
            return None
        if key == node.key:
            return node
        elif key < node.key:
            return self._search(node.left, key)
        else:
            return self._search(node.right, key)
    
    def get_most_frequent(self, n=5):
        """Devuelve las n rutas más frecuentes"""
        routes = []
        self.inorder_traversal(lambda node: routes.append((node.key, node.value)))
        return sorted(routes, key=lambda x: x[1].frequency, reverse=True)[:n]
    
    def inorder_traversal(self, callback):
        """Recorrido in-order con callback"""
        self._inorder_traversal(self.root, callback)
    
    def _inorder_traversal(self, node, callback):
        if node:
            self._inorder_traversal(node.left, callback)
            callback(node)
            self._inorder_traversal(node.right, callback)
    
    # Funciones auxiliares para rotaciones y balanceo
    def _get_height(self, node):
        return node.height if node else 0
    
    def _get_balance(self, node):
        return self._get_height(node.left) - self._get_height(node.right) if node else 0
    
    def _left_rotate(self, z):
        y = z.right
        T2 = y.left
        
        y.left = z
        z.right = T2
        
        z.height = 1 + max(self._get_height(z.left), 
                         self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), 
                         self._get_height(y.right))
        
        return y
    
    def _right_rotate(self, z):
        y = z.left
        T3 = y.right
        
        y.right = z
        z.left = T3
        
        z.height = 1 + max(self._get_height(z.left), 
                         self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), 
                         self._get_height(y.right))
        
        return y