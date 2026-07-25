from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import status
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, time, timedelta

from utility.views import Utility
from authentication.models import Login
from users.models import Franchise
from customer.models import Customer
from customer_wallet.models import CustomerWallet, WalletRechargeHistory, WithdrawalRequest, ManualRechargeRequest, WalletManualCredit, WalletManualDebit
from customer_transaction.models import CustomerTransaction

util_obj = Utility()

def get_all_downline_referral_ids(franchise):
    referral_ids = [franchise.referral_id]
    # Level 1 children (MRAs or RAs)
    level1_franchises = Franchise.objects.filter(parent=franchise)
    level1_ids = []
    for f in level1_franchises:
        referral_ids.append(f.referral_id)
        level1_ids.append(f.id)
        
    # Level 2 grandchildren (RAs if level 1 was MRA)
    if level1_ids:
        level2_franchises = Franchise.objects.filter(parent_id__in=level1_ids)
        for f in level2_franchises:
            referral_ids.append(f.referral_id)
            
    return referral_ids

class Pages:
    def dashboard(self,request):
        if util_obj.checkSession(request) == False:
            return render(request,'portal/admin-dashboard.html')
        else:
            return util_obj.goToLogin(request)

    def get_dashboard_metrics(self, request):
        if util_obj.checkSession(request):
            return JsonResponse({'success': 0, 'message': 'Session expired'}, status=status.HTTP_401_UNAUTHORIZED)
            
        role = request.session.get('role')
        login_id = request.session.get('login_id')
        
        try:
            login = Login.objects.get(id=login_id)
        except Login.DoesNotExist:
            return JsonResponse({'success': 0, 'message': 'User not found'}, status=status.HTTP_401_UNAUTHORIZED)
            
        is_franchise = role in [2, 3, 4]
        ref_ids = []
        franchise_name = ""
        role_name = login.role.role_name if login.role else "Administrator"
        
        # 1. Compile filterable franchises list depending on current user role
        filterable_franchises = []
        own_franchise = None
        
        if role in [1, 5]:  # Admin / Super Admin
            filterable_franchises = Franchise.objects.filter(status='Approved').order_by('franchise_name')
        elif role == 2:  # SMRA
            try:
                own_franchise = Franchise.objects.get(unique_id=login.table_id)
                level1 = Franchise.objects.filter(parent=own_franchise, status='Approved')
                level2 = Franchise.objects.filter(parent__in=level1, status='Approved')
                filterable_franchises = list(level1) + list(level2)
                
                # Default scope is own hierarchy
                ref_ids = get_all_downline_referral_ids(own_franchise)
                franchise_name = own_franchise.franchise_name
            except Franchise.DoesNotExist:
                pass
        elif role == 3:  # MRA
            try:
                own_franchise = Franchise.objects.get(unique_id=login.table_id)
                filterable_franchises = Franchise.objects.filter(parent=own_franchise, status='Approved')
                
                # Default scope is own hierarchy
                ref_ids = get_all_downline_referral_ids(own_franchise)
                franchise_name = own_franchise.franchise_name
            except Franchise.DoesNotExist:
                pass
        elif role == 4:  # RA
            try:
                own_franchise = Franchise.objects.get(unique_id=login.table_id)
                ref_ids = get_all_downline_referral_ids(own_franchise)
                franchise_name = own_franchise.franchise_name
            except Franchise.DoesNotExist:
                pass

        # 2. Check for optional selected franchise uid filter
        selected_franchise_uid = request.GET.get('franchise_uid', '').strip()
        if selected_franchise_uid and selected_franchise_uid != 'all':
            if role in [1, 5]:
                try:
                    selected_franchise = Franchise.objects.get(unique_id=selected_franchise_uid, status='Approved')
                    is_franchise = True
                    ref_ids = get_all_downline_referral_ids(selected_franchise)
                    franchise_name = selected_franchise.franchise_name
                except Franchise.DoesNotExist:
                    pass
            elif role == 2 and own_franchise:
                try:
                    selected_franchise = Franchise.objects.get(unique_id=selected_franchise_uid, status='Approved')
                    is_descendant = (selected_franchise.parent == own_franchise) or (selected_franchise.parent and selected_franchise.parent.parent == own_franchise)
                    if is_descendant:
                        is_franchise = True
                        ref_ids = get_all_downline_referral_ids(selected_franchise)
                        franchise_name = selected_franchise.franchise_name
                except Franchise.DoesNotExist:
                    pass
            elif role == 3 and own_franchise:
                try:
                    selected_franchise = Franchise.objects.get(unique_id=selected_franchise_uid, status='Approved')
                    if selected_franchise.parent == own_franchise:
                        is_franchise = True
                        ref_ids = get_all_downline_referral_ids(selected_franchise)
                        franchise_name = selected_franchise.franchise_name
                except Franchise.DoesNotExist:
                    pass
            
        period = request.GET.get('period', 'today').lower()
        now = timezone.localtime(timezone.now())
        
        if period == 'today':
            start_date = timezone.make_aware(datetime.combine(now.date(), time.min))
            end_date = timezone.make_aware(datetime.combine(now.date(), time.max))
        elif period == 'yesterday':
            yesterday = now.date() - timedelta(days=1)
            start_date = timezone.make_aware(datetime.combine(yesterday, time.min))
            end_date = timezone.make_aware(datetime.combine(yesterday, time.max))
        elif period == 'weekly':
            start_date = timezone.make_aware(datetime.combine(now.date() - timedelta(days=6), time.min))
            end_date = timezone.make_aware(datetime.combine(now.date(), time.max))
        elif period == 'monthly':
            start_date = timezone.make_aware(datetime.combine(now.date() - timedelta(days=29), time.min))
            end_date = timezone.make_aware(datetime.combine(now.date(), time.max))
        elif period == 'custom':
            start_str = request.GET.get('start_date')
            end_str = request.GET.get('end_date')
            if not start_str or not end_str:
                return JsonResponse({'success': 0, 'message': 'Start and end dates are required for custom range'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                start_date = timezone.make_aware(datetime.combine(datetime.strptime(start_str, '%Y-%m-%d').date(), time.min))
                end_date = timezone.make_aware(datetime.combine(datetime.strptime(end_str, '%Y-%m-%d').date(), time.max))
            except ValueError:
                return JsonResponse({'success': 0, 'message': 'Invalid date format. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'success': 0, 'message': 'Invalid period specified'}, status=status.HTTP_400_BAD_REQUEST)
            
        # 1. Registrations
        reg_qs = Customer.objects.filter(date__range=(start_date, end_date))
        if is_franchise:
            reg_qs = reg_qs.filter(referral_code__in=ref_ids)
        registrations_count = reg_qs.count()
        
        # 2. Recharges
        online_qs = WalletRechargeHistory.objects.filter(status='Success', created_at__range=(start_date, end_date))
        manual_qs = ManualRechargeRequest.objects.filter(status='APPROVED', action_date__range=(start_date, end_date))
        credit_qs = WalletManualCredit.objects.filter(credited_on__range=(start_date, end_date))
        
        if is_franchise:
            online_qs = online_qs.filter(customer__referral_code__in=ref_ids)
            manual_qs = manual_qs.filter(customer__referral_code__in=ref_ids)
            credit_qs = credit_qs.filter(customer__referral_code__in=ref_ids)
            
        online_sum = online_qs.aggregate(total=Sum('amount'))['total'] or 0
        manual_sum = manual_qs.aggregate(total=Sum('amount'))['total'] or 0
        credit_sum = credit_qs.aggregate(total=Sum('amount'))['total'] or 0
        total_recharges = float(online_sum + manual_sum + credit_sum)
        
        # 3. Withdrawals
        withdraw_qs = WithdrawalRequest.objects.filter(status='APPROVED', action_date__range=(start_date, end_date))
        debit_qs = WalletManualDebit.objects.filter(debited_on__range=(start_date, end_date))
        
        if is_franchise:
            withdraw_qs = withdraw_qs.filter(customer__referral_code__in=ref_ids)
            debit_qs = debit_qs.filter(customer__referral_code__in=ref_ids)
            
        withdraw_sum = withdraw_qs.aggregate(total=Sum('request_amount'))['total'] or 0
        debit_sum = debit_qs.aggregate(total=Sum('amount'))['total'] or 0
        total_withdrawals = float(withdraw_sum + debit_sum)
        
        # 4. Profit
        profit_qs = CustomerTransaction.objects.filter(transaction_type='SELL', profit_loss='PROFIT', created_at__range=(start_date, end_date))
        if is_franchise:
            profit_qs = profit_qs.filter(customer__referral_code__in=ref_ids)
        total_profit = float(profit_qs.aggregate(total=Sum('profit_loss_amount'))['total'] or 0)
        
        # 5. Loss
        loss_qs = CustomerTransaction.objects.filter(transaction_type='SELL', profit_loss='LOSS', created_at__range=(start_date, end_date))
        if is_franchise:
            loss_qs = loss_qs.filter(customer__referral_code__in=ref_ids)
        total_loss = float(loss_qs.aggregate(total=Sum('profit_loss_amount'))['total'] or 0)
        
        # 6. Wallet Balance
        wallet_qs = CustomerWallet.objects.all()
        if is_franchise:
            wallet_qs = wallet_qs.filter(customer__referral_code__in=ref_ids)
        total_wallet_balance = float(wallet_qs.aggregate(total=Sum('balance'))['total'] or 0)
        
        # 6.5 Total Txn (Sum of Reward / 5 for BUY transactions)
        txn_qs = CustomerTransaction.objects.filter(transaction_type='BUY', created_at__range=(start_date, end_date))
        if is_franchise:
            txn_qs = txn_qs.filter(customer__referral_code__in=ref_ids)
        total_rewards = float(txn_qs.aggregate(total=Sum('reward'))['total'] or 0)
        total_txn = round(total_rewards / 5.0, 2)
        
        # 7. Chart Series
        chart_data = {
            'labels': [],
            'registrations': [],
            'recharges': [],
            'withdrawals': [],
            'profit': [],
            'loss': []
        }
        
        delta = end_date - start_date
        if delta.days <= 1:
            # Hourly trend
            hours = 24
            for h in range(hours):
                hour_start = start_date + timedelta(hours=h)
                hour_end = hour_start + timedelta(hours=1)
                label = hour_start.strftime('%I %p')
                
                r_qs = Customer.objects.filter(date__range=(hour_start, hour_end))
                if is_franchise: r_qs = r_qs.filter(referral_code__in=ref_ids)
                r_count = r_qs.count()
                
                on_qs = WalletRechargeHistory.objects.filter(status='Success', created_at__range=(hour_start, hour_end))
                man_qs = ManualRechargeRequest.objects.filter(status='APPROVED', action_date__range=(hour_start, hour_end))
                cr_qs = WalletManualCredit.objects.filter(credited_on__range=(hour_start, hour_end))
                if is_franchise:
                    on_qs = on_qs.filter(customer__referral_code__in=ref_ids)
                    man_qs = man_qs.filter(customer__referral_code__in=ref_ids)
                    cr_qs = cr_qs.filter(customer__referral_code__in=ref_ids)
                rec_sum = float((on_qs.aggregate(t=Sum('amount'))['t'] or 0) + (man_qs.aggregate(t=Sum('amount'))['t'] or 0) + (cr_qs.aggregate(t=Sum('amount'))['t'] or 0))
                
                w_qs = WithdrawalRequest.objects.filter(status='APPROVED', action_date__range=(hour_start, hour_end))
                db_qs = WalletManualDebit.objects.filter(debited_on__range=(hour_start, hour_end))
                if is_franchise:
                    w_qs = w_qs.filter(customer__referral_code__in=ref_ids)
                    db_qs = db_qs.filter(customer__referral_code__in=ref_ids)
                wdr_sum = float((w_qs.aggregate(t=Sum('request_amount'))['t'] or 0) + (db_qs.aggregate(t=Sum('amount'))['t'] or 0))

                p_qs = CustomerTransaction.objects.filter(transaction_type='SELL', profit_loss='PROFIT', created_at__range=(hour_start, hour_end))
                l_qs = CustomerTransaction.objects.filter(transaction_type='SELL', profit_loss='LOSS', created_at__range=(hour_start, hour_end))
                if is_franchise:
                    p_qs = p_qs.filter(customer__referral_code__in=ref_ids)
                    l_qs = l_qs.filter(customer__referral_code__in=ref_ids)
                p_sum = float(p_qs.aggregate(t=Sum('profit_loss_amount'))['t'] or 0)
                l_sum = float(l_qs.aggregate(t=Sum('profit_loss_amount'))['t'] or 0)
                
                chart_data['labels'].append(label)
                chart_data['registrations'].append(r_count)
                chart_data['recharges'].append(rec_sum)
                chart_data['withdrawals'].append(wdr_sum)
                chart_data['profit'].append(p_sum)
                chart_data['loss'].append(l_sum)
        else:
            # Daily trend
            days = delta.days + 1
            step_days = 1
            if days > 31:
                step_days = (days // 30) or 1
            
            for d in range(0, days, step_days):
                day_date = start_date.date() + timedelta(days=d)
                day_start = timezone.make_aware(datetime.combine(day_date, time.min))
                day_end = timezone.make_aware(datetime.combine(day_date, time.max))
                label = day_date.strftime('%d %b')
                
                r_qs = Customer.objects.filter(date__range=(day_start, day_end))
                if is_franchise: r_qs = r_qs.filter(referral_code__in=ref_ids)
                r_count = r_qs.count()
                
                on_qs = WalletRechargeHistory.objects.filter(status='Success', created_at__range=(day_start, day_end))
                man_qs = ManualRechargeRequest.objects.filter(status='APPROVED', action_date__range=(day_start, day_end))
                cr_qs = WalletManualCredit.objects.filter(credited_on__range=(day_start, day_end))
                if is_franchise:
                    on_qs = on_qs.filter(customer__referral_code__in=ref_ids)
                    man_qs = man_qs.filter(customer__referral_code__in=ref_ids)
                    cr_qs = cr_qs.filter(customer__referral_code__in=ref_ids)
                rec_sum = float((on_qs.aggregate(t=Sum('amount'))['t'] or 0) + (man_qs.aggregate(t=Sum('amount'))['t'] or 0) + (cr_qs.aggregate(t=Sum('amount'))['t'] or 0))
                
                w_qs = WithdrawalRequest.objects.filter(status='APPROVED', action_date__range=(day_start, day_end))
                db_qs = WalletManualDebit.objects.filter(debited_on__range=(day_start, day_end))
                if is_franchise:
                    w_qs = w_qs.filter(customer__referral_code__in=ref_ids)
                    db_qs = db_qs.filter(customer__referral_code__in=ref_ids)
                wdr_sum = float((w_qs.aggregate(t=Sum('request_amount'))['t'] or 0) + (db_qs.aggregate(t=Sum('amount'))['t'] or 0))

                p_qs = CustomerTransaction.objects.filter(transaction_type='SELL', profit_loss='PROFIT', created_at__range=(day_start, day_end))
                l_qs = CustomerTransaction.objects.filter(transaction_type='SELL', profit_loss='LOSS', created_at__range=(day_start, day_end))
                if is_franchise:
                    p_qs = p_qs.filter(customer__referral_code__in=ref_ids)
                    l_qs = l_qs.filter(customer__referral_code__in=ref_ids)
                p_sum = float(p_qs.aggregate(t=Sum('profit_loss_amount'))['t'] or 0)
                l_sum = float(l_qs.aggregate(t=Sum('profit_loss_amount'))['t'] or 0)
                
                chart_data['labels'].append(label)
                chart_data['registrations'].append(r_count)
                chart_data['recharges'].append(rec_sum)
                chart_data['withdrawals'].append(wdr_sum)
                chart_data['profit'].append(p_sum)
                chart_data['loss'].append(l_sum)
                
        # Compile franchises list for dropdown selection
        franchises_data = [
            {
                'unique_id': f.unique_id,
                'franchise_name': f.franchise_name,
                'referral_id': f.referral_id,
                'model': f.franchise_model
            }
            for f in filterable_franchises
        ]

        return JsonResponse({
            'success': 1,
            'is_franchise': is_franchise,
            'franchise_name': franchise_name,
            'role_name': role_name,
            'franchises': franchises_data,
            'metrics': {
                'registrations': registrations_count,
                'recharge': total_recharges,
                'withdrawals': total_withdrawals,
                'profit': total_profit,
                'loss': total_loss,
                'wallet_balance': total_wallet_balance,
                'total_txn': total_txn,
            },
            'chart_data': chart_data
        })