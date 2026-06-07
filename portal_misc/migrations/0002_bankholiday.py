from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal_misc', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankHoliday',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True)),
                ('description', models.CharField(max_length=200)),
                ('is_active', models.BooleanField(default=True)),
                ('added_by', models.CharField(max_length=50)),
                ('added_on', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'bank_holidays',
                'ordering': ['date'],
            },
        ),
    ]
