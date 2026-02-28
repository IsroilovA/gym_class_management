# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0002_alter_gymclass_duration_minutes_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainer',
            name='photo',
            field=models.ImageField(
                blank=True,
                help_text='Trainer profile photo.',
                null=True,
                upload_to='trainers/',
            ),
        ),
    ]
