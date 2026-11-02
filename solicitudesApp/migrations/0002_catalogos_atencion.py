import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def migrar_catalogos_legacy(apps, schema_editor):
    """Copia los nombres existentes a los catálogos antes de quitar las columnas antiguas."""
    alias = schema_editor.connection.alias
    Solicitud = apps.get_model('solicitudesApp', 'Solicitud')
    Delegacion = apps.get_model('solicitudesApp', 'Delegacion')
    Categoria = apps.get_model('solicitudesApp', 'Categoria')

    for solicitud in Solicitud.objects.using(alias).all().iterator():
        nombre_delegacion = (solicitud.delegacion_territorial or '').strip()
        nombre_categoria = (solicitud.tipo_categoria or '').strip()

        if nombre_delegacion:
            delegacion, _ = Delegacion.objects.using(alias).get_or_create(
                nombre=nombre_delegacion,
                defaults={'descripcion': f'Delegación {nombre_delegacion}'},
            )
            solicitud.delegacion_id = delegacion.pk

        if nombre_categoria:
            categoria, _ = Categoria.objects.using(alias).get_or_create(
                nombre=nombre_categoria,
                defaults={'descripcion': f'Solicitudes de {nombre_categoria.lower()}'},
            )
            solicitud.categoria_id = categoria.pk

        solicitud.save(using=alias, update_fields=['delegacion', 'categoria'])


def restaurar_catalogos_legacy(apps, schema_editor):
    """Restaura los nombres antiguos si se revierte esta migración."""
    alias = schema_editor.connection.alias
    Solicitud = apps.get_model('solicitudesApp', 'Solicitud')

    for solicitud in Solicitud.objects.using(alias).all().iterator():
        solicitud.delegacion_territorial = (
            solicitud.delegacion.nombre if solicitud.delegacion_id else '')
        solicitud.tipo_categoria = (
            solicitud.categoria.nombre if solicitud.categoria_id else '')
        solicitud.save(
            using=alias,
            update_fields=['delegacion_territorial', 'tipo_categoria'],
        )


class Migration(migrations.Migration):

    dependencies = [
        ('solicitudesApp', '0001_initial'),
        ('usuariosApp', '0002_usuario_user_alter_usuario_options'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Delegacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=150, unique=True)),
                ('descripcion', models.CharField(blank=True, max_length=255)),
                ('activa', models.BooleanField(default=True)),
            ],
            options={'ordering': ['nombre']},
        ),
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('descripcion', models.CharField(blank=True, max_length=255)),
                ('activa', models.BooleanField(default=True)),
            ],
            options={'ordering': ['nombre']},
        ),
        migrations.AlterModelOptions(
            name='solicitud',
            options={'ordering': ['-fecha_registro', '-id']},
        ),
        migrations.AddField(
            model_name='solicitud',
            name='delegacion',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='solicitudes', to='solicitudesApp.delegacion'),
        ),
        migrations.AddField(
            model_name='solicitud',
            name='categoria',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='solicitudes', to='solicitudesApp.categoria'),
        ),
        migrations.AlterField(
            model_name='solicitud',
            name='delegacion_territorial',
            field=models.CharField(max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='solicitud',
            name='tipo_categoria',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.RunPython(migrar_catalogos_legacy, restaurar_catalogos_legacy),
        migrations.RemoveField(model_name='solicitud', name='delegacion_territorial'),
        migrations.RemoveField(model_name='solicitud', name='tipo_categoria'),
        migrations.AlterField(
            model_name='solicitud',
            name='funcionario_responsable',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='solicitudes', to='usuariosApp.usuario'),
        ),
        migrations.CreateModel(
            name='AtencionSolicitud',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_hora', models.DateTimeField(auto_now_add=True)),
                ('observacion', models.TextField()),
                ('estado_anterior', models.CharField(max_length=50)),
                ('estado_resultante', models.CharField(max_length=50)),
                ('avance_anterior', models.PositiveIntegerField()),
                ('avance_resultante', models.PositiveIntegerField()),
                ('funcionario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='atenciones', to='usuariosApp.usuario')),
                ('registrado_por', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='atenciones_registradas', to=settings.AUTH_USER_MODEL)),
                ('solicitud', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='atenciones', to='solicitudesApp.solicitud')),
            ],
            options={'ordering': ['-fecha_hora', '-id']},
        ),
    ]
