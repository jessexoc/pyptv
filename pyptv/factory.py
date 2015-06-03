
class TypeFactory(object):

    def __init__(self, client):
        self.client = client

    def create(self, transport_type, *args, **kwargs):
        klass = self.classes[transport_type]
        cls = klass(*args, **kwargs)
        cls._client = self.client
        return cls
