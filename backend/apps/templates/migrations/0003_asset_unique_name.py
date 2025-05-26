from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('templates', '0002_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='asset',
            unique_together={('template', 'name')},
        ),
    ]

