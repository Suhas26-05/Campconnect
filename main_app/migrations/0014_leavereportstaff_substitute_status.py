from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main_app", "0013_leavereportstaff_substitute_staff"),
    ]

    operations = [
        migrations.AddField(
            model_name="leavereportstaff",
            name="substitute_status",
            field=models.SmallIntegerField(default=0),
        ),
    ]
