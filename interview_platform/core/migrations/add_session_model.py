# Generated manually
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', 'YOUR_LAST_MIGRATION'),  # Replace with your last migration
    ]

    operations = [
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('code', models.CharField(max_length=10, unique=True)),
                ('active', models.BooleanField(default=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_new_sessions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ] 