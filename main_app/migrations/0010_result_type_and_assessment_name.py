from django.db import migrations, models


def backfill_result_identity(apps, schema_editor):
    StudentResult = apps.get_model('main_app', 'StudentResult')
    for index, result in enumerate(StudentResult.objects.all(), start=1):
        updates = []
        if not result.result_type:
            result.result_type = 'unit'
            updates.append('result_type')
        if not result.assessment_name:
            result.assessment_name = f'Legacy Result {index}'
            updates.append('assessment_name')
        if updates:
            result.save(update_fields=updates)


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0009_session_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentresult',
            name='assessment_name',
            field=models.CharField(default='Assessment 1', max_length=120),
        ),
        migrations.AddField(
            model_name='studentresult',
            name='result_type',
            field=models.CharField(choices=[('unit', 'Unit Test'), ('mid', 'Mid Term'), ('semester', 'Semester Result')], default='unit', max_length=20),
        ),
        migrations.RunPython(backfill_result_identity, migrations.RunPython.noop),
        migrations.AlterUniqueTogether(
            name='studentresult',
            unique_together={('student', 'subject', 'result_type', 'assessment_name')},
        ),
    ]
