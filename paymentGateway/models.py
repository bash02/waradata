from django.db import models
from django.conf import settings


class BankAccount(models.Model):
    bank_code = models.CharField(max_length=20)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    account_name = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True) 



class Contacts(models.Model):
    contract_code = models.CharField(max_length=100)
    account_reference = models.CharField(max_length=100)
    account_name = models.CharField(max_length=100)
    currency_code = models.CharField(max_length=10)
    customer_email = models.EmailField()
    customer_name = models.CharField(max_length=100)
    accounts = models.ManyToManyField(BankAccount)
    collection_channel = models.CharField(max_length=100)
    reservation_reference = models.CharField(max_length=100)
    reserved_account_type = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_on = models.DateTimeField()
    income_split_config = models.JSONField()
    bvn = models.CharField(max_length=100)
    nin = models.CharField(max_length=100)
    restrict_payment_source = models.BooleanField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)


class Transaction(models.Model):
    DEBIT = 'debit'
    CREDIT = 'credit'
    
    email = models.EmailField()

    TYPE_CHOICES = [
        (DEBIT, 'Debit Alert'),
        (CREDIT, 'Credit Alert'),
    ]

    BANK_TRANSFER = 'bank_transfer'
    CARD_TRANSFER = 'card_transfer'
    WALLET_TRANSFER = 'wallet_transfer'
 

    METHOD_CHOICES = [
        (BANK_TRANSFER, 'Bank transfer'),
        (CARD_TRANSFER, 'Card transfer'),
        (WALLET_TRANSFER, 'Wallet transfer'),
    ]
    payment_method = models.CharField(max_length=255, choices=METHOD_CHOICES, null=True)
    amount_paid = models.FloatField(blank=True, null=True)
    settlement_amount = models.FloatField(blank=True, null=True)
    charge = models.FloatField(null=True)
    old_balance = models.FloatField(blank=True, null=True)
    new_balance = models.FloatField(blank=True, null=True)
    date = models.DateTimeField(auto_now=True, null=True)
    type = models.CharField(max_length=255, choices=TYPE_CHOICES, null=True)
    PENDING = 'P'
    COMPLETE = 'C'
    FAILED = 'F'
    CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETE, 'Complete'),
        (FAILED, 'Failed')
    ]

    status = models.CharField(
        max_length=1, choices=CHOICES, default=PENDING)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f'Transaction ID: {self.id} - Amount: {self.amount_paid} - User: {self.user.username}'


class Charge(models.Model):
    WALLET_DISRSEMENT = 'wallet_disbursement'
    PERMANENT_SAVING_DISBURSEMENT = 'permanent_saving_disbursement'
    TEMPORARY_SAVING_DISBURSEMENT = 'temporary_saving_disbursement'
    SAVING_PENALTY  = 'saving_penalty'

    CHARGE_TYPE_CHOICES = [
        (WALLET_DISRSEMENT, 'Disburment charge'),
        (PERMANENT_SAVING_DISBURSEMENT, 'Customer permanent saving disbursement earning'),
        (TEMPORARY_SAVING_DISBURSEMENT, 'Customer temporary saving disbursement earning'),
        (SAVING_PENALTY, 'saving penalty')
        # Add more choices as needed
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    percentage = models.FloatField()
    charge_type = models.CharField(max_length=255, choices=CHARGE_TYPE_CHOICES)

    def __str__(self):
        return self.name
    


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.message



class WalletTransfer(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_transactions', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)





class Disbursement(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    destination_account_name = models.CharField(max_length=255)
    destination_bank_name = models.CharField(max_length=255)
    destination_account_number = models.CharField(max_length=20)
    destination_bank_code = models.CharField(max_length=10)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.reference  # or any other field you prefer

class Refund(models.Model):
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_reference = models.CharField(max_length=255)
    refund_reference = models.CharField(max_length=255)
    customer_note = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    destination_account_name = models.CharField(max_length=255)
    destination_bank_name = models.CharField(max_length=255)
    destination_account_number = models.CharField(max_length=20)
    destination_bank_code = models.CharField(max_length=10)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    def __str__(self):
        return self.reference  # or any other field you prefer


class Saving(models.Model):
    PERMANENT = 'permanent'
    BREAKABLE_LOCK = 'breakable_lock'
    SAVING_TYPE_CHOICES = [
        (PERMANENT, 'Parmanent lock'),
        (BREAKABLE_LOCK, 'Breakable lock'),
        # Add more choices as needed
    ]
    saving_type = models.CharField(max_length=20, choices=SAVING_TYPE_CHOICES)
    amount = models.FloatField(default=0.0)

    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    ONCE = 'once'
    MATURITY = [
        (DAILY, 'daily'),
        (WEEKLY, 'weekly'),
        (MONTHLY, 'monthly'),
        (ONCE, 'once')
        # Add more choices as needed
    ]
    maturity = models.CharField(max_length=20, choices=MATURITY)
    CARD = 'card'
    TRANSFER = 'transfer'
    WALLET = 'wallet'
    PAYMENT_METHOD_TYPE_CHOICES = [
        (CARD, 'Card mathod'),
        (TRANSFER, 'Transfer method'),
        (WALLET, 'Wallet method'),
        # Add more choices as needed
    ]
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    collection_date = models.DateField(null=True)
    notification_time = models.TimeField(auto_now_add=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    

class SavingWallet(models.Model):
    amount = models.FloatField(blank=True, null=True)
    PERMANENT = 'permanent'
    BREAKABLE_LOCK = 'breakable_lock'
    SAVING_TYPE_CHOICES = [
        (PERMANENT, 'Parmanent lock'),
        (BREAKABLE_LOCK, 'Breakable lock'),
        # Add more choices as needed
    ]
    saving_type = models.CharField(max_length=20, choices=SAVING_TYPE_CHOICES)
    with_penalty = models.BooleanField(default=False)
    collection_date = models.DateField(null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)



class SavingTransaction(models.Model):
    DEBIT = 'debit'
    CREDIT = 'credit'
    

    TYPE_CHOICES = [
        (DEBIT, 'Debit Alert'),
        (CREDIT, 'Credit Alert'),
    ]
    old_balance = models.FloatField(blank=True, null=True)
    amount_paid = models.FloatField(blank=True, null=True)
    new_balance = models.FloatField(blank=True, null=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class DisbursefromSavingWalletTransaction(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    destination_account_name = models.CharField(max_length=255)
    destination_bank_name = models.CharField(max_length=255)
    destination_account_number = models.CharField(max_length=20)
    destination_bank_code = models.CharField(max_length=10)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    saving_transaction = models.ForeignKey(SavingTransaction, on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.reference  # or any other field you prefer

class RefundFromSavingWalletTransaction(models.Model):
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_reference = models.CharField(max_length=255)
    refund_reference = models.CharField(max_length=255)
    customer_note = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    destination_account_name = models.CharField(max_length=255)
    destination_bank_name = models.CharField(max_length=255)
    destination_account_number = models.CharField(max_length=20)
    destination_bank_code = models.CharField(max_length=10)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    saving_transaction = models.ForeignKey(SavingTransaction, on_delete=models.CASCADE)
    def __str__(self):
        return self.reference  # or any other field you prefer



class TransactionReferenceAndType(models.Model):
    transaction_reference = models.CharField(max_length=255)
    SAVING = 'saving'
    FUNDING = 'funding'
    TYPE_CHOICES = [
        (SAVING, 'Saving reference'),
        (FUNDING, 'Funding reference'),
        # Add more choices as needed
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
