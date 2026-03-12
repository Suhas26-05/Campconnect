from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0011_alter_admin_id_alter_attendance_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationparent',
            name='hide_from_dashboard',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='notificationstaff',
            name='hide_from_dashboard',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='notificationstudent',
            name='hide_from_dashboard',
            field=models.BooleanField(default=False),
        ),
    ]
