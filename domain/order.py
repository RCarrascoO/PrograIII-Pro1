from datetime import datetime

class Order:
    def __init__(self, order_id, origin, destination, priority, status="pending", cost=None, route=None, completed_at=None):
        self.order_id = order_id
        self.origin = origin
        self.destination = destination
        self.priority = priority
        self.status = status
        self.cost = cost
        self.route = route
        self.completed_at = completed_at

    def to_dict(self):
        return {
            "order_id": self.order_id,
            "origin": self.origin,
            "destination": self.destination,
            "priority": self.priority,
            "status": self.status,
            "cost": self.cost,
            "route": self.route.path_str() if self.route else None,  # <-- Esto lo hace legible
            "completed_at": str(self.completed_at) if self.completed_at else None,
        }
    
    def complete(self, cost):
        self.status = "completed"
        self.completed_at = datetime.now()
        self.cost = cost