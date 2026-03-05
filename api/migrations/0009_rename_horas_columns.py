from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_actividad_api_activid_usuario_130e0e_idx_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql='ALTER TABLE api_actividad RENAME COLUMN "horasEst" TO horas_est;',
            reverse_sql='ALTER TABLE api_actividad RENAME COLUMN horas_est TO "horasEst";',
        ),
        migrations.RunSQL(
            sql='ALTER TABLE api_actividad RENAME COLUMN "horasComp" TO horas_comp;',
            reverse_sql='ALTER TABLE api_actividad RENAME COLUMN horas_comp TO "horasComp";',
        ),
    ]
