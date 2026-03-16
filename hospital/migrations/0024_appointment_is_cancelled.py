from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0023_auto_20260302_1335'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='is_cancelled',
            field=models.BooleanField(default=False),
        ),
    ]
