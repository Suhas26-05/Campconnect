from django.db import migrations, models


def populate_session_names(apps, schema_editor):
    Session = apps.get_model('main_app', 'Session')
    for session in Session.objects.all():
        if session.name:
            continue
        session.name = f"Session {session.id}"
        session.save(update_fields=['name'])


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0008_superuser_safe_defaults'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='name',
            field=models.CharField(blank=True, default='', max_length=80),
        ),
        migrations.RunPython(populate_session_names, migrations.RunPython.noop),
    ]
