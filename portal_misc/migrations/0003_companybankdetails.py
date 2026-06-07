from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal_misc', '0002_bankholiday'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyBankDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_name', models.CharField(max_length=100)),
                ('bank_name', models.CharField(max_length=100)),
                ('account_number', models.CharField(max_length=30)),
                ('ifsc_code', models.CharField(max_length=15)),
                ('branch_name', models.CharField(blank=True, max_length=100)),
                ('upi_id', models.CharField(blank=True, max_length=100)),
                ('qr_code_image', models.CharField(blank=True, max_length=300)),
                ('is_active', models.BooleanField(default=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'company_bank_details',
            },
        ),
    ]
