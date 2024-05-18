from django.core.cache import cache
from .models import BankAccount, Contacts, Transaction
from django.contrib.auth import get_user_model
from .models import Notification, Disbursement, Charge, Saving, SavingTransaction, TransactionReferenceAndType, SavingWallet, Refund, RefundFromSavingWalletTransaction, DisbursefromSavingWalletTransaction
from .serializers import BankAccountSerializer, CreateReserveAccountSerializer, DisburseFromSavingWalletTransactionSerializer, RefundFromSavingWalletTransactionSerializer, DisbursefromSavingWalletTransaction, TransactionSerializer, DisbursementSerializer, RefundSerializer, SavingTransactionSerializer, SavingSerializer, WalletTransferSerializer, NotificationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, serializers
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from rest_framework.decorators import permission_classes
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet
from waradata.settings.dev import ENV_ROOT
import base64, hashlib, hmac, requests, json
from django.utils import timezone
from datetime import datetime, timedelta


User = get_user_model()

your_secret_key = ""
monnify_ip = ""
api_key = ""
monnify_username = ""
monnify_password = ""
monnify_token = ""



with open(ENV_ROOT, 'r') as f:
    for line in f:
        if line.startswith('MONNIFY_SECRET='):
            your_secret_key = line.split('=')[1].strip()
        elif line.startswith('MONNIFY_IP='):
            monnify_ip = line.split('=')[1].strip()
        elif line.startswith('MONNIFY_TOKEN='):
            monnify_token = line.split('=')[1].strip()
        elif line.startswith('MONNIFY_API_KEY='):
            api_key = line.split('=')[1].strip()
        elif line.startswith('MONNIFY_PASSWORD='):
            monnify_password = line.split('=')[1].strip()
        elif line.startswith('MONNIFY_USERNAME='):
            monnify_username = line.split('=')[1].strip()


# Payment gateway
# Get new monnify token
def make_monnify_auth_request(monnify_username, monnify_password, api_key, your_secret_key):
    try:
   
        # Combine API key and secret key, then base64 encode the resulting string
        credentials = f"{api_key}:{your_secret_key}"
        base64_encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

        # Prepare the payload for the Monnify API request
        payload = {
            "username": monnify_username,
            "password": monnify_password
        }

        # Set up the headers with the base64-encoded credentials
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {base64_encoded_credentials}"
        }

        # Make the POST request to the Monnify API
        response = requests.post("https://sandbox.monnify.com/api/v1/auth/login", json=payload, headers=headers)
        response_data = response.json()

        # Check the response status and return the token
        if response.status_code == 200 and 'requestSuccessful' in response_data and response_data['requestSuccessful']:
            return response_data.get('responseBody', {}).get('accessToken')

        # Handle non-200 status codes or unsuccessful request
        else:
            raise Exception(f"Failed to authenticate with Monnify API. Status Code: {response.status_code}, Message: {response_data}")

    except Exception as e:
        # Handle any other exceptions and raise an error
        raise Exception(f"Error during Monnify API authentication: {str(e)}")


# Assign new token
def assign_new_token(monnify_token):
    existing_lines = []
    token_updated = False
    with open(ENV_ROOT, 'r') as f:
        for line in f:
            if line.startswith('MONNIFY_TOKEN='):
                existing_lines.append(f'MONNIFY_TOKEN={monnify_token}\n')
                token_updated = True
            else:
                existing_lines.append(line)


    # If MONNIFY_TOKEN was not found, add it to the end of the file
    if not token_updated:
        existing_lines.append(f'\nMONNIFY_TOKEN={monnify_token}\n')

    # Write the updated lines to the .env file
    with open(ENV_ROOT, 'w') as f:
        f.writelines(existing_lines)


# Create a reserve account
# Decorator to exempt CSRF token requirement for this view
class CreateReserveAccountView(ViewSet):
    permission_classes = [IsAuthenticated]

    @method_decorator(csrf_exempt)
    def create(self, request):
        try:
            user = self.request.user
            
            # Debugging: Print request data to inspect incoming data
            print("Request Data:", request.data)
            
            # Deserialize the JSON data using the serializer
            serializer = CreateReserveAccountSerializer(data=request.data)
            if serializer.is_valid():
                print("Serializer data:", serializer.validated_data)
            else:
                print("Serializer errors:", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve validated data from the serializer
            account_reference = serializer.validated_data.get('account_reference')
            account_name = serializer.validated_data.get('account_name')
            currency_code = serializer.validated_data.get('currency_code')
            contract_code = serializer.validated_data.get('contract_code')
            customer_email = serializer.validated_data.get('customer_email')
            customer_name = serializer.validated_data.get('customer_name')
            bvn = serializer.validated_data.get('bvn')
            nin = serializer.validated_data.get('nin')
            get_all_available_banks = serializer.validated_data.get('get_all_available_banks')

            # Check if the Monnify token is available and not expired
            
            your_secret_key = ""
            monnify_ip = ""
            api_key = ""
            monnify_username = ""
            monnify_password = ""
            monnify_token = ""
            
            with open(ENV_ROOT, 'r') as f:
                for line in f:
                    if line.startswith('MONNIFY_SECRET='):
                        your_secret_key = line.split('=')[1].strip()
                    elif line.startswith('MONNIFY_IP='):
                        monnify_ip = line.split('=')[1].strip()
                    elif line.startswith('MONNIFY_TOKEN='):
                        monnify_token = line.split('=')[1].strip()
                    elif line.startswith('MONNIFY_API_KEY='):
                        api_key = line.split('=')[1].strip()
                    elif line.startswith('MONNIFY_PASSWORD='):
                        monnify_password = line.split('=')[1].strip()
                    elif line.startswith('MONNIFY_USERNAME='):
                        monnify_username = line.split('=')[1].strip()
            
            # Sensitive Informations
            if not monnify_token:
                # If the token is not available or expired, refresh it
                monnify_token = make_monnify_auth_request(monnify_username, monnify_password, api_key, your_secret_key)
                assign_new_token(monnify_token)


            # Prepare the payload for the Monnify API request
            payload = {
                'accountReference': account_reference,
                'accountName': account_name,
                'currencyCode': currency_code,
                'contractCode': contract_code,
                'customerEmail': customer_email,
                'customerName': customer_name,
                'bvn': bvn,
                'nin': nin,
                'getAllAvailableBanks': get_all_available_banks
            }
            
                


            # Set up the headers with the Monnify token
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {monnify_token}"
            }

            # Make the POST request to the Monnify API
            response = requests.post("https://sandbox.monnify.com/api/v2/bank-transfer/reserved-accounts", headers=headers, json=payload)
            response_data = response.json()

            # Check if the response message contains "Access token expired"
            if 'error' in response_data and 'invalid_token' in response_data['error']:
                # Refresh the token
                monnify_token = make_monnify_auth_request(monnify_username, monnify_password, api_key, your_secret_key)
                assign_new_token(monnify_token)


                # Retry the API request with the new token
                headers['Authorization'] = f"Bearer {monnify_token}"
                response = requests.post("https://sandbox.monnify.com/api/v2/bank-transfer/reserved-accounts", headers=headers, json=payload)
                response_data = response.json()

            # Check the response status and return it
            if response.status_code == 200:
                if 'requestSuccessful' in response_data and response_data['requestSuccessful']:
                    success_response = {
                        'requestSuccessful': True,
                        'responseMessage': 'success',
                        'responseCode': '0',
                        'responseBody': response_data.get('responseBody', {})
                    }
                    response_body = response_data.get('responseBody', {})

                    # Extract data from the response
                    contract_data = {
                        'contract_code': response_body.get('contractCode'),
                        'account_reference': response_body.get('accountReference'),
                        'account_name': response_body.get('accountName'),
                        'currency_code': response_body.get('currencyCode'),
                        'customer_email': response_body.get('customerEmail'),
                        'customer_name': response_body.get('customerName'),
                        'collection_channel': response_body.get('collectionChannel'),
                        'reservation_reference': response_body.get('reservationReference'),
                        'reserved_account_type': response_body.get('reservedAccountType'),
                        'status': response_body.get('status'),
                        'created_on': response_body.get('createdOn'),
                        'income_split_config': response_body.get('incomeSplitConfig', []),
                        'bvn': response_body.get('bvn'),
                        'nin': response_body.get('nin'),
                        'restrict_payment_source': response_body.get('restrictPaymentSource', False),
                        'user': user
                    }

                    # Create Contract instance
                    contract_instance = Contacts.objects.create(**contract_data)

                    # Extract and create BankAccount instances
                    accounts_data = response_body.get('accounts', [])
                    for account_data in accounts_data:
                        account_instance = BankAccount.objects.create(
                            bank_code=account_data.get('bankCode'),
                            bank_name=account_data.get('bankName'),
                            account_number=account_data.get('accountNumber'),
                            account_name=account_data.get('accountName'), 
                            user=user
                        )
                        contract_instance.accounts.add(account_instance)
                    return Response(success_response, status=200)
                else:
                    response_data['requestSuccessful'] = False
                    response_data['responseMessage'] = response_data.get('responseMessage', 'Unknown error')
                    return Response(response_data, status=response.status_code)
            else:
                return Response(response_data, status=response.status_code)

        except serializers.ValidationError as e:
            error_data = {'status': 'error', 'message': str(e)}
            return Response(error_data, status=400)

        # except Exception as e:
        #     # Handle any other exceptions and return an error response
        #     error_data = {'status': 'error', 'message': str(e)}
        #     return Response(error_data, status=500) 



# Verify monnify webhook hash
def verify_hash(payload_in_bytes, monnify_hash):
    """
    Recieves the monnify payload in bytes and perform a SHA-512 hash
    with your secret key which is also encoded in byte.
    uses hmac.compare_digest rather than "=" sign as the former helps
    to prevent timing attacks.
    """
    secret_key_bytes = your_secret_key.encode(
        "utf-8"
    )  # encodes your secret key as byte
    your_hash_in_bytes = hmac.new(
        secret_key_bytes, msg=payload_in_bytes, digestmod=hashlib.sha512
    )
    your_hash_in_hex = your_hash_in_bytes.hexdigest()  # Hexlify generated hash
    return hmac.compare_digest(your_hash_in_hex, monnify_hash)

# Get sender api
def get_sender_ip(headers):
    """
    Get senders' IP address, by first checking if your API server
    is behind a proxy by checking for HTTP_X_FORWARDED_FOR
    if not gets sender actual IP address using REMOTE_ADDR
    """

    x_forwarded_for = headers.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # in some cases this might be in the second index ie [1]
        # depending on your hosting environment
        return x_forwarded_for.split(",")[0]
    else:
        return headers.get("REMOTE_ADDR")

# Verify the webhoook
def verify_monnify_webhook(payload_in_bytes, monnify_hash, headers):
    """
    The interface that does the verification by calling necessary functions.
    Though everything has been tested to work well, but if you have issues
    with this function returning False, you can remove the get_sender_ip
    function to be sure that the verify_hash is working, then you can check
    what header contains the IP address.
    """

    return get_sender_ip(headers) == monnify_ip and verify_hash(
        payload_in_bytes, monnify_hash
    )



# Handle transaction for receiving payment from customer's reserve account
def transaction_handle_transaction(request_data):
    transaction_reference = request_data['eventData']['transactionReference']
    # Retrieve the charge based on the assigned charge_type
    amount_paid = float(request_data['eventData']['amountPaid'])
    email = request_data['eventData']['customer']['email']
    try:
        user_object = settings.AUTH_USER_MODEL.objects.get(email=email)
    except settings.AUTH_USER_MODEL.DoesNotExist:
        return Response({"error": "No user"}, status=status.HTTP_404_NOT_FOUND)
    
    if TransactionReferenceAndType.objects.get(transaction_reference=transaction_reference, type="funding"):
        obj = SavingWallet.objects.get(user=user_object)
        old_balance = obj.amount
        obj.amount += amount_paid
        obj.save()
        new_balance = obj.amount 
        # Save the transaction details
        transaction_data = {
            'amount_paid': amount_paid,
            'old_balance': old_balance,
            'new_balance': new_balance,
            'type': 'credit', 
            'status': 'C'
        }
        serializer = SavingTransactionSerializer(data=transaction_data)

    else:
        old_balance = user_object.balance
        user_object.balance += amount_paid
        user_object.save()
        new_balance = user_object.balance
        

        # Save the transaction details
        transaction_data = {
            'amount_paid': amount_paid,
            'old_balance': old_balance,
            'new_balance': new_balance,
            'type': 'credit', 
            'status': 'C'
        }
        serializer = TransactionSerializer(data=transaction_data)
    if serializer.is_valid():
        serializer.save(user=user_object)
        return Response(serializer.data, status=200)
    else:
        return Response(serializer.errors, status=400)

# Webhook for payment from monnify customer's reserve account
class TrasanctionWebhookView(ViewSet):
    @method_decorator(csrf_exempt)
    def create(self, request):
        payload_in_bytes = request.body
        monnify_hash = request.META.get("HTTP_MONNIFY_SIGNATURE")
        confirmation = verify_monnify_webhook(payload_in_bytes, monnify_hash, request.META)
        if not confirmation:
            return Response({"status": "failed", "msg": "Webhook does not appear to come from Monnify"},
                            status=status.HTTP_400_BAD_REQUEST)

        data = json.loads(payload_in_bytes)
        your_secret_key = ""
        monnify_ip = ""
        api_key = ""
        monnify_username = ""
        monnify_password = ""
        monnify_token = ""
        
        with open(ENV_ROOT, 'r') as f:
            for line in f:
                if line.startswith('MONNIFY_SECRET='):
                    your_secret_key = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_IP='):
                    monnify_ip = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_TOKEN='):
                    monnify_token = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_API_KEY='):
                    api_key = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_PASSWORD='):
                    monnify_password = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_USERNAME='):
                    monnify_username = line.split('=')[1].strip()

        if not monnify_token:
            monnify_token = make_monnify_auth_request(monnify_username, monnify_password, api_key, your_secret_key)
            assign_new_token(monnify_token)

        # Parse the JSON string into a Python dictionary
        request_data = json.loads(payload_in_bytes)

        # Extracting transactionReference
        transaction_reference = request_data['eventData']['transactionReference']
        if not transaction_reference:
            return Response({"error": "Transaction reference not found in webhook data"},
                            status=status.HTTP_400_BAD_REQUEST)

        url = "https://sandbox.monnify.com/api/v2/merchant/transactions/query"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {monnify_token}"}
        params = {"transactionReference": transaction_reference}

        try:
            response = requests.get(url, params=params, headers=headers)
            response_data = response.json()
            if response.status_code == 200:
                if response_data.get('requestSuccessful', False):
                    return transaction_handle_transaction(request_data)
                else:
                    return Response(response_data, status=response.status_code)
            elif 'error' in response_data and 'invalid_token' in response_data['error']:
                monnify_token = make_monnify_auth_request(monnify_username, monnify_password, api_key, your_secret_key)
                assign_new_token(monnify_token)
                headers['Authorization'] = f"Bearer {monnify_token}"
                response = requests.get(url, params=params, headers=headers)
                response_data = response.json()
                if response.status_code == 200 and response_data.get('requestSuccessful', False):
                    return transaction_handle_transaction(request_data)
                else:
                    return Response(response_data, status=response.status_code)
            else:
                return Response(response_data, status=response.status_code)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            
         
            
            
# User's reservem account            
class ViewUserAccouts(ModelViewSet):
    http_method_names = ['get']
    serializer_class = BankAccountSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return BankAccount.objects.all()

        return BankAccount.objects.filter(user=user)
    
# list of transaction
class TransactionViewSet(ModelViewSet):
    http_method_names = ['get']
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
   

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Transaction.objects.all()

        return Transaction.objects.filter(user=user)
    



# Bank list from monnify
class BanksViewSet(ViewSet):
    def list(self, request):
        cached_response = cache.get('banks_response')
        if cached_response:
            return Response(cached_response, status=status.HTTP_200_OK)
        your_secret_key = ""
        monnify_ip = ""
        api_key = ""
        monnify_username = ""
        monnify_password = ""
        monnify_token = ""
        
        with open(ENV_ROOT, 'r') as f:
            for line in f:
                if line.startswith('MONNIFY_SECRET='):
                    your_secret_key = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_IP='):
                    monnify_ip = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_TOKEN='):
                    monnify_token = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_API_KEY='):
                    api_key = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_PASSWORD='):
                    monnify_password = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_USERNAME='):
                    monnify_username = line.split('=')[1].strip()
        headers = {
            'Authorization': f"Bearer {monnify_token}",
            'Content-Type': 'application/json'
        }
        response = requests.get("https://sandbox.monnify.com/api/v1/banks", headers=headers)   

        response_data = response.json()
        if 'error' in response_data and 'invalid_token' in response_data['error']:
                # Refresh the token
                monnify_token = make_monnify_auth_request(monnify_username, monnify_password, api_key, your_secret_key)
                assign_new_token(monnify_token)


        # Check the response status and return it
        if response.status_code == 200:
            if 'requestSuccessful' in response_data and response_data['requestSuccessful']:
                # Cache the response for future use
                cache.set('banks_response', response_data, timeout=3600)  # Cache for 1 hour
                return Response(response_data, status=status.HTTP_200_OK)
                    # Check if the response message contains "Access token expired"
        return Response(response_data, status=response.status_code)

# Validate Account number
# @permission_classes([IsAuthenticated])
class ValidateAccountNumberViewSet(ViewSet):
    def create(self, request):
        
        # Construct the URL with parameters
        monnify_token = ""
        with open(ENV_ROOT, 'r') as f:
            for line in f:
                
                if line.startswith('MONNIFY_TOKEN='):
                    monnify_token = line.split('=')[1].strip()
        headers = {
            'Authorization': f'Token {monnify_token}',  # Correct formatting for f-string
            'Content-Type': 'application/json'
        }

        account_number = request.data.get('account_number')
        bank_code = request.data.get('bank_code')
        
        # Format the URL string using payload variables
        url = f'https://sandbox.monnify.com/api/v1/disbursements/account/validate?accountNumber={account_number}&bankCode={bank_code}'

        print(url)
        response = requests.get(url, headers=headers)
        response_data = response.json()
        if 'error' in response_data and 'invalid_token' in response_data['error']:
                # Refresh the token
                monnify_token = make_monnify_auth_request(monnify_username, monnify_password, api_key, your_secret_key)
                assign_new_token(monnify_token)

        # Check the response status and return it
        if response.status_code == 200:
            if 'requestSuccessful' in response_data and response_data['requestSuccessful']:
                return Response(response_data, status=status.HTTP_200_OK)
        return Response(response_data, status=response.status_code)
    


# Wallet transfer to anither customer
@permission_classes([IsAuthenticated])
class WalletTransferViewSet(ViewSet):

    def create(self, request):
        receiver_identifier = request.data.get('receiver_identifier')  # Accept email or username
        amount = request.data.get('amount')
        sender_user = request.user

        
        try:
            receiver_user = User.objects.get(email=receiver_identifier)  # Search by email
        except User.DoesNotExist:
            try:
                receiver_user = User.objects.get(username=receiver_identifier)  # Search by username
            except User.DoesNotExist:
                return Response({'error': 'Receiver not found'}, status=status.HTTP_404_NOT_FOUND)



        sender_balance = sender_user.balance  # Assuming User has a OneToOneField to Wallet
        receiver_balance = receiver_user.balance # Assuming User has a OneToOneField to Wallet

        if sender_balance >= amount:
            sender_old_balance = sender_balance
            receiver_old_balance = receiver_balance 
            sender_user.balance -= amount
            receiver_user.balance += amount

            sender_user.save()
            receiver_user.save()
            sender_new_balance = sender_user.balance
            receiver_new_balance = receiver_user.balance

            Transaction.objects.create(amount_paid=amount, email=sender_user.email, old_balance=sender_old_balance, new_balance=sender_new_balance, user=sender_user, type='debit')
            receiver_transaction = Transaction.objects.create(amount_paid=amount, email=receiver_user.email, old_balance=receiver_old_balance, new_balance=receiver_new_balance, user=receiver_user, type='credit')


            transaction_data = {
                'sender': sender_user.id,
                'receiver': receiver_user.id,
                'amount': amount
            }
            serializer = WalletTransferSerializer(data=transaction_data, transaction=receiver_transaction)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)




class NotificationViewSet(ModelViewSet):
    http_method_names = ['get', 'patch']
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
   

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Notification.objects.all()

        return Notification.objects.filter(user=user)
    





# Disbursement handler
def disbursement_handle_transaction(response_data, user):
    # Retrieve the charge based on the assigned charge_type
    amount_paid = float(response_data['responseBody']['amount'])
    charge_type = 'transaction'
    percentage = Charge.objects.get(charge_type=charge_type).percentage
    charge = (amount_paid * percentage/100 + 1)

    old_balance = user.balance
    user.balance -= (amount_paid + charge)
    user.save()
    new_balance = user.balance
    settlement_amount = (amount_paid + charge)
    data = {
        "amount": response_data['responseBody']['amount'],
        "reference": response_data['responseBody']['refrence'],
        "destinationAccountName": response_data['responseBody']['destinationAccountName'],
        "destinationBankName": response_data['responseBody']['destinationBankName'],
        "destinationAccountNumber": response_data['responseBody']['destinationAccountNumber'],
        "destinationBankCode": response_data['responseBody']['destinationBankCode']
        }
    transaction = Transaction.objects.create(amount_paid=amount_paid, charge=charge, settlement_amount=settlement_amount, email=user.email, old_balance=old_balance, new_balance=new_balance, user=user, type='debit')
    serializer = DisbursementSerializer(data=data, transaction=transaction)
    if serializer.is_valid():
        serializer.save(user=user)
        return Response(serializer.data, status=200)
    else:
        return Response(serializer.errors, status=400)

# Disbursement viewset 
class DisbursementViewSet(ViewSet):
    @method_decorator(csrf_exempt)
    def create(self, request):
        # Get the values from the request body using request.data.get()
        amount = request.data.get('amount')
        reference = request.data.get('reference')
        narration = request.data.get('narration')
        destination_bank_code = request.data.get('destination_bank_code')
        destination_account_number = request.data.get('destination_account_number')
        currency = request.data.get('currency')
        source_account_number = request.data.get('source_account_number')
        user = request.user


        your_secret_key = ""
        monnify_ip = ""
        api_key = ""
        monnify_username = ""
        monnify_password = ""
        monnify_token = ""
        
        with open(ENV_ROOT, 'r') as f:
            for line in f:
                if line.startswith('MONNIFY_SECRET='):
                    your_secret_key = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_IP='):
                    monnify_ip = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_TOKEN='):
                    monnify_token = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_API_KEY='):
                    api_key = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_PASSWORD='):
                    monnify_password = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_USERNAME='):
                    monnify_username = line.split('=')[1].strip()

        request_data = {
            'amount': amount,
            'reference': reference,
            'narration': narration,
            'destinationBankCode': destination_bank_code,
            'destinationAccountNumber': destination_account_number,
            'currency': currency,
            'sourceAccountNumber': source_account_number
        }



        if not monnify_token:
            monnify_token = make_monnify_auth_request(monnify_username, monnify_password, api_key, your_secret_key)
            assign_new_token(monnify_token)


        url = "https://sandbox.monnify.com/api/v2/disbursements/single"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {monnify_token}"}

        try:
            response = requests.post(url, json=request_data, headers=headers)
            response_data = response.json()
            if response.status_code == 200:
                if response_data.get('requestSuccessful', False):
                    transaction_reference = response_data['responseBody']['refrence']
                    TransactionReferenceAndType.objects.create(
                        transaction_reference=transaction_reference,
                        type="funding"
                    )
                    return disbursement_handle_transaction(response_data, user)
                else:
                    return Response(response_data, status=response.status_code)
            elif 'error' in response_data and 'invalid_token' in response_data['error']:
                monnify_token = make_monnify_auth_request(monnify_username, monnify_password, api_key, your_secret_key)
                assign_new_token(monnify_token)
                headers['Authorization'] = f"Bearer {monnify_token}"
                response = requests.get(url, json=request_data, headers=headers)
                response_data = response.json()
                if response.status_code == 200 and response_data.get('requestSuccessful', False):
                    transaction_reference = response_data['responseBody']['refrence']
                    TransactionReferenceAndType.objects.create(
                        transaction_reference=transaction_reference,
                        type="funding"
                    )
                    return disbursement_handle_transaction(response_data, user)
                else:
                    return Response(response_data, status=response.status_code)
            else:
                return Response(response_data, status=response.status_code)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        




# Handle transaction for disbursement
def webhook_disbursement_handle_transaction(request_data, transaction_reference):
    # Retrieve the charge based on the assigned charge_type
    status = request_data['eventData']['status']
    if status == 'SUCCESS':
        disbursement = Disbursement.objects.get(transaction_reference=transaction_reference)
        transaction = Transaction.objects.get(disbursement=disbursement)
        transaction.status = 'C'
        transaction.save()
    elif status == 'FAILED':
        disbursement = Disbursement.objects.get(transaction_reference=transaction_reference)
        transaction = Transaction.objects.get(disbursement=disbursement)
        transaction.status = 'F'
        transaction.save()
        user = User.objects.get(transaction=transaction)
        amount_paid = float(request_data['eventData']['amount'])
        charge_type = 'transaction'
        percentage = Charge.objects.get(charge_type=charge_type).percentage
        charge = (amount_paid * percentage/100 + 1)
        user.balance += (amount_paid + charge)
        user.save()




# Webhook for disbursement
class WebhookDisbursementView(ViewSet):
    @method_decorator(csrf_exempt)
    def create(self, request):
        payload_in_bytes = request.body
        monnify_hash = request.META.get("HTTP_MONNIFY_SIGNATURE")
        confirmation = verify_monnify_webhook(payload_in_bytes, monnify_hash, request.META)
        if not confirmation:
            return Response({"status": "failed", "msg": "Webhook does not appear to come from Monnify"},
                            status=status.HTTP_400_BAD_REQUEST)

        data = json.loads(payload_in_bytes)
        your_secret_key = ""
        monnify_ip = ""
        api_key = ""
        monnify_username = ""
        monnify_password = ""
        monnify_token = ""
        
        with open(ENV_ROOT, 'r') as f:
            for line in f:
                if line.startswith('MONNIFY_SECRET='):
                    your_secret_key = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_IP='):
                    monnify_ip = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_TOKEN='):
                    monnify_token = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_API_KEY='):
                    api_key = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_PASSWORD='):
                    monnify_password = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_USERNAME='):
                    monnify_username = line.split('=')[1].strip()

        if not monnify_token:
            monnify_token = make_monnify_auth_request(monnify_username, monnify_password, api_key, your_secret_key)
            assign_new_token(monnify_token)

        # Parse the JSON string into a Python dictionary
        request_data = json.loads(payload_in_bytes)

        # Extracting transactionReference
        transaction_reference = request_data['eventData']['transactionReference']
        if not transaction_reference:
            return Response({"error": "Transaction reference not found in webhook data"},
                            status=status.HTTP_400_BAD_REQUEST)

        url = "https://sandbox.monnify.com/api/v2/disbursements/single"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {monnify_token}"}
        params = {"transactionReference": transaction_reference}

        try:
            response = requests.get(url, params=params, headers=headers)
            response_data = response.json()
            if response.status_code == 200:
                if response_data.get('requestSuccessful', False):
                    return webhook_disbursement_handle_transaction(request_data, transaction_reference)
                else:
                    return Response(response_data, status=response.status_code)
            elif 'error' in response_data and 'invalid_token' in response_data['error']:
                monnify_token = make_monnify_auth_request(monnify_username, monnify_password, api_key, your_secret_key)
                assign_new_token(monnify_token)
                headers['Authorization'] = f"Bearer {monnify_token}"
                response = requests.get(url, params=params, headers=headers)
                response_data = response.json()
                if response.status_code == 200 and response_data.get('requestSuccessful', False):
                    return webhook_disbursement_handle_transaction(request_data, transaction_reference)
                else:
                    return Response(response_data, status=response.status_code)
            else:
                return Response(response_data, status=response.status_code)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)










# Refund handler
def refund_handle_transaction(response_data, user):
    # Retrieve the charge based on the assigned charge_type
    amount_paid = float(response_data['responseBody']['refundAmount'])

    old_balance = user.balance
    user.balance -= amount_paid
    user.save()
    new_balance = user.balance
    data = {
        "refund_amount": response_data['responseBody']['refundAmount'],
        "transaction_reference": response_data['responseBody']['transactionRefrence'],
        "refund_reference": response_data['responseBody']['refundRefrence'],
        "destination_account_name": response_data['responseBody']['destinationAccountName'],
        "destination_bank_name": response_data['responseBody']['destinationBankName'],
        "destination_account_number": response_data['responseBody']['destinationAccountNumber'],
        "destination_bank_code": response_data['responseBody']['destinationBankCode']
        }
    transaction = Transaction.objects.create(amount_paid=amount_paid, email=user.email, old_balance=old_balance, new_balance=new_balance, user=user, type='debit')
    serializer = RefundSerializer(data=data, transaction=transaction)
    if serializer.is_valid():
        serializer.save(user=user)
        return Response(serializer.data, status=200)
    else:
        return Response(serializer.errors, status=400)

# refund viewset 
class RefundViewSet(ViewSet):
    @method_decorator(csrf_exempt)
    def create(self, request):
        # Get the values from the request body using request.data.get()
        transaction_reference = request.data.get('transaction_reference')
        refund_reference = request.data.get('refund_reference')
        refund_amount = request.data.get('refund_amount')
        refund_reason = request.data.get('refund_reason')
        customer_note = request.data.get('customer_note')
        destination_bank_code = request.data.get('destination_bankcode')
        destination_account_number = request.data.get('destination_account_number')
        user = request.user


        your_secret_key = ""
        monnify_ip = ""
        api_key = ""
        monnify_username = ""
        monnify_password = ""
        monnify_token = ""
        
        with open(ENV_ROOT, 'r') as f:
            for line in f:
                if line.startswith('MONNIFY_SECRET='):
                    your_secret_key = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_IP='):
                    monnify_ip = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_TOKEN='):
                    monnify_token = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_API_KEY='):
                    api_key = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_PASSWORD='):
                    monnify_password = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_USERNAME='):
                    monnify_username = line.split('=')[1].strip()

        request_data = {
            'transactionReference': transaction_reference,
            'refundReference': refund_reference,
            'refundAmount': refund_amount,
            'refundReason': refund_reason,
            'customerNote': customer_note,
            'destinationBankCode': destination_bank_code,
            'destinationAccountNumber': destination_account_number,
        }



        if not monnify_token:
            monnify_token = make_monnify_auth_request(monnify_username, monnify_password, api_key, your_secret_key)
            assign_new_token(monnify_token)


        url = "https://sandbox.monnify.com/api/v1/refunds/initiate-refund"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {monnify_token}"}

        try:
            response = requests.post(url, json=request_data, headers=headers)
            response_data = response.json()
            if response.status_code == 200:
                if response_data.get('requestSuccessful', False):
                    return refund_handle_transaction(response_data, user)
                else:
                    return Response(response_data, status=response.status_code)
            elif 'error' in response_data and 'invalid_token' in response_data['error']:
                monnify_token = make_monnify_auth_request(monnify_username, monnify_password, api_key, your_secret_key)
                assign_new_token(monnify_token)
                headers['Authorization'] = f"Bearer {monnify_token}"
                response = requests.get(url, json=request_data, headers=headers)
                response_data = response.json()
                if response.status_code == 200 and response_data.get('requestSuccessful', False):
                    return refund_handle_transaction(response_data, user)
                else:
                    return Response(response_data, status=response.status_code)
            else:
                return Response(response_data, status=response.status_code)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        







# Handle transaction for refund
def webhook_refund_handle_transaction(request_data, transaction_reference):
    # Retrieve the charge based on the assigned charge_type
    status = request_data['eventData']['status']
    if status == 'COMPLETED':
        disbursement = Refund.objects.get(transaction_reference=transaction_reference)
        transaction = Transaction.objects.get(disbursement=disbursement)
        transaction.status = 'C'
        transaction.save()
    elif status == 'refundStatus':
        disbursement = Refund.objects.get(transaction_reference=transaction_reference)
        transaction = Transaction.objects.get(disbursement=disbursement)
        transaction.status = 'F'
        transaction.save()
        user = User.objects.get(transaction=transaction)
        amount_paid = float(request_data['eventData']['refundAmount'])
        user.balance += amount_paid
        user.save()




# Webhook for refund
class WebhookRefundView(ViewSet):
    @method_decorator(csrf_exempt)
    def create(self, request):
        payload_in_bytes = request.body
        monnify_hash = request.META.get("HTTP_MONNIFY_SIGNATURE")
        confirmation = verify_monnify_webhook(payload_in_bytes, monnify_hash, request.META)
        if not confirmation:
            return Response({"status": "failed", "msg": "Webhook does not appear to come from Monnify"},
                            status=status.HTTP_400_BAD_REQUEST)

        data = json.loads(payload_in_bytes)
        your_secret_key = ""
        monnify_ip = ""
        api_key = ""
        monnify_username = ""
        monnify_password = ""
        monnify_token = ""
        
        with open(ENV_ROOT, 'r') as f:
            for line in f:
                if line.startswith('MONNIFY_SECRET='):
                    your_secret_key = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_IP='):
                    monnify_ip = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_TOKEN='):
                    monnify_token = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_API_KEY='):
                    api_key = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_PASSWORD='):
                    monnify_password = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_USERNAME='):
                    monnify_username = line.split('=')[1].strip()

        if not monnify_token:
            monnify_token = make_monnify_auth_request(monnify_username, monnify_password, api_key, your_secret_key)
            assign_new_token(monnify_token)

        # Parse the JSON string into a Python dictionary
        request_data = json.loads(payload_in_bytes)

        # Extracting transactionReference
        transaction_reference = request_data['eventData']['transactionReference']
        if not transaction_reference:
            return Response({"error": "Transaction reference not found in webhook data"},
                            status=status.HTTP_400_BAD_REQUEST)

        url = "https://sandbox.monnify.com/api/v1/refunds/initiate-refund"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {monnify_token}"}
        params = {"transactionReference": transaction_reference}

        try:
            response = requests.get(url, params=params, headers=headers)
            response_data = response.json()
            if response.status_code == 200:
                if response_data.get('requestSuccessful', False):
                    return webhook_refund_handle_transaction(request_data, transaction_reference)
                else:
                    return Response(response_data, status=response.status_code)
            elif 'error' in response_data and 'invalid_token' in response_data['error']:
                monnify_token = make_monnify_auth_request(monnify_username, monnify_password, api_key, your_secret_key)
                assign_new_token(monnify_token)
                headers['Authorization'] = f"Bearer {monnify_token}"
                response = requests.get(url, params=params, headers=headers)
                response_data = response.json()
                if response.status_code == 200 and response_data.get('requestSuccessful', False):
                    return webhook_refund_handle_transaction(request_data, transaction_reference)
                else:
                    return Response(response_data, status=response.status_code)
            else:
                return Response(response_data, status=response.status_code)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


















# Initiate a transfer

@method_decorator(csrf_exempt, name='dispatch')
class  InitializeTransacionForFutureSaveView(ViewSet):
    def create(self, request, *args, **kwargs):
        amount = request.data.get('amount')
        customer_name = request.data.get('customer_name')
        customer_email = request.data.get('customer_email')
        payment_reference = request.data.get('payment_reference')
        payment_description = request.data.get('payment_description')
        currency_code = request.data.get('currency_code')
        contract_code = request.data.get('contract_code')
        redirect_url = request.data.get('redirect_url')
        payment_methods = request.data.get('payment_methods')

        your_secret_key = ""
        monnify_ip = ""
        api_key = ""
        monnify_username = ""
        monnify_password = ""
        monnify_token = ""
        
        with open(ENV_ROOT, 'r') as f:
            for line in f:
                if line.startswith('MONNIFY_SECRET='):
                    your_secret_key = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_IP='):
                    monnify_ip = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_TOKEN='):
                    monnify_token = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_API_KEY='):
                    api_key = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_PASSWORD='):
                    monnify_password = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_USERNAME='):
                    monnify_username = line.split('=')[1].strip()

        if not monnify_token:
            monnify_token = make_monnify_auth_request(monnify_username, monnify_password, api_key, your_secret_key)
            assign_new_token(monnify_token)


        payload = {
                'amount': amount,
                'customerName': customer_name,
                'customerEmail': customer_email,
                "paymentReference": payment_reference,
                "paymentDescription": payment_description,
                "currencyCode": currency_code,
                "contractCode": contract_code,
                "redirectUrl": redirect_url,
                'paymentMethods': payment_methods
        }

        # Set up the headers with the base64-encoded credentials
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {monnify_token}"
        }

        try:
            response = requests.post("https://sandbox.monnify.com/api/v1/merchant/transactions/init-transaction/", json=payload, headers=headers)
            response_data = response.json()
            if response.status_code == 200:
                if response_data.get('requestSuccessful', False):
                    transaction_reference = response_data['responseBody']['transactionReference']
                    TransactionReferenceAndType.objects.create(
                        transaction_reference=transaction_reference,
                        type="saving"
                    )
                    return Response(response_data, status=response.status_code)
                else:
                    return Response(response_data, status=response.status_code)
            elif 'error' in response_data and 'invalid_token' in response_data['error']:
                monnify_token = make_monnify_auth_request(monnify_username, monnify_password, api_key, your_secret_key)
                assign_new_token(monnify_token)
                headers['Authorization'] = f"Bearer {monnify_token}"
                response = requests.get("https://sandbox.monnify.com/api/v1/merchant/transactions/init-transaction/", json=payload, headers=headers)
                response_data = response.json()
                if response.status_code == 200 and response_data.get('requestSuccessful', False):
                    return Response(response_data, status=response.status_code)
                else:
                    return Response(response_data, status=response.status_code)
            else:
                return Response(response_data, status=response.status_code)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





@method_decorator(csrf_exempt, name='dispatch')
class  FutureSavingWithCardView(ViewSet):
    def create(self, request, *args, **kwargs):
        transaction_reference = request.data.get('transaction_reference')
        collection_channel = request.data.get('collection_channel')
        number = request.data.get('number')
        expiry_month = request.data.get('expiry_month')
        expiry_year = request.data.get('expiry_year')
        pin = request.data.get('pin')
        cvv = request.data.get('cvv')

        your_secret_key = ""
        monnify_ip = ""
        api_key = ""
        monnify_username = ""
        monnify_password = ""
        monnify_token = ""
        
        with open(ENV_ROOT, 'r') as f:
            for line in f:
                if line.startswith('MONNIFY_SECRET='):
                    your_secret_key = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_IP='):
                    monnify_ip = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_TOKEN='):
                    monnify_token = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_API_KEY='):
                    api_key = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_PASSWORD='):
                    monnify_password = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_USERNAME='):
                    monnify_username = line.split('=')[1].strip()

        if not monnify_token:
            monnify_token = make_monnify_auth_request(monnify_username, monnify_password, api_key, your_secret_key)
            assign_new_token(monnify_token)


        payload = {
            "transactionReference": transaction_reference,
            "collectionChannel": collection_channel,
            "card": {
                "number": number,
                "expiryMonth": expiry_month,
                "expiryYear": expiry_year,
                "pin": pin,
                "cvv": cvv
            }
        }

        # Set up the headers with the base64-encoded credentials
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {monnify_token}"
        }

        try:
            response = requests.post("https://sandbox.monnify.com/api/v1/merchant/cards/charge", json=payload, headers=headers)
            response_data = response.json()
            if response.status_code == 200:
                if response_data.get('requestSuccessful', False):
                    TransactionReferenceAndType.objects.create(
                        transaction_reference=transaction_reference,
                        type="saving"
                    )
                    return Response(response_data, status=response.status_code)
                else:
                    return Response(response_data, status=response.status_code)
            elif 'error' in response_data and 'invalid_token' in response_data['error']:
                monnify_token = make_monnify_auth_request(monnify_username, monnify_password, api_key, your_secret_key)
                assign_new_token(monnify_token)
                headers['Authorization'] = f"Bearer {monnify_token}"
                response = requests.get("https://sandbox.monnify.com/api/v1/merchant/cards/charge", json=payload, headers=headers)
                response_data = response.json()
                if response.status_code == 200 and response_data.get('requestSuccessful', False):
                    return Response(response_data, status=response.status_code)
                else:
                    return Response(response_data, status=response.status_code)
            else:
                return Response(response_data, status=response.status_code)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@method_decorator(csrf_exempt, name='dispatch')
class  FunWalletWithCardView(ViewSet):
    def create(self, request, *args, **kwargs):
        transaction_reference = request.data.get('transaction_reference')
        collection_channel = request.data.get('collection_channel')
        number = request.data.get('number')
        expiry_month = request.data.get('expiry_month')
        expiry_year = request.data.get('expiry_year')
        pin = request.data.get('pin')
        cvv = request.data.get('cvv')

        your_secret_key = ""
        monnify_ip = ""
        api_key = ""
        monnify_username = ""
        monnify_password = ""
        monnify_token = ""
        
        with open(ENV_ROOT, 'r') as f:
            for line in f:
                if line.startswith('MONNIFY_SECRET='):
                    your_secret_key = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_IP='):
                    monnify_ip = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_TOKEN='):
                    monnify_token = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_API_KEY='):
                    api_key = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_PASSWORD='):
                    monnify_password = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_USERNAME='):
                    monnify_username = line.split('=')[1].strip()

        if not monnify_token:
            monnify_token = make_monnify_auth_request(monnify_username, monnify_password, api_key, your_secret_key)
            assign_new_token(monnify_token)


        payload = {
            "transactionReference": transaction_reference,
            "collectionChannel": collection_channel,
            "card": {
                "number": number,
                "expiryMonth": expiry_month,
                "expiryYear": expiry_year,
                "pin": pin,
                "cvv": cvv
            }
        }

        # Set up the headers with the base64-encoded credentials
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {monnify_token}"
        }

        try:
            response = requests.post("https://sandbox.monnify.com/api/v1/merchant/cards/charge", json=payload, headers=headers)
            response_data = response.json()
            if response.status_code == 200:
                if response_data.get('requestSuccessful', False):
                    TransactionReferenceAndType.objects.create(
                        transaction_reference=transaction_reference,
                        type="funding"
                    )
                    return Response(response_data, status=response.status_code)
                else:
                    return Response(response_data, status=response.status_code)
            elif 'error' in response_data and 'invalid_token' in response_data['error']:
                monnify_token = make_monnify_auth_request(monnify_username, monnify_password, api_key, your_secret_key)
                assign_new_token(monnify_token)
                headers['Authorization'] = f"Bearer {monnify_token}"
                response = requests.get("https://sandbox.monnify.com/api/v1/merchant/cards/charge", json=payload, headers=headers)
                response_data = response.json()
                if response.status_code == 200 and response_data.get('requestSuccessful', False):
                    return Response(response_data, status=response.status_code)
                else:
                    return Response(response_data, status=response.status_code)
            else:
                return Response(response_data, status=response.status_code)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class SavingViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SavingSerializer
    queryset = Saving.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            # Get the user instance
            user = self.request.user
                       
            # Call the super() method to perform the default create logic
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user)  # Pass the user instance to the serializer
            
            # Return a success response
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            # Handle any other unexpected exceptions
            return Response({'error': f'An unexpected error occurred. ({str(e)})'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        





class ViewSaving(ViewSet):
    serializer_class = SavingSerializer

    def list(self, request):
        today = timezone.now()
        print(today.time())
        queryset = Saving.objects.filter(maturity='daily', notification_time='19:12:00.000000')
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)










# Validate Account number
# @permission_classes([IsAuthenticated])
class ValidateWithDrawSaving(ViewSet):
    def create(self, request):
        user = request.user

        saving_wallet = SavingWallet.objects.all(user=user)
        amount = saving_wallet.amount
        if (saving_wallet.collection_date <= timezone.now()) and (saving_wallet.saving_type == 'permanent_lock'):
            today_date = timezone.now()
            stored_date = saving_wallet.collection_date
            date_difference = today_date - stored_date
            number_of_days = timedelta(days=date_difference.days)
            percentage = Charge.objects.get(charge_type='permanent_saving_disbursement').percentage
            return Response({"message": f"You will receive {amount + (percentage/100)*amount*number_of_days}"}, status=status.HTTP_200_OK)
        elif (saving_wallet.collection_date <= timezone.now() or saving_wallet.collection_date > timezone.now()) and saving_wallet.saving_type == 'breakable_lock':
            today_date = timezone.now()
            stored_date = saving_wallet.collection_date
            date_difference = today_date - stored_date
            number_of_days = timedelta(days=date_difference.days) 
            percentage = Charge.objects.get(charge_type='temporary_saving_disbursement').percentage
            return Response({"message": f"You will receive {amount + (percentage/100)*amount*number_of_days}"}, status=status.HTTP_200_OK)
        elif (saving_wallet.collection_date > timezone.now()) and (saving_wallet.saving_type == 'permanent_lock' and saving_wallet.with_penalty == True):
            today_date = timezone.now()
            stored_date = saving_wallet.collection_date
            date_difference = today_date - stored_date
            number_of_days = timedelta(days=date_difference.days)
            percentage = Charge.objects.get(charge_type='saving_penalty').percentage
            return Response({"message": f"You will receive {amount - (percentage/100)*amount*number_of_days}"}, status=status.HTTP_200_OK)
        elif saving_wallet.collection_date > timezone.now() and (saving_wallet.saving_type == 'permanent_lock' and saving_wallet.with_penalty == False):
            percentage = Charge.objects.get(charge_type='saving_penalty').percentage
            return Response({"Warning": f"you cannot disburse the saving since is lockable and you can contact the admin but you can recieve the penalty fee {amount - (percentage/100)*amount*number_of_days}"}, status=status.HTTP_200_OK)

        


class ValidateRefundForSaving(ViewSet):
    def create(self, request):
        user = request.user
        id = request.data.get('id')
        transaction = SavingTransaction.objects.get(user=user, id=id)
        return Response(transaction, status=status.HTTP_200_OK)
        

        
class ValidateRefundForFunding(ViewSet):
    def create(self, request):
        user = request.user
        id = request.data.get('id')
        transaction = Transaction.objects.get(user=user, id=id)
        return Response(transaction, status=status.HTTP_200_OK)
















# Withdraw save for future handler
def disburse_from_saving_wallet_handler(response_data, user, number_of_days):
    # Retrieve the charge based on the assigned charge_type
    amount_paid = float(response_data['responseBody']['amount'])
    saving_wallet = SavingWallet.objects.get(user=user)
    old_balance = saving_wallet.amount
    saving_wallet.amount = 0.0
    saving_wallet.save()
    new_balance = saving_wallet.amount
    data = {
        "amount": response_data['responseBody']['amount'],
        "reference": response_data['responseBody']['refrence'],
        "destinationAccountName": response_data['responseBody']['destinationAccountName'],
        "destinationBankName": response_data['responseBody']['destinationBankName'],
        "destinationAccountNumber": response_data['responseBody']['destinationAccountNumber'],
        "destinationBankCode": response_data['responseBody']['destinationBankCode']
        }
    transaction = SavingTransaction.objects.create(amount_paid=amount_paid, old_balance=old_balance, new_balance=new_balance, user=user, type='debit')
    serializer = DisburseFromSavingWalletTransactionSerializer(data=data, transaction=transaction)
    if serializer.is_valid():
        serializer.save(user=user)
        return Response(serializer.data, status=200)
    else:
        return Response(serializer.errors, status=400)

# Disbursement viewset 
class DisbursementFromSavingWalletHandlerViewSet(ViewSet):
    @method_decorator(csrf_exempt)
    def create(self, request):
        # Get the values from the request body using request.data.get()
        amount = request.data.get('amount')
        reference = request.data.get('reference')
        narration = request.data.get('narration')
        destination_bank_code = request.data.get('destination_bank_code')
        destination_account_number = request.data.get('destination_account_number')
        currency = request.data.get('currency')
        source_account_number = request.data.get('source_account_number')
        user = request.user


        your_secret_key = ""
        monnify_ip = ""
        api_key = ""
        monnify_username = ""
        monnify_password = ""
        monnify_token = ""
        
        with open(ENV_ROOT, 'r') as f:
            for line in f:
                if line.startswith('MONNIFY_SECRET='):
                    your_secret_key = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_IP='):
                    monnify_ip = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_TOKEN='):
                    monnify_token = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_API_KEY='):
                    api_key = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_PASSWORD='):
                    monnify_password = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_USERNAME='):
                    monnify_username = line.split('=')[1].strip()

        request_data = {
            'amount': amount,
            'reference': reference,
            'narration': narration, 
            'destinationBankCode': destination_bank_code,
            'destinationAccountNumber': destination_account_number,
            'currency': currency,
            'sourceAccountNumber': source_account_number
        }



        if not monnify_token:
            monnify_token = make_monnify_auth_request(monnify_username, monnify_password, api_key, your_secret_key)
            assign_new_token(monnify_token)


        url = "https://sandbox.monnify.com/api/v2/disbursements/single"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {monnify_token}"}

        try:
            response = requests.post(url, json=request_data, headers=headers)
            response_data = response.json()
            if response.status_code == 200:
                if response_data.get('requestSuccessful', False):
                    transaction_reference = response_data['responseBody']['refrence']
                    TransactionReferenceAndType.objects.create(
                        transaction_reference=transaction_reference,
                        type="funding"
                    )
                    return disburse_from_saving_wallet_handler(response_data, user)
                else:
                    return Response(response_data, status=response.status_code)
            elif 'error' in response_data and 'invalid_token' in response_data['error']:
                monnify_token = make_monnify_auth_request(monnify_username, monnify_password, api_key, your_secret_key)
                assign_new_token(monnify_token)
                headers['Authorization'] = f"Bearer {monnify_token}"
                response = requests.get(url, json=request_data, headers=headers)
                response_data = response.json()
                if response.status_code == 200 and response_data.get('requestSuccessful', False):
                    transaction_reference = response_data['responseBody']['refrence']
                    TransactionReferenceAndType.objects.create(
                        transaction_reference=transaction_reference,
                        type="funding"
                    )
                    return disburse_from_saving_wallet_handler(response_data, user)
                else:
                    return Response(response_data, status=response.status_code)
            else:
                return Response(response_data, status=response.status_code)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       

        







 

# Refund handler
def refund_from_saving_wallet_refund_handle(response_data, user):
    # Retrieve the charge based on the assigned charge_type
    amount_paid = float(response_data['responseBody']['refundAmount'])
    saving_wallet = SavingWallet.objects.get(user=user)
    old_balance = saving_wallet.balance
    saving_wallet.balance -= amount_paid
    saving_wallet.save()
    new_balance = saving_wallet.balance
    data = {
        "refund_amount": response_data['responseBody']['refundAmount'],
        "transaction_reference": response_data['responseBody']['transactionRefrence'],
        "refund_reference": response_data['responseBody']['refundRefrence'],
        "destination_account_name": response_data['responseBody']['destinationAccountName'],
        "destination_bank_name": response_data['responseBody']['destinationBankName'],
        "destination_account_number": response_data['responseBody']['destinationAccountNumber'],
        "destination_bank_code": response_data['responseBody']['destinationBankCode']
        }
    transaction = SavingTransaction.objects.create(amount_paid=amount_paid, old_balance=old_balance, new_balance=new_balance, user=user, type='debit')
    serializer = RefundFromSavingWalletTransaction(data=data, transaction=transaction)
    if serializer.is_valid():
        serializer.save(user=user)
        return Response(serializer.data, status=200)
    else:
        return Response(serializer.errors, status=400)

# refund viewset 
class RefundFromSavingWalletViewSet(ViewSet):
    @method_decorator(csrf_exempt)
    def create(self, request):
        # Get the values from the request body using request.data.get()
        transaction_reference = request.data.get('transaction_reference')
        refund_reference = request.data.get('refund_reference')
        refund_amount = request.data.get('refund_amount')
        refund_reason = request.data.get('refund_reason')
        customer_note = request.data.get('customer_note')
        destination_bank_code = request.data.get('destination_bankcode')
        destination_account_number = request.data.get('destination_account_number')
        user = request.user
       


        your_secret_key = ""
        monnify_ip = ""
        api_key = ""
        monnify_username = ""
        monnify_password = ""
        monnify_token = ""
        
        with open(ENV_ROOT, 'r') as f:
            for line in f:
                if line.startswith('MONNIFY_SECRET='):
                    your_secret_key = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_IP='):
                    monnify_ip = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_TOKEN='):
                    monnify_token = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_API_KEY='):
                    api_key = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_PASSWORD='):
                    monnify_password = line.split('=')[1].strip()
                elif line.startswith('MONNIFY_USERNAME='):
                    monnify_username = line.split('=')[1].strip()

        request_data = {
            'transactionReference': transaction_reference,
            'refundReference': refund_reference,
            'refundAmount': refund_amount,
            'refundReason': refund_reason,
            'customerNote': customer_note,
            'destinationBankCode': destination_bank_code,
            'destinationAccountNumber': destination_account_number,
        }



        if not monnify_token:
            monnify_token = make_monnify_auth_request(monnify_username, monnify_password, api_key, your_secret_key)
            assign_new_token(monnify_token)


        url = "https://sandbox.monnify.com/api/v1/refunds/initiate-refund"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {monnify_token}"}

        try:
            response = requests.post(url, json=request_data, headers=headers)
            response_data = response.json()
            if response.status_code == 200:
                if response_data.get('requestSuccessful', False):
                    return refund_handle_transaction(response_data, user)
                else:
                    return Response(response_data, status=response.status_code)
            elif 'error' in response_data and 'invalid_token' in response_data['error']:
                monnify_token = make_monnify_auth_request(monnify_username, monnify_password, api_key, your_secret_key)
                assign_new_token(monnify_token)
                headers['Authorization'] = f"Bearer {monnify_token}"
                response = requests.get(url, json=request_data, headers=headers)
                response_data = response.json()
                if response.status_code == 200 and response_data.get('requestSuccessful', False):
                    transaction_reference = response_data['responseBody']['refrence']
                    TransactionReferenceAndType.objects.create(
                        transaction_reference=transaction_reference,
                        type="saving"
                    )
                    return refund_handle_transaction(response_data, user)
                else:
                    return Response(response_data, status=response.status_code)
            else:
                return Response(response_data, status=response.status_code)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
 