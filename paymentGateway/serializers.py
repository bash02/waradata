from .models import BankAccount, Transaction, Refund, Notification, WalletTransfer, Disbursement, Saving, SavingTransaction, DisbursefromSavingWalletTransaction, RefundFromSavingWalletTransaction
from rest_framework import serializers



class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ['id', 'user', 'bank_code', 'bank_name', 'account_number', 'account_name', 'user']



class CreateReserveAccountSerializer(serializers.Serializer):
    account_reference = serializers.CharField(max_length=20)
    account_name = serializers.CharField(max_length=100)
    currency_code = serializers.CharField(max_length=5)
    contract_code = serializers.CharField(max_length=20)
    customer_email = serializers.EmailField()
    customer_name = serializers.CharField(max_length=100)
    bvn = serializers.CharField(max_length=20)
    nin = serializers.CharField(max_length=20)
    get_all_available_banks = serializers.BooleanField()



class TransactionSerializer(serializers.ModelSerializer):
    user_id =  serializers.IntegerField(read_only=True)
    date =  serializers.DateTimeField(read_only=True)
    class Meta:
        model = Transaction
        fields = ['id', 'settlement_amount', 'amount_paid', 'charge', 'old_balance', 'new_balance', 'user_id', 'date']



class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'created_at', 'is_read']


class WalletTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransfer
        fields = ['id', 'sender', 'receiver', 'amount', 'timestamp']



class DisbursementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disbursement
        fields = ['amount', 'reference', 'status', 'destination_account_name', 'destination_bank_name',
                  'destination_account_number', 'destination_bank_code', 'user', 'transaction']
        


class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = ['refund_amount', 'transaction_reference', 'refund_reference', 'destination_account_name', 'destination_bank_name',
                  'destination_account_number', 'destination_bank_code', 'user', 'transaction']
        
class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = ['saving_type', 'amount', 'maturity', 'payment_method', 'collection_date']


class SavingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Saving
        fields = ['saving_type', 'amount', 'maturity', 'payment_method', 'collection_date']


class SavingTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingTransaction
        fields = ['old_balance', 'new_balance', 'amount_paid', 'type', 'user']





class DisburseFromSavingWalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisbursefromSavingWalletTransaction
        fields = ['amount', 'reference', 'status', 'destination_account_name', 'destination_bank_name',
                  'destination_account_number', 'destination_bank_code', 'user', 'saving_transaction']
        


class RefundFromSavingWalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundFromSavingWalletTransaction
        fields = ['refund_amount', 'transaction_reference', 'refund_reference', 'destination_account_name', 'destination_bank_name',
                  'destination_account_number', 'destination_bank_code', 'user', 'saving_transaction']