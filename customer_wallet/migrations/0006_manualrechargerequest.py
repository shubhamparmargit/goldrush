from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0001_initial'),
        ('customer_wallet', '0005_withdrawalrequest'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManualRechargeRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_id', models.CharField(max_length=32, unique=True)),
                ('amount', models.PositiveIntegerField()),
                ('utr_number', models.CharField(max_length=100)),
                ('payment_mode', models.CharField(
                    choices=[('UPI', 'UPI'), ('NEFT', 'NEFT'), ('IMPS', 'IMPS'), ('RTGS', 'RTGS')],
                    default='UPI', max_length=10
                )),
                ('screenshot', models.CharField(blank=True, max_length=300, null=True)),
                ('status', models.CharField(
                    choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')],
                    default='PENDING', max_length=20
                )),
                ('remark', models.TextField(blank=True, null=True)),
                ('request_date', models.DateTimeField(auto_now_add=True)),
                ('action_date', models.DateTimeField(blank=True, null=True)),
                ('action_by', models.CharField(blank=True, max_length=50, null=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer.customer')),
                ('membership', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='customer_wallet.membershipmaster')),
            ],
            options={
                'db_table': 'manual_recharge_request',
                'ordering': ['-request_date'],
            },
        ),
    ]
