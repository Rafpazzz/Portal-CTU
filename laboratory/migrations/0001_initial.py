from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='ObjetoLaboratorio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(db_index=True, max_length=120)),
                ('condicao', models.CharField(choices=[('bom', 'Bom'), ('ruim', 'Ruim'), ('novo', 'Novo'), ('quebrado', 'Quebrado')], max_length=20)),
                ('quantidade', models.PositiveIntegerField(default=0)),
                ('descricao', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Objeto de laboratorio',
                'verbose_name_plural': 'Objetos de laboratorio',
                'db_table': 'objetos_laboratorio',
                'ordering': ['-id'],
                'indexes': [
                    models.Index(fields=['-id'], name='obj_lab_id_desc_idx'),
                    models.Index(fields=['nome'], name='obj_lab_nome_idx'),
                ],
            },
        ),
    ]
