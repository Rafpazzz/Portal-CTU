from django import forms

from .models import ObjetoLaboratorio


class ObjetoLaboratorioForm(forms.ModelForm):
    class Meta:
        model = ObjetoLaboratorio
        fields = ('nome', 'condicao', 'quantidade', 'descricao')
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_nome(self):
        nome = self.cleaned_data['nome'].strip()
        if not nome:
            raise forms.ValidationError('Informe o nome do objeto.')
        return nome
