from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0001_initial'),
        ('customer_wallet', '0006_manualrechargerequest'),
    ]

    operations = [
        migrations.CreateModel(
            name='WalletManualCredit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_id', models.CharField(max_length=32, unique=True)),
                ('amount', models.PositiveIntegerField()),
                ('remark', models.TextField()),
                ('utr_number', models.CharField(blank=True, max_length=100)),
                ('balance_before', models.DecimalField(decimal_places=2, max_digits=12)),
                ('balance_after', models.DecimalField(decimal_places=2, max_digits=12)),
                ('credited_by', models.CharField(max_length=50)),
                ('credited_on', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer.customer')),
            ],
            options={
                'db_table': 'wallet_manual_credit',
                'ordering': ['-credited_on'],
            },
        ),
    ]
