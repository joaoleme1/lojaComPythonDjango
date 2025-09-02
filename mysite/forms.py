# mysite/forms.py
from django import forms

class CheckoutForm(forms.Form):
    nome = forms.CharField(max_length=100, label="Nome completo")
    email = forms.EmailField(max_length=100, label="E-mail")
    telefone = forms.CharField(max_length=32, required=False, label="Telefone")
    endereco = forms.CharField(max_length=200, label="Endereço")
    observacoes = forms.CharField(widget=forms.Textarea, required=False, label="Observações")
