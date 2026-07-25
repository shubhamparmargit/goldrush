from django.test import TestCase
from customer_wallet.views import is_withdrawal_window_open
from portal_misc.models import CompanyBankDetails

class WithdrawalWindowTest(TestCase):
    def setUp(self):
        # Create default bank details
        self.bank, created = CompanyBankDetails.objects.get_or_create(
            id=1,
            defaults={
                'account_name': "Test Name",
                'bank_name': "Test Bank",
                'account_number': "1234567890",
                'ifsc_code': "ABCD0123456",
                'withdrawals_closed': False
            }
        )
        if not created:
            self.bank.withdrawals_closed = False
            self.bank.save()

    def test_withdrawals_not_closed(self):
        # By default, checking is_withdrawal_window_open should not fail due to withdrawals_closed.
        allowed, reason = is_withdrawal_window_open()
        if not allowed:
            self.assertNotEqual(reason, "Withdrawals are temporarily disabled by the administrator.")

    def test_withdrawals_closed(self):
        # Set withdrawals_closed to True
        self.bank.withdrawals_closed = True
        self.bank.save()
        
        allowed, reason = is_withdrawal_window_open()
        self.assertFalse(allowed)
        self.assertEqual(reason, "Withdrawals are temporarily disabled by the administrator.")
