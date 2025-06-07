from datetime import datetime

class Order:
    def __init__(self, order_id, origin, destination, priority=1):
        self.id = order_id
        self.origin = origin
        self.destination = destination
        self.priority = priority
        self.created_at = datetime.now()
        self.completed_at = None
        self.status = "pending"
        self.route = None
        self.cost = None
    
    def complete(self, cost):
        self.status = "completed"
        self.completed_at = datetime.now()
        self.cost = cost