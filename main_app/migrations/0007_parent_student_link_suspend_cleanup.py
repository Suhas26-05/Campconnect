# Generated manually for CampConnect cleanup.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0006_remove_customuser_roll_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='fcm_token',
        ),
        migrations.AddField(
            model_name='student',
            name='is_suspended',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='student',
            name='roll_number',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='parent',
            name='student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='parents', to='main_app.student'),
        ),
        migrations.DeleteModel(
            name='FeedbackParent',
        ),
    ]
