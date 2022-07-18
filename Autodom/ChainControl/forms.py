from . import models
from django import forms
from django.forms import inlineformset_factory

class DateInput(forms.DateInput):
    input_type = 'date'

class RequestForm(forms.ModelForm):

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
    

    class Meta:
        model = models.Request
        exclude = ('is_closed',)
        widgets = {
            'user' : forms.Select(attrs={'disabled':'true'}),
            'type' : forms.Select(),
            'payment_type' : forms.Select(),
            'client' : forms.Select(),
            'contract' : forms.Select(),
            'bank_account' : forms.Select(),
            'sum' : forms.NumberInput(attrs={'class' : 'form-control',}),
            }
       
AdditionalFileInlineFormset = inlineformset_factory(models.Request,models.Additional_file, widgets= {
    "file" : forms.FileInput(attrs = {'class' : 'form-control form-control-sm'})
    },
                                                   extra=3,max_num=5,fields= ['file'], can_delete= False)