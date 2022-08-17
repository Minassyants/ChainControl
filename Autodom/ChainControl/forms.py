
from django import forms
from django.forms import inlineformset_factory
from . import models




class DateInput(forms.DateInput):
    input_type = 'date'
    input_formats = ['%d.%m.%y']




class RequestSearchForm(forms.ModelForm):



    date = forms.DateField(widget=DateInput(attrs={'class' : 'form-control',
                                                 }))
    id = forms.IntegerField(widget=forms.NumberInput(attrs={'class' : 'form-control',
                                                            }))
    status = forms.ChoiceField(choices= models.Request.StatusTypes.choices + [("","----")],required=False)

    class Meta:
        model = models.Request
        fields = ['id','client','user','sum','date','status']
        widgets = {
            'id' : forms.NumberInput(attrs={'class' : 'form-control',}),
            'user' : forms.Select(attrs={'class' : 'form-control',}),
            'client' : forms.Select(attrs={'class' : 'form-control',}),
            'sum' : forms.NumberInput(attrs={'class' : 'form-control',}),
            'date' : forms.DateInput(format='%Y-%m-%d'),
            'status' : forms.Select(attrs={'class' : 'form-control',})
            }

    def __init__(self, data=None,instance = None, **kwargs):
        super(RequestSearchForm, self).__init__(data=data,instance=instance,**kwargs)
        for i in self.fields:
            self.fields[i].required = False
        #self.fields['status'].choices.append(("" , "----" ))
        #self.fields['status'].initial = self.fields['status'].choices[0]
        


class ApprovalForm(forms.ModelForm):

    approval_comment = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control',
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
            'id' : forms.HiddenInput(),
            'user':forms.HiddenInput(),
            'role':forms.HiddenInput(),
            'request':forms.HiddenInput(),
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
    
    contract = forms.ChoiceField(choices= [("","----")])

    bank_account = forms.ChoiceField(choices= [("","----")])


    class Meta:
        model = models.Request
        fields = '__all__'
        widgets = {
            'user' : forms.Select(attrs={'disabled':'true'}),
            'type' : forms.Select(),
            'payment_type' : forms.Select(),
            'client' : forms.Select(),
            'contract' : forms.Select(),
            'bank_account' : forms.Select(),
            'sum' : forms.NumberInput(attrs={'class' : 'form-control',}),
            'date' : forms.DateInput(format='%Y-%m-%d'),
            'complete_before' : forms.DateInput(format='%Y-%m-%d'),
            'invoice_date' : forms.DateInput(format='%Y-%m-%d'),
            'AVR_date' : forms.DateInput(format='%Y-%m-%d'),
            }
       
AdditionalFileInlineFormset = inlineformset_factory(models.Request,models.Additional_file, widgets= {
    "file" : forms.FileInput(attrs = {'class' : 'form-control form-control-sm'})
    },
                                                   extra=3,max_num=5,fields='__all__', can_delete= True)