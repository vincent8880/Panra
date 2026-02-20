# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('markets', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='market',
            name='resolution_criteria',
            field=models.TextField(
                blank=True,
                help_text="When does this market resolve to YES? e.g. 'Resolves to YES when Kenya wins AFCON 2024.'"
            ),
        ),
    ]
