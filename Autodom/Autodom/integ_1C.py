import requests as rq
from datetime import datetime
import urllib
from ChainControl.models import Client, Contract, Bank, Currency, Bank_account
from . import settings

TOKEN_1C = 'gFsfzvrSayQ7QDTZmax61gdsMWSzwJYOqx5S'
try:

    USER_1C=settings.USER_1C.encode()
    PASSWORD_1C=settings.PASSWORD_1C.encode()
    ROOT_URL_1C=settings.ROOT_URL_1C
except:
    USER_1C=settings.USER_1C
    PASSWORD_1C=settings.PASSWORD_1C
    ROOT_URL_1C=settings.ROOT_URL_1C

def delClients():
    clients = Client.objects.filter(request__isnull=True)
    payload ={
        
        '$format':'json',
        '$orderby':'Description'}
    for client in clients:
        payload['$filter'] = 'Ref_Key eq guid\''+client.guid+'\' and DeletionMark eq false'
        rjs = get1C("Catalog_Контрагенты", payload)
        print(payload)
        
        if not 'value' in rjs or len(rjs['value'])==0:
            client.delete()
    
    bank_accounts = Bank_account.objects.filter(request__isnull=True)
    for ba in bank_accounts:
        payload['$filter'] = 'Ref_Key eq guid\''+ba.guid+'\' and DeletionMark eq false'
        rjs = get1C("Catalog_БанковскиеСчета",payload)
        print(payload)
        
        if not 'value' in rjs or len(rjs['value'])==0:
            ba.delete()

    contracts = Contract.objects.filter(request__isnull=True)
    for contract in contracts:
        payload['$filter'] = 'Ref_Key eq guid\''+contract.guid+'\' and DeletionMark eq false'
        rjs = get1C("Catalog_ДоговорыКонтрагентов",payload)
        print(payload)
        
        if not 'value' in rjs or len(rjs['value'])==0:
            contract.delete()


def getClients(guid=None):
    getCurrency()
    getBanks()

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
            
            obj.guid = el['Ref_Key']
            obj.biin = el['ИдентификационныйКодЛичности']
            obj.name = el['Description']
            obj.KBE  = el['КБЕ']
            obj.save()
            #if created:
            #    obj.guid = el['Ref_Key']
            #    obj.biin = el['ИдентификационныйКодЛичности']
            #    obj.name = el['Description']
            #    obj.KBE  = el['КБЕ']
            #    obj.save()
                
            getContracts(obj)
            getBank_accounts(obj)
                
    return True

def getContracts(client):
    payload ={
        '$filter':'Owner_Key eq guid\''+client.guid+'\' and IsFolder eq false and DeletionMark eq false',
        '$format':'json',
        '$orderby':'Description'}
    
    count = get1C("Catalog_ДоговорыКонтрагентов",payload,True)
    print(fr'total count {count}')
    step=20
    for i in range(0,count,step):
        payload['$top'] = 20
        payload['$skip'] = i
        print('skip='+str(payload['$skip']))
        rjs = get1C("Catalog_ДоговорыКонтрагентов",payload)
        for el in rjs['value']:
            obj, created = Contract.objects.get_or_create(guid=el['Ref_Key'], client=client)

            obj.guid = el['Ref_Key']
            obj.client = client
            obj.name = el['Description']
            obj.number  = el['НомерДоговора']
            obj.date = None if el['ДатаДоговора'] == '0001-01-01T00:00:00' else datetime.strptime( el['ДатаДоговора'] ,"%Y-%m-%dT%H:%M:%S")
            obj.start_date = None if el['ДатаНачалаДействияДоговора'] == '0001-01-01T00:00:00' else datetime.strptime( el['ДатаНачалаДействияДоговора'] , "%Y-%m-%dT%H:%M:%S")
            obj.end_date = None if el['ДатаОкончанияДействияДоговора'] == '0001-01-01T00:00:00' else datetime.strptime( el['ДатаОкончанияДействияДоговора'] , "%Y-%m-%dT%H:%M:%S")
            obj.currency  = None if el['ВалютаВзаиморасчетов_Key']=='00000000-0000-0000-0000-000000000000' else Currency.objects.get(guid=el['ВалютаВзаиморасчетов_Key'])
            obj.save()
            
                
            #if created:
            #    obj.guid = el['Ref_Key']
            #    obj.client = client
            #    obj.name = el['Description']
            #    obj.number  = el['НомерДоговора']
            #    obj.date = None if el['ДатаДоговора'] == '0001-01-01T00:00:00' else datetime.strptime( el['ДатаДоговора'] ,"%Y-%m-%dT%H:%M:%S")
            #    obj.start_date = None if el['ДатаНачалаДействияДоговора'] == '0001-01-01T00:00:00' else datetime.strptime( el['ДатаНачалаДействияДоговора'] , "%Y-%m-%dT%H:%M:%S")
            #    obj.end_date = None if el['ДатаОкончанияДействияДоговора'] == '0001-01-01T00:00:00' else datetime.strptime( el['ДатаОкончанияДействияДоговора'] , "%Y-%m-%dT%H:%M:%S")
            #    obj.save()
            #    print('created'+el['Description'])
    return True

def getBank_accounts(client):
    payload ={
        '$filter':'Owner eq cast(guid\''+client.guid+'\', \'Catalog_Контрагенты\') and DeletionMark eq false',
        '$format':'json',
        '$orderby':'Description'}
    
    count = get1C("Catalog_БанковскиеСчета",payload,True)
   
    print(fr'total count {count}')
    step=20
    for i in range(0,count,step):
        payload['$top'] = 20
        payload['$skip'] = i
        print('skip='+str(payload['$skip']))
        rjs = get1C("Catalog_БанковскиеСчета",payload)
        for el in rjs['value']:
            bank = Bank.objects.get(guid= el['Банк_Key'] ) if el['Банк_Key'] != '00000000-0000-0000-0000-000000000000' else None
            currency = Currency.objects.get( guid = el['ВалютаДенежныхСредств_Key'] )
            obj, created = Bank_account.objects.get_or_create(guid=el['Ref_Key'], client=client,defaults={
                'bank':bank,
                'currency':currency,
                })
            
            obj.guid = el['Ref_Key']
            obj.client = client
            obj.bank = bank
            obj.currency  = currency
            obj.account_number = el['НомерСчета']
            obj.save()
                
            #if created:
            #    obj.guid = el['Ref_Key']
            #    obj.client = client
            #    obj.bank = bank
            #    obj.currency  = currency
            #    obj.account_number = el['НомерСчета']
            #    obj.save()
            #    print('created'+el['Description'])

    return True

def getBanks():
    payload ={
        '$filter':'IsFolder eq false and DeletionMark eq false',
        '$format':'json',
        '$orderby':'Description'}
    
    count = get1C("Catalog_Банки",payload,True)
    print(fr'total count {count}')
    step=20
    for i in range(0,count,step):
        payload['$top'] = 20
        payload['$skip'] = i
        print('skip='+str(payload['$skip']))
        rjs = get1C("Catalog_Банки",payload)
        for el in rjs['value']:
            obj, created = Bank.objects.get_or_create(guid=el['Ref_Key'])
            
            obj.guid = el['Ref_Key']
            obj.name = el['Description']
            obj.BIK = el['БИК']
            obj.save()
                
            #if created:
            #    obj.guid = el['Ref_Key']
            #    obj.name = el['Description']
            #    obj.BIK = el['БИК']
            #    obj.save()
            #    print('created'+el['Description'])
    return True

def getCurrency():
    payload ={
        '$filter':'DeletionMark eq false',
        '$format':'json',
        '$orderby':'Description'}
    
    count = get1C("Catalog_Валюты",payload,True)
    print(fr'total count {count}')
    step=20
    for i in range(0,count,step):
        payload['$top'] = 20
        payload['$skip'] = i
        print('skip='+str(payload['$skip']))
        rjs = get1C("Catalog_Валюты",payload)
        for el in rjs['value']:
            obj, created = Currency.objects.get_or_create(guid=el['Ref_Key'])
            
            obj.guid = el['Ref_Key']
            obj.name = el['Description']
            obj.code = el['Code']
            obj.code_str = el['БуквенныйКод']
            obj.save()
                
            #if created:
            #    obj.guid = el['Ref_Key']
            #    obj.name = el['Description']
            #    obj.code = el['Code']
            #    obj.code_str = el['БуквенныйКод']
            #    obj.save()
            #    print('created'+el['Description'])

    return True

def get1C(entity,payload,is_count=False):
    params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote)
    r = rq.get(ROOT_URL_1C+entity+('/$count' if is_count else "/"),auth=(USER_1C,PASSWORD_1C),params=params)
    return r.json()
