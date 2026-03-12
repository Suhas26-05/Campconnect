from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0012_notification_hide_from_dashboard'),
    ]

    operations = [
        migrations.AddField(
            model_name='leavereportstaff',
            name='substitute_staff',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='substitute_leave_assignments',
                to='main_app.staff',
            ),
        ),
    ]
