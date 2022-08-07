from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField

class Role(models.Model):
    name= models.TextField(verbose_name='Наименование',max_length = 100,blank=True,null=True)
    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user= models.OneToOneField(User, on_delete = models.CASCADE)
    role= models.ForeignKey(Role,on_delete = models.CASCADE)

    def __str__(self):
        return self.user.username + " доп. информация"

class Client(models.Model):
    guid = models.TextField(verbose_name = 'ГУИД 1с',max_length = 36)
    biin= models.TextField(verbose_name='ИИН',max_length = 12, blank=True,null=True)
    name= models.TextField(verbose_name='Наименование', max_length = 150)
    KBE = models.TextField(verbose_name='КБЕ', max_length = 2, blank=True,null=True)
    def __str__(self):
        return self.name +", "+self.biin

class Contract(models.Model):
    guid = models.TextField(verbose_name = 'ГУИД 1с',max_length = 36)
    client = models.ForeignKey(Client,on_delete = models.CASCADE)
    name= models.TextField(verbose_name='Наименование',max_length = 200)
    number = models.TextField(verbose_name='Номер договора',max_length = 20)
    date = models.DateField(verbose_name='Дата договора')
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(verbose_name = 'Дата окончания')

    def __str__(self):
        return self.name

class Bank(models.Model):
    name = models.TextField(verbose_name='Наименование',max_length = 200)
    BIK = models.TextField(verbose_name = 'БИК',max_length = 10)

    def __str__(self):
        return self.name +", "+self.BIK


class Currency(models.Model):
    name = models.TextField(verbose_name='Наименование',max_length = 50)
    code = models.TextField(verbose_name='Код валюты',max_length = 3)
    code_str = models.TextField(verbose_name='Код валюты строкой', max_length = 3)

    def __str__(self):
        return self.code_str

class Payment_type(models.Model):
    name = models.TextField(verbose_name='Наименование',max_length = 50)

    def __str__(self):
        return self.name

class Bank_account(models.Model):
    guid = models.TextField(verbose_name = 'ГУИД 1с',max_length = 36)
    client = models.ForeignKey(Client,on_delete = models.CASCADE)
    bank = models.ForeignKey(Bank,on_delete= models.CASCADE)
    currency = models.ForeignKey(Currency,on_delete = models.CASCADE)
    account_number = models.TextField(verbose_name = 'Номер счета',max_length = 100)

    def __str__(self):
        return self.account_number + ", "+ self.currency.code_str

class Request_type(models.Model):
    name = models.TextField(verbose_name='Наименование',max_length= 100)
    initiator = models.ForeignKey(Role,on_delete=models.SET_NULL,blank=True,null=True, related_name='role_initiator')
    executor = models.ForeignKey(Role,on_delete=models.SET_NULL,blank=True,null=True, related_name='role_executor')
    roles = models.ManyToManyField(Role,through = 'Ordering')

    def __str__(self):
        return self.name

class Request(models.Model):
    user = models.ForeignKey(User,models.SET_NULL,blank=True,null=True,)
    date = models.DateField(verbose_name='Дата создания',default=datetime.now,blank=True)
    type = models.ForeignKey(Request_type, on_delete = models.CASCADE)
    payment_type = models.ForeignKey(Payment_type, on_delete = models.CASCADE)
    client = models.ForeignKey(Client, on_delete = models.CASCADE)
    contract = models.ForeignKey(Contract, on_delete = models.CASCADE)
    bank_account = models.ForeignKey(Bank_account, on_delete = models.CASCADE)
    complete_before = models.DateField(verbose_name='Завершить до')
    invoice_number = models.TextField(verbose_name='Номер счета на оплату', max_length = 20)
    invoice_date = models.DateField(verbose_name='Дата счета на оплату')
    invoice_details = models.TextField(verbose_name='Содержание',max_length = 200)
    AVR_date = models.DateField(verbose_name='Дата оказания услуг/передачи товара')
    sum = models.FloatField(verbose_name = 'Сумма')
    comment = models.TextField(verbose_name ='Комментарий',max_length = 200)
    
    
    class StatusTypes(models.TextChoices):
        OPEN = 'OP', _('Открыта')
        ON_APPROVAL = 'OA', _('На согласовании')
        APPROVED = 'AP', _('Согласована')
        ON_REWORK = 'OR', _('На доработке')
        CANCELED = 'CA', _('Отменена')
        DONE = 'DO', _('Выполнена')

    status = models.CharField(verbose_name='Статус заявки', max_length = 2, choices=StatusTypes.choices, default=StatusTypes.ON_APPROVAL)
    

    def __str__(self):
        return self.client.name + ", "+ str(self.complete_before)+", "+str(self.sum)

    class Meta:
        ordering = ["complete_before"]
        verbose_name_plural = "Requests"


class Approval(models.Model):
    user = models.ForeignKey(User,models.SET_NULL,blank=True,null=True,)
    role = models.ForeignKey(Role,models.SET_NULL,blank=True,null=True,)
    new_status = models.CharField(verbose_name='Установленный статус', max_length = 2, choices=Request.StatusTypes.choices, default=Request.StatusTypes.ON_APPROVAL)
    order = models.IntegerField(verbose_name = 'Порядок согласования')
    request = models.ForeignKey(Request,on_delete = models.CASCADE)

    def __str__(self):
        return str(self.request)+", "+str(self.role)+", "+str(self.is_approved)



class Ordering(models.Model):
    user = models.ForeignKey(User,models.SET_NULL,blank=True,null=True,)
    role = models.ForeignKey(Role, on_delete = models.CASCADE)
    request_type = models.ForeignKey(Request_type, on_delete = models.CASCADE)
    order = models.IntegerField(verbose_name='Порядок согласования')





class Additional_file(models.Model):
    request_1= models.ForeignKey(Request,on_delete = models.CASCADE)
    file = models.FileField(verbose_name='Приложение')

class Email_templates(models.Model):
    class Email_types(models.TextChoices):
        INITIAL_NOTIFICATION = '1', _('Создана новая заявка')
        DONE_NOTIFICATION = '100', _('Заявка выполнена')

    email_type = models.CharField(verbose_name='Тип шаблона', max_length=3,choices= Email_types.choices,default=Email_types.INITIAL_NOTIFICATION,unique=True)
    text = HTMLField()
    subject = models.CharField(verbose_name='Тема письма', max_length=100,blank=False,null=False)
    
    
