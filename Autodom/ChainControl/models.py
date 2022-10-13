
from datetime import datetime
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Role(models.Model):
    name= models.CharField(verbose_name='Наименование',max_length = 100,blank=True,null=True)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

class UserProfile(models.Model):
    user= models.OneToOneField(User, on_delete = models.CASCADE, verbose_name='Пользователь')
    role= models.ForeignKey(Role,on_delete = models.CASCADE, verbose_name='Роль')
    tg_chat_id = models.IntegerField(verbose_name='ID чата (телеграм)', blank=True,null=True)
    def __str__(self):
        return self.user.username + " доп. информация"

    class Meta:
        verbose_name = 'Доп. информация'
        verbose_name_plural = 'Доп. информации'

class Individual(models.Model):
    guid = models.CharField(verbose_name = 'ГУИД 1с',max_length = 36)
    name= models.CharField(verbose_name='Наименование', max_length = 150)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Физическое лицо'
        verbose_name_plural = 'Физические лица'

class Client(models.Model):
    guid = models.CharField(verbose_name = 'ГУИД 1с',max_length = 36)
    biin= models.CharField(verbose_name='ИИН',max_length = 12, blank=True,null=True)
    name= models.CharField(verbose_name='Наименование', max_length = 150)
    KBE = models.CharField(verbose_name='КБЕ', max_length = 2, blank=True,null=True)
    def __str__(self):
        return self.name +", "+self.biin

    class Meta:
        verbose_name = 'Контрагент'
        verbose_name_plural = 'Контрагенты'

class Currency(models.Model):
    guid = models.CharField(verbose_name = 'ГУИД 1с',max_length = 36)
    name = models.CharField(verbose_name='Наименование',max_length = 50)
    code = models.CharField(verbose_name='Код валюты',max_length = 3,blank=True,null=True)
    code_str = models.CharField(verbose_name='Код валюты строкой', max_length = 3,blank=True,null=True)

    def __str__(self):
        return self.code_str

    class Meta:
        verbose_name = 'Валюта'
        verbose_name_plural = 'Валюты'

class Contract(models.Model):
    guid = models.CharField(verbose_name = 'ГУИД 1с',max_length = 36)
    client = models.ForeignKey(Client,on_delete = models.CASCADE, verbose_name='Контрагент')
    name= models.CharField(verbose_name='Наименование',max_length = 200)
    number = models.CharField(verbose_name='Номер договора',max_length = 20,blank=True,null=True)
    date = models.DateField(verbose_name='Дата договора',blank=True,null=True)
    start_date = models.DateField(verbose_name='Дата начала',blank=True,null=True)
    end_date = models.DateField(verbose_name = 'Дата окончания',blank=True,null=True)
    currency = models.ForeignKey(Currency,verbose_name='Валюта договора', blank=True,null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Договор контрагента'
        verbose_name_plural = 'Договоры контрагентов'

class Bank(models.Model):
    guid = models.CharField(verbose_name = 'ГУИД 1с',max_length = 36)
    name = models.CharField(verbose_name='Наименование',max_length = 200)
    BIK = models.CharField(verbose_name = 'БИК',max_length = 10)

    def __str__(self):
        return self.name +", "+self.BIK

    class Meta:
        verbose_name = 'Банк'
        verbose_name_plural = 'Банки'




class Payment_type(models.Model):
    name = models.CharField(verbose_name='Наименование',max_length = 50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тип оплаты'
        verbose_name_plural = 'Типы оплаты'

class Bank_account(models.Model):
    guid = models.CharField(verbose_name = 'ГУИД 1с',max_length = 36)
    client = models.ForeignKey(Client,on_delete = models.CASCADE, verbose_name='Контрагент')
    bank = models.ForeignKey(Bank,on_delete= models.CASCADE,null=True, verbose_name='Банк')
    currency = models.ForeignKey(Currency,on_delete = models.CASCADE, verbose_name='Валюта')
    account_number = models.CharField(verbose_name = 'Номер счета',max_length = 100)

    def __str__(self):
        return self.account_number + ", "+ self.currency.code_str

    class Meta:
        verbose_name = 'Банковский счет'
        verbose_name_plural = 'Банковские счета'

class Individual_bank_account(models.Model):
    guid = models.CharField(verbose_name = 'ГУИД 1с',max_length = 36)
    individual = models.ForeignKey(Individual, on_delete= models.CASCADE, null=True, verbose_name='Физ. лицо')
    bank = models.ForeignKey(Bank,on_delete= models.CASCADE,null=True, verbose_name='Банк')
    account_number = models.CharField(verbose_name = 'Номер счета',max_length = 100)

    def __str__(self):
        return self.account_number

    class Meta:
        verbose_name = 'Карт-счет'
        verbose_name_plural = 'Карт-счета'

class Request_type(models.Model):
    name = models.CharField(verbose_name='Наименование',max_length= 100)
    roles = models.ManyToManyField(Role,through = 'Ordering', verbose_name='Порядок согласования')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Вид заявки'
        verbose_name_plural = 'Виды заявок'

class Request(models.Model):
    user = models.ForeignKey(User,models.SET_NULL,blank=True,null=True, verbose_name='Пользователь')
    date = models.DateField(verbose_name='Дата создания',default=datetime.now,blank=True)
    type = models.ForeignKey(Request_type, on_delete = models.CASCADE, verbose_name='Вид заявки')
    payment_type = models.ForeignKey(Payment_type, on_delete = models.CASCADE, verbose_name='Тип оплаты')
    client = models.ForeignKey(Client, on_delete = models.CASCADE, verbose_name='Контрагент')
    contract = models.ForeignKey(Contract, on_delete = models.CASCADE, verbose_name='Договор')
    bank_account = models.ForeignKey(Bank_account, on_delete = models.CASCADE, verbose_name='Банковский счет')
    complete_before = models.DateField(verbose_name='Завершить до')
    invoice_number = models.CharField(verbose_name='Номер счета на оплату', max_length = 20)
    invoice_date = models.DateField(verbose_name='Дата счета на оплату')
    invoice_details = models.CharField(verbose_name='Содержание',max_length = 200,blank=True,null=True)
    AVR_date = models.DateField(verbose_name='Дата оказания услуг/передачи товара',blank=True,null=True)
    sum = models.FloatField(verbose_name = 'Сумма')
    comment = models.CharField(verbose_name ='Комментарий',max_length = 200,blank=True,null=True)
    currency = models.ForeignKey(Currency, on_delete = models.CASCADE,verbose_name='Валюта',blank=True,null=True)
    
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

    def get_absolute_url(self):
        return reverse('request_item', args=[str(self.id)])

    class Meta:
        ordering = ["complete_before"]
        verbose_name = 'Заявка'
        verbose_name_plural = "Заявки"


class Approval(models.Model):
    user = models.ForeignKey(User,models.SET_NULL,blank=True,null=True, verbose_name='Пользователь')
    role = models.ForeignKey(Role,models.SET_NULL,blank=True,null=True, verbose_name='Роль')
    new_status = models.CharField(verbose_name='Установленный статус', max_length = 2, choices=Request.StatusTypes.choices, default=Request.StatusTypes.ON_APPROVAL)
    order = models.IntegerField(verbose_name = 'Порядок согласования')
    request = models.ForeignKey(Request,on_delete = models.CASCADE, verbose_name='Заявка')

    def __str__(self):
        return str(self.request)+", "+str(self.role)+", "+str(self.new_status)

    class Meta:
        verbose_name = 'Согласование'
        verbose_name_plural = 'Согласования'



class Ordering(models.Model):
    user = models.ForeignKey(User,models.SET_NULL,blank=True,null=True, verbose_name='Пользователь')
    role = models.ForeignKey(Role, on_delete = models.CASCADE, verbose_name='Роль')
    request_type = models.ForeignKey(Request_type, on_delete = models.CASCADE, verbose_name='Вид заявки')
    order = models.IntegerField(verbose_name='Порядок согласования')

    class Meta:
        verbose_name = 'Порядок согласования'
        verbose_name_plural = 'Порядки согласования'

class Initiator(models.Model):
    user = models.ForeignKey(User,models.SET_NULL,blank=True,null=True, verbose_name='Пользователь')
    role = models.ForeignKey(Role, on_delete = models.CASCADE, verbose_name='Роль')
    request_type = models.ForeignKey(Request_type, on_delete = models.CASCADE, verbose_name='Вид заявки')

    class Meta:
        verbose_name = 'Иницатор'
        verbose_name_plural = 'Инициаторы'

class RequestExecutor(models.Model):
    role = models.ForeignKey(Role, on_delete = models.CASCADE, verbose_name='Роль')
    request_type = models.ForeignKey(Request_type, on_delete = models.CASCADE, verbose_name='Вид заявки')

    class Meta:
        verbose_name = 'Исполнитель'
        verbose_name_plural = 'Исполнители'





class Additional_file(models.Model):
    request_1= models.ForeignKey(Request,on_delete = models.CASCADE, verbose_name='Заявка')
    file = models.FileField(verbose_name='Приложение')

    class Meta:
        verbose_name = 'Вложение'
        verbose_name_plural = 'Вложения'

class Email_templates(models.Model):
    class Email_types(models.TextChoices):
        INITIAL_NOTIFICATION = '1', _('Создана новая заявка')
        WAITING_FOR_APPROVAL_NOTIFICATION = '10', _('Заявка ожидает согласования')
        REWORKED_NOTIFICATION = '20', _('Заявка на доработке')
        CANCELED_NOTIFICATION = '50', _('Заявка отменена')
        APPROVED_NOTIFICATION = '70', _('Заявка согласована всеми участниками и ожидает исполнения')
        DONE_NOTIFICATION = '100', _('Заявка выполнена')
        DAILY_APPROVAL_NOTIFICATION = '200', _('Ежедневное напоминание о необходимости согласования')
        DAILY_EXECUTOR_NOTIFICATION = '210', _('Ежедневное напоминание о необходимости исполнения')
        DEADLINE_PASSED_NOTIFICATION = '220', _('Напоминание о просроченных заявках')

    email_type = models.CharField(verbose_name='Тип шаблона', max_length=3,choices= Email_types.choices,default=Email_types.INITIAL_NOTIFICATION,unique=True)
    subject = models.CharField(verbose_name='Тема письма', max_length=100,blank=False,null=False)
    text = models.TextField(verbose_name='Текст письма', max_length=500,blank=False,null=False)
    
    notification_subject = models.CharField(verbose_name='Заголовок уведомления', max_length=100,blank=False,null=False,default='123')
    notification_text = models.TextField(verbose_name='Текст уведомления', max_length=400,blank=False,null=False,default='123')

    tg_text = models.TextField(verbose_name='Текст телеграмм сообщения', max_length=400,blank=False,null=False,default='123')

    def __str__(self):
        return self.get_email_type_display()

    class Meta:
        verbose_name = 'Шаблон уведомлений'
        verbose_name_plural = 'Шаблоны уведомлений'
    
    
class History(models.Model):
    request = models.ForeignKey(Request, on_delete= models.CASCADE, verbose_name='Заявка')
    date = models.DateTimeField(verbose_name='Дата события',default=datetime.now,blank=True)
    user = models.ForeignKey(User,models.SET_NULL, null=True, verbose_name='Пользователь')
    status = models.CharField(verbose_name='Статус', max_length = 2, choices=Request.StatusTypes.choices, blank=True, null=True)
    comment = models.TextField(verbose_name ='Комментарий',max_length = 200, blank=True, null=True)

    def __str__(self):
        return str(self.request)+", "+str(self.user)+", "+str(self.status)+", "+self.comment

    class Meta:
        verbose_name = 'История изменения'
        verbose_name_plural = 'История изменений'