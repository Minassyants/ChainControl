
import logging
from django import forms
from django.contrib.contenttypes.forms import generic_inlineformset_factory
from django.contrib.contenttypes.models import ContentType
from . import models




class DateInput(forms.DateInput):
    input_type = 'date'
    input_formats = ['%d.%m.%y']



class MissionSearchForm(forms.ModelForm):



    date = forms.DateField(widget=DateInput(attrs={'class' : 'form-control',
                                                 }))
    id = forms.IntegerField(widget=forms.NumberInput(attrs={'class' : 'form-control',
                                                            }))
    status = forms.ChoiceField(choices= models.Mission.StatusTypes.choices + [("","----")],required=False)

    expired = forms.BooleanField(widget= forms.CheckboxInput(attrs={'class' : 'form-check-input',
                                                                    'role' : 'switch'}))

    class Meta:
        model = models.Mission
        fields = ['id','client','user','individual','date','status']
        widgets = {
            'id' : forms.NumberInput(attrs={'class' : 'form-control',}),
            'user' : forms.Select(attrs={'class' : 'form-control',}),
            'client' : forms.Select(attrs={'class' : 'form-control',}),
            'individual' : forms.Select(attrs={'class' : 'form-control',}),
            #'sum' : forms.NumberInput(attrs={'class' : 'form-control',}),
            'date' : forms.DateInput(format='%Y-%m-%d'),
            'status' : forms.Select(attrs={'class' : 'form-control',}),
            'expired' : forms.CheckboxInput(attrs={'class' : 'form-control',
                                                   'role' : 'switch'}),
            }

    def __init__(self, data=None,instance = None, **kwargs):
        super(MissionSearchForm, self).__init__(data=data,instance=instance,**kwargs)
        for i in self.fields:
            self.fields[i].required = False


class RequestSearchForm(forms.ModelForm):



    date = forms.DateField(widget=DateInput(attrs={'class' : 'form-control',
                                                 }))
    id = forms.IntegerField(widget=forms.NumberInput(attrs={'class' : 'form-control',
                                                            }))
    status = forms.ChoiceField(choices= models.Request.StatusTypes.choices + [("","----")],required=False)

    expired = forms.BooleanField(widget= forms.CheckboxInput(attrs={'class' : 'form-check-input',
                                                                    'role' : 'switch'}))

    class Meta:
        model = models.Request
        fields = ['id','client','user','sum','date','status']
        widgets = {
            'id' : forms.NumberInput(attrs={'class' : 'form-control',}),
            'user' : forms.Select(attrs={'class' : 'form-control',}),
            'client' : forms.Select(attrs={'class' : 'form-control',}),
            'sum' : forms.NumberInput(attrs={'class' : 'form-control',}),
            'date' : forms.DateInput(format='%Y-%m-%d'),
            'status' : forms.Select(attrs={'class' : 'form-control',}),
            'expired' : forms.CheckboxInput(attrs={'class' : 'form-control',
                                                   'role' : 'switch'}),
            }

    def __init__(self, data=None,instance = None, **kwargs):
        super(RequestSearchForm, self).__init__(data=data,instance=instance,**kwargs)
        for i in self.fields:
            self.fields[i].required = False
        


class ApprovalForm(forms.ModelForm):

    approval_comment = forms.CharField(label="Комментарий к согласованию",widget=forms.Textarea(attrs={'class':'form-control',
                                                           'rows':'2',
                                                                   }))

    def __init__(self, data=None,instance = None, **kwargs):
        super(ApprovalForm, self).__init__(data=data,instance=instance,**kwargs)
        self.fields['approval_comment'].required = False
        choices = models.Request.StatusTypes.choices
        choices.remove(choices[5])
        choices.remove(choices[0])
        self.fields['new_status'].choices = choices

    def save(self, commit=True):
        approval = super(ApprovalForm, self).save(commit=False)
        #set some other attrs on user here ...
        approval._comment = self.cleaned_data['approval_comment']
        if commit:
            approval.save()

        return approval

    class Meta:
        model = models.Approval
        fields = '__all__'
        widgets = {
            'new_status': forms.Select(),
            'order': forms.HiddenInput(),
            'content_type' : forms.HiddenInput(),
            'object_id' : forms.HiddenInput(),
            'user':forms.HiddenInput(),
            'role':forms.HiddenInput(),
            'request':forms.HiddenInput(),
            'can_edit':forms.HiddenInput()
        }

class RequestForm(forms.ModelForm):

    date = forms.DateField(widget=DateInput(attrs={'class' : 'form-control',
                                                 }))
    complete_before = forms.DateField(widget=DateInput(attrs={'class' : 'form-control',
                                                 }))
    invoice_number = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control',
                                                                   }))
    invoice_date = forms.DateField(widget=DateInput(attrs={'class' : 'form-control',
                                                 }))
    invoice_details = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control',
                                                                    'rows':'5',
                                                                   }))
    AVR_date = forms.DateField(widget=DateInput(attrs={'class' : 'form-control',
                                                 }))
    comment = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control',
                                                           'rows':'2',
                                                                   }))
    is_accountable_person = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class' : 'form-check-input',
                                                 }))

    class Meta:
        model = models.Request
        fields = '__all__'
        widgets = {
            'user' : forms.Select(attrs={'disabled':'true'}),
            'type' : forms.Select(),
            'payment_type' : forms.Select(),
            'client' : forms.Select(),
            'contract' : forms.Select(),
            'individual' : forms.Select(),
            'individual_bank_account' : forms.Select(),
            'bank_account' : forms.Select(),
            'sum' : forms.NumberInput(attrs={'class' : 'form-control',}),
            'date' : forms.DateInput(format='%Y-%m-%d'),
            'complete_before' : forms.DateInput(format='%Y-%m-%d'),
            'invoice_date' : forms.DateInput(format='%Y-%m-%d'),
            'AVR_date' : forms.DateInput(format='%Y-%m-%d'),
            }

    def __init__(self, *args , **kwargs):
        super(RequestForm, self).__init__(*args, **kwargs)
        self.fields['bank_account'].required = False
        self.fields['is_accountable_person'].required = False
        self.fields['currency'].required = False
        self.fields['comment'].required = False
        self.fields['AVR_date'].required = False
        self.fields['invoice_details'].required = False

        #if getattr(self.instance,'type',None) ==None:
        #    try:
        #        initial = kwargs.get('initial',None)
        #        if initial != None:
        #            self.fields['type'].choices = kwargs['initial']['user'].initiator_set.filter(content_type = ContentType.objects.get_for_model(models.Request_type).id).values_list('request_type_id','request_type__name')
        #    except Exception as e:
        #         logging.error(e)


        if getattr(self.instance,'contract',None) !=None:
            self.fields['contract'].choices = self.instance.client.contract_set.values_list('id','name')
        else:
            self.fields['contract'].choices = [("","----")]

        if getattr(self.instance,'bank_account',None) !=None:
            self.fields['bank_account'].choices = self.instance.client.bank_account_set.values_list('id','account_number')
        else:
            self.fields['bank_account'].choices = [("","----")]

        if getattr(self.instance,'client',None) !=None:
            self.fields['client'].choices = [ (str(self.instance.client.id), str(self.instance.client )) ]
        else:
            self.fields['client'].choices = [("","----")]

        if getattr(self.instance,'individual_bank_account',None) !=None:
            self.fields['individual_bank_account'].choices = self.instance.individual.individual_bank_account_set.values_list('id','account_number')
        else:
            self.fields['individual_bank_account'].choices = [("","----")]

        if getattr(self.instance,'individual',None) !=None:
            self.fields['individual'].choices = [ (str(self.instance.individual.id), str(self.instance.individual )) ]
        else:
            self.fields['individual'].choices = [("","----")]

##widgets= {
##"file" : forms.FileInput(attrs = {'class' : 'form-control form-control-sm'})
##},


class MissionForm(forms.ModelForm):

    date = forms.DateField(widget=DateInput(attrs={'class' : 'form-control',
                                                 }))
    complete_before = forms.DateField(widget=DateInput(attrs={'class' : 'form-control',
                                                 }))
    destination = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control',
                                                                   }))
    purpose = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control',
                                                                    'rows':'5',
                                                                   }))
    date_from = forms.DateField(widget=DateInput(attrs={'class' : 'form-control',
                                                 }))
    date_to = forms.DateField(widget=DateInput(attrs={'class' : 'form-control',
                                                 }))
    comment = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control',
                                                           'rows':'2',
                                                                   }))

    class Meta:
        model = models.Mission
        fields = '__all__'
        widgets = {
            'user' : forms.Select(attrs={'disabled':'true'}),
            'type' : forms.Select(),
            'client' : forms.Select(),
            'contract' : forms.Select(),
            'individual' : forms.Select(),
            'ticket_price' : forms.NumberInput(attrs={'class' : 'form-control',}),
            'cost_of_living' : forms.NumberInput(attrs={'class' : 'form-control',}),
            'daily_allowance' : forms.NumberInput(attrs={'class' : 'form-control',}),
            'date' : forms.DateInput(format='%Y-%m-%d'),
            'complete_before' : forms.DateInput(format='%Y-%m-%d'),
            'date_from' : forms.DateInput(format='%Y-%m-%d'),
            'date_to' : forms.DateInput(format='%Y-%m-%d'),
            }

    def __init__(self, *args , **kwargs):
        super(MissionForm, self).__init__(*args, **kwargs)

        self.fields['comment'].required = False
        self.fields['date'].required = False

        #if getattr(self.instance,'type',None) ==None:
        #    try:
        #        initial = kwargs.get('initial',None)
        #        if initial != None:
        #            self.fields['type'].choices = kwargs['initial']['user'].initiator_set.values_list('request_type_id','request_type__name')
        #    except Exception as e:
        #        logging.error(e)

       

       

        if getattr(self.instance,'client',None) !=None:
            self.fields['client'].choices = [ (str(self.instance.client.id), str(self.instance.client )) ]
        else:
            self.fields['client'].choices = [("","----")]


        if getattr(self.instance,'individual',None) !=None:
            self.fields['individual'].choices = [ (str(self.instance.individual.id), str(self.instance.individual )) ]
        else:
            self.fields['individual'].choices = [("","----")]

       
AdditionalFileInlineFormset = generic_inlineformset_factory(models.Additional_file, 
                                                   extra=3,max_num=5,fields='__all__', can_delete= True)