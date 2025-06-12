class Client:
    def __init__(self, client_id: str, name: str, type_: str, total_orders: int = 0):
        self.client_id = client_id
        self.name = name
        self.type = type_      # Por ejemplo: "premium"
        self.total_orders = total_orders

    def to_dict(self):
        return {
            "client_id": self.client_id,
            "name": self.name,
            "type": self.type,
            "total_orders": self.total_orders
        }

    def __repr__(self):
        return f"<Client {self.client_id} ({self.name}) type={self.type} orders={self.total_orders}>"