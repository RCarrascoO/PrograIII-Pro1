class Route:
    def __init__(self, path, cost):
        self.path = path  # Lista de vértices
        self.cost = cost
        self.frequency = 1
    
    def path_str(self):
        return "->".join(str(v) for v in self.path)
    
    def increment_frequency(self):
        self.frequency += 1