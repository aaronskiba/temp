# Generated by Django 4.1.2 on 2022-10-23 06:50

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import utils.model_utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authors', '0002_follower_isaccepted_alter_author_host_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('type', models.CharField(default='post', editable=False, max_length=255)),
                ('id', models.CharField(default=utils.model_utils.generate_random_string, editable=False, max_length=255, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('source', models.URLField()),
                ('origin', models.URLField()),
                ('description', models.CharField(max_length=255)),
                ('contentType', models.CharField(choices=[('text/markdown', 'Text Markdown'), ('text/plain', 'Text Plain'), ('application/base64', 'Application'), ('image/png;base64', 'Png'), ('image/jpeg;base64', 'Jpeg')], max_length=255)),
                ('content', models.TextField(null=True)),
                ('count', models.IntegerField(default=0)),
                ('published', models.DateTimeField(default=django.utils.timezone.now)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authors.author')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=255)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='posts.post')),
            ],
            options={
                'unique_together': {('post', 'category')},
            },
        ),
    ]
