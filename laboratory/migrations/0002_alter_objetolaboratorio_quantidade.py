import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('laboratory', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='objetolaboratorio',
            name='quantidade',
            field=models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AddConstraint(
            model_name='objetolaboratorio',
            constraint=models.CheckConstraint(condition=models.Q(('quantidade__gt', 0)), name='obj_lab_quantidade_gt_zero'),
        ),
    ]
