from django.contrib import admin

from .models import ObjetoLaboratorio


@admin.register(ObjetoLaboratorio)
class ObjetoLaboratorioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'condicao', 'quantidade')
    list_filter = ('condicao',)
    search_fields = ('nome', 'descricao')
    ordering = ('-id',)
