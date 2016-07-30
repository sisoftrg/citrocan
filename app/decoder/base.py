import importlib

from six import PY3


class Decoder(object):

    def __new__(cls, *args, **kwargs):
        instance = object.__new__(cls, *args)
        ids = [prop_name for prop_name, prop in instance.__dict__.items()
               if callable(prop) and prop_name.startswith('id_') and prop_name != 'id_else']
        instance.supported_ids = ids
        return instance

    def __setitem__(self, key, value):
        self.decode(key, value)

    def decode(self, id, data, data_len=None):
        if not data_len:
            data_len = len(data)
        data = data[:data_len]
        if isinstance(id, int):
            id = hex(id)
        if id in self.supported_ids:
            f = getattr(self, 'id_%s' % id)
            f(data)
        else:
            self.id_else(id, data)

    def id_else(self, id, data):
        pass

    @staticmethod
    def get_str(b):
        if PY3:
            ba = bytes(b).strip(b'\0')
        else:
            ba = bytes(b''.join([chr(x) for x in b if x]))
        try:
            s = ba.decode('utf8')
        except UnicodeDecodeError:
            try:
                s = ba.decode('cp1251', errors='replace')
            except UnicodeDecodeError:
                s = "<bad name>"
            except LookupError:
                s = "<wrong program build>"
        return s.strip()


class DecoderGroup(object):

    def __init__(self, decoders, proxy_attributes=False):
        self._decoders = []
        self.proxy_attributes = proxy_attributes
        for decoder in decoders:
            module, cls = decoder.rsplit('.', 1)
            module = importlib.import_module(module)
            attr_name = cls[:-7] if cls.endswith('Decoder') else cls
            attr_name = attr_name.lower()
            attr = getattr(module, cls)()
            self._decoders.append(attr_name)
            setattr(self, attr_name, attr)

    def __getattr__(self, item):
        if not self.proxy_attributes:
            raise AttributeError
        for decoder in self.decoders:
            attr = getattr(decoder, item, None)
            if attr:
                return attr

    @property
    def decoders(self):
        return [getattr(self, name) for name in self._decoders]

    def decode(self, id, data, data_len):
        for decoder in self.decoders:
            decoder.decode(id, data, data_len)
