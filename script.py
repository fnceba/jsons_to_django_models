
import datetime
from typing import Any, Iterable
import json
import requests
from url_list import urls

def get_field(value: Any, existing_field:str=None):
    type_to_field_dict = {
        "<class 'int'>":'IntegerField(**nb)',
        "<class 'bool'>":'BooleanField()',
        "<class 'float'>":'FloatField(**nb)'
    }

    if type(value) is type(None):
        return existing_field
    
    try:
        datetime.datetime.strptime(str(value), "%Y-%m-%dT%H:%M:%S%z")
        return 'DateTimeField(**nb)'
    except ValueError:
        pass
    if type(value) is str:
        if existing_field and existing_field.startswith('TextField'):
            return existing_field
        return 'CharField(max_length=100,**nb)' if len(value)<100 else 'TextField(**nb)'

    return type_to_field_dict[str(type(value))]

def get_new_dict(prefix:str, olddict:dict) -> dict:
    keys = olddict.keys()
    ret={}
    for key in keys:
        ret[prefix+'_'+key]=olddict[key]

    return ret

def extend_dicts(main_fields:dict, extra_models:dict, json_list:list, nonefields:list):
    for i, json in enumerate(json_list):
        #print(i)
        keys = list(json.keys())
        for key in keys:
            if type(json[key]) is list:
                extra_models[key] = {**extra_models.get(key, {}), **(create_django_models(json[key],key)[0])}
                continue
            if type(json[key]) is dict:
                #json = {**json, **get_new_dict(key,json[key])}
                main_fields, extra_models, nonefields = extend_dicts(main_fields,extra_models,[get_new_dict(key,json[key])], nonefields)
                keys = list(json.keys())
                continue
            
            field = get_field(json[key], main_fields.get(key, None))
            if field:
                main_fields[key] = field
                if key in nonefields:
                    nonefields.remove(key)
            elif key not in nonefields:
                nonefields.append(key)      
    return main_fields, extra_models, nonefields

def create_django_models(json_list:Iterable[dict]) -> tuple[dict,dict]:
    
    main_fields = {}
    extra_models = {}
    nonefields = []
    return extend_dicts(main_fields,extra_models, json_list, nonefields)


main_fields, extra_models, nonefields = create_django_models(map(lambda url: json.loads(requests.get(url).content), urls))

for key,value in main_fields.items():
    print(key+' = '+value)

for key,fields in extra_models.items():
    print(key, extra_models[key])
    for kkey,value in fields.items():
        print(kkey+' = '+value)

print(nonefields)

