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