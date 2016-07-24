class Decoder(object):

    def __new__(cls, *args, **kwargs):
        instance = object.__new__(cls, *args)
        ids = [prop_name for prop_name, prop in instance.__dict__.iteritems()
               if callable(prop) and prop_name.startswith('id_') and prop_name != 'id_else']
        instance.supported_ids = ids
        return instance

    def __setitem__(self, key, value):
        self.parse(key, value)

    def parse(self, id, data):
        if isinstance(id, int):
            id = hex(id)
        if id in self.supported_ids:
            f = getattr(self, 'id_%s' % id)
            if f:
                f(data)
            else:
                self.id_else(id, data)

    def id_else(self, id, data):
        pass
