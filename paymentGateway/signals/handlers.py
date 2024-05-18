from django.db.models.signals import post_save
from django.dispatch import receiver
from paymentGateway.models import WalletTransfer, Notification, Saving, SavingTransaction, SavingWallet


@receiver(post_save, sender=WalletTransfer)
def create_notification_on_transaction(sender, instance, created, **kwargs):
    if created:
        sender_user = instance.sender
        receiver_user = instance.receiver
        amount = instance.amount
        message = f"You have received ₦{amount} from {sender_user.username}."

        Notification.objects.create(user=receiver_user, message=message)



@receiver(post_save, sender=Saving)
def create_notification_on_saving(sender, instance, created, **kwargs):
    if created:
        amount = instance.amount
        user = instance.user
        saving_type = instance.saving_type
        payment_method = instance.payment_method
        collection_date = instance.collection_date
        if payment_method == 'wallet':
            if user.balance >= amount:
                old_balance = user.balance
                user.balance -= amount
                user.save()
                new_balance = user.balance
                message = f"You have suceefully saved ₦{amount} from your main wallet."

                Notification.objects.create(user=user, message=message)
                SavingTransaction.objects.create(user=user, old_balance=old_balance, new_balance=new_balance)
                SavingWallet.objects.create(user=user, amount=amount, saving_type=saving_type, collection_date=collection_date)
            else:
                message = f"You don have insufficient balance to save ₦{amount} from your wallet balance."
                Notification.objects.create(user=user, message=message)
        elif payment_method == 'card':
            message = f"Reminder!, Please saved ₦{amount} using your debit card." 
            Notification.objects.create(user=user, message=message)
        elif payment_method == 'transfer':
            message = f"Reminder!, Please saved ₦{amount} using your automated bank account."
            Notification.objects.create(user=user, message=message)
            
