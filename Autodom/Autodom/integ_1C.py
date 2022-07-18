import requests as rq
import json, urllib
from ChainControl.models import Client

TOKEN_1C = 'gFsfzvrSayQ7QDTZmax61gdsMWSzwJYOqx5S'
USER_1C=fr'МА_АДМИН'.encode()
PASSWORD_1C=fr'741852'.encode()
ROOT_URL_1C="http://185.233.3.224/Hino_test/odata/standard.odata/"

def getClients(guid=None):
    payload ={
        '$filter':'IsFolder eq false and DeletionMark eq false',
        '$format':'json',
        '$orderby':'Description'}
    
    count = get1C("Catalog_Контрагенты",payload,True)
    print(fr'total count {count}')
    step=20
    for i in range(0,count,step):
        payload['$top'] = 20
        payload['$skip'] = i
        print('skip='+str(payload['$skip']))
        rjs = get1C("Catalog_Контрагенты",payload)
        for el in rjs['value']:
            obj, created = Client.objects.get_or_create(guid=el['Ref_Key'])
            if created:
                obj.guid = el['Ref_Key']
                obj.biin = el['ИдентификационныйКодЛичности']
                obj.name = el['Description']
                obj.KBE  = el['КБЕ']
                obj.save()
                print('created'+el['Description'])
    return True


def get1C(entity,payload,is_count=False):
    params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote)
    r = rq.get(ROOT_URL_1C+entity+('/$count' if is_count else "/"),auth=(USER_1C,PASSWORD_1C),params=params)
    return r.json()
