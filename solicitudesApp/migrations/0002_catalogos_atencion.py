import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


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
        migrations.RemoveField(model_name='solicitud', name='delegacion_territorial'),
        migrations.RemoveField(model_name='solicitud', name='tipo_categoria'),
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
