def get_compendium_object(base):
    class CompendiumObject(base):
        def __init__(self, *args, **kwargs):
            self.compendium = kwargs['compendium']

        def get(self, filter=None, fields=None):
            return base.get(self, filter=filter, fields=fields)

        def by(self, *args, **kwargs):
            return base.by(self, *args, **kwargs)

    return CompendiumObject


def get_factory(new__init__):
    class Meta(type):
        def __new__(cls, name, bases, namespace):
            old_init = namespace.get('__init__')
            namespace['__init__'] = new__init__

            def __factory_build_object__(cls_obj, *args, **kwargs):
                obj = cls_obj.__new__(cls_obj, *args, **kwargs)
                ins = old_init(obj, *args, **kwargs)
                return ins

            namespace['__factory_build_object__'] = classmethod(__factory_build_object__)
            return super().__new__(cls, name, bases, namespace)
    return Meta
