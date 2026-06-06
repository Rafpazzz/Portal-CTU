from django.db import models


class ObjetoLaboratorio(models.Model):
    class Condicao(models.TextChoices):
        BOM = 'bom', 'Bom'
        RUIM = 'ruim', 'Ruim'
        NOVO = 'novo', 'Novo'
        QUEBRADO = 'quebrado', 'Quebrado'

    nome = models.CharField(max_length=120, db_index=True)
    condicao = models.CharField(max_length=20, choices=Condicao.choices)
    quantidade = models.PositiveIntegerField(default=0)
    descricao = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'objetos_laboratorio'
        ordering = ['-id']
        indexes = [
            models.Index(fields=['-id'], name='obj_lab_id_desc_idx'),
            models.Index(fields=['nome'], name='obj_lab_nome_idx'),
        ]
        verbose_name = 'Objeto de laboratorio'
        verbose_name_plural = 'Objetos de laboratorio'

    def __str__(self):
        return self.nome
