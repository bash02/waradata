from celery import shared_task
from django.utils import timezone
from .models import Saving, Notification, SavingTransaction, SavingWallet



@shared_task
def send_saving_notifications():
    print("Starting send_saving_notifications task...")  # Debug message
    
    today = timezone.now()
    print("Today's date and time:", today)  # Debug message
    
    # Filter savings for today based on maturity and notification_time
    daily_savings = Saving.objects.filter(maturity='daily')
    print("Daily savings count:", daily_savings.count())  # Debug message
    
    weekly_savings = Saving.objects.filter(maturity='weekly')
    print("Weekly savings count:", weekly_savings.count())  # Debug message
    
    monthly_savings = Saving.objects.filter(maturity='monthly')
    print("Monthly savings count:", monthly_savings.count())  # Debug message



    for saving in daily_savings:
        if saving.payment_method == 'wallet':
            if saving.user.balance >= saving.amount:
                old_balance = saving.user.balance
                saving.user.balance -= saving.amount
                saving.user.save()
                new_balance = saving.user.balance
                message = f"You have suceefully saved ₦{saving.amount} from your main wallet."

                Notification.objects.create(user=saving.user, message=message)
                SavingTransaction.objects.create(user=saving.user, old_balance=old_balance, new_balance=new_balance)
                SavingWallet.objects.create(user=saving.user, amount=saving.amount, saving_type=saving.saving_type)
            else:
                message = f"You don have insufficient balance to save ₦{saving.amount} from your wallet balance."
                Notification.objects.create(user=saving.user, message=message)

        if saving.payment_method == 'card':
            message = f"Reminder!, Please saved ₦{saving.amount} using your debit card." 
            Notification.objects.create(user=saving.user, message=message)


        if saving.payment_method == 'transfer':
            message = f"Reminder!, Please saved ₦{saving.amount} using your automated bank account." 
            Notification.objects.create(user=saving.user, message=message)



    for saving in weekly_savings:
        if saving.payment_method == 'wallet':
            if saving.user.balance >= saving.amount:
                old_balance = saving.user.balance
                saving.user.balance -= saving.amount
                saving.user.save()
                new_balance = saving.user.balance
                message = f"You have suceefully saved ₦{saving.amount} from your main wallet."

                Notification.objects.create(user=saving.user, message=message)
                SavingTransaction.objects.create(user=saving.user, old_balance=old_balance, new_balance=new_balance)
                SavingWallet.objects.create(user=saving.user, amount=saving.amount, saving_type=saving.saving_type)
            else:
                message = f"You don have insufficient balance to save ₦{saving.amount} from your wallet balance."
                Notification.objects.create(user=saving.user, message=message)

        if saving.payment_method == 'card':
            message = f"Reminder!, Please saved ₦{saving.amount} using your debit card." 
            Notification.objects.create(user=saving.user, message=message)


        if saving.payment_method == 'transfer':
            message = f"Reminder!, Please saved ₦{saving.amount} using your automated bank account." 
            Notification.objects.create(user=saving.user, message=message)

    for saving in monthly_savings:
        if saving.payment_method == 'wallet':
            if saving.user.balance >= saving.amount:
                old_balance = saving.user.balance
                saving.user.balance -= saving.amount
                saving.user.save()
                new_balance = saving.user.balance
                message = f"You have suceefully saved ₦{saving.amount} from your main wallet."

                Notification.objects.create(user=saving.user, message=message)
                SavingTransaction.objects.create(user=saving.user, old_balance=old_balance, new_balance=new_balance)
                SavingWallet.objects.create(user=saving.user, amount=saving.amount, saving_type=saving.saving_type)
            else:
                message = f"You don have insufficient balance to save ₦{saving.amount} from your wallet balance."
                Notification.objects.create(user=saving.user, message=message)

        if saving.payment_method == 'card':
            message = f"Reminder!, Please saved ₦{saving.amount} using your debit card." 
            Notification.objects.create(user=saving.user, message=message)


        if saving.payment_method == 'transfer':
            message = f"Reminder!, Please saved ₦{saving.amount} using your automated bank account." 
            Notification.objects.create(user=saving.user, message=message)

