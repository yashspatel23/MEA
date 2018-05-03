from collections import OrderedDict


def model_create(model_cls, js, fingerprint_check=True):
    model = model_cls.build(js)
    model = model.db_create(fingerprint_check=fingerprint_check)
    
    resp = OrderedDict()
    resp['created'] = True
    resp['jsdata'] = model.js
    
    return resp


def model_read(model_cls, _id):
    return model_cls.backend_read(_id).js


def model_update(model_cls, js):
    model = model_cls(js)
    model = model.db_update()
     
    resp = OrderedDict()
    resp['updated'] = True
    resp['jsdata'] = model.js
    return resp


def model_delete(model_cls, _id):
    model = model_cls.backend_read(_id)
    model = model.db_delete()
     
    resp = OrderedDict()
    resp['deleted'] = True
    
    resp['jsdata'] = model.js
    return resp


