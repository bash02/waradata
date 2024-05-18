from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, serializers
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.viewsets import ModelViewSet
from .models import Charge, CableAPISetting, DataAPISetting, DataTransaction, AirtimeTransaction, ElectricityTransaction, CableTransaction, AirtimeAPISetting, ElectricityAPISetting, CablePlan, DataPlan
from .serializers import DataAPISettingSerializer, DataTransactionSerializer, AirtimeTransactionSerializer, CableAPISettingSerializer, ElectricityAPISettingSerializer, AirtimeAPISetting, CablePlanSerializer, DataPlanSerializer, CableTransactionSerializer, ElectricityTransactionSerializer
from djoser.conf import settings
import requests, uuid, re




class DataPlanView(ModelViewSet):
    queryset = DataPlan.objects.all()
    serializer_class = DataPlanSerializer
    
    def get_permissions(self):
        if self.request.method in ['POST', 'PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    


class CablePlanView(ModelViewSet):
    queryset = CablePlan.objects.all()
    serializer_class = CablePlanSerializer
    
    def get_permissions(self):
        if self.request.method in ['POST', 'PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]





class BuyDataViewSet(ViewSet):
    def get_plans(plans_url, token):
        headers = {
            'Authorization': f"Token {token}",
            'Content-Type': 'application/json'
        }
    
        response = requests.get(plans_url, headers=headers)

    def search_plan(dataplans, network, plan_type, month_validate, plan):
        for network_key, network_data in dataplans.items():
            if network_key == f"{network}_PLAN":
                for type_key, plans_list in network_data.items():
                    if type_key == plan_type:
                        for plan_info in plans_list:
                            if (plan_info["month_validate"] == month_validate and
                                plan_info["plan"] == plan):
                                return plan_info["dataplan_id"]
        return None  # Return None if no matching plan is found

    def get_service_variations(self, service_id, plans_url):
        params = {'serviceID': service_id}
        
        try:
            response = requests.get(plans_url, params=params)
            response.raise_for_status()  # Raise HTTPError for non-200 status codes
            
            return response.json().get('content', {}).get('variations', [])

        except requests.RequestException as e:
            print(f"API request failed: {e}")
            return []

    def handle_request(self, token, payload, purchase_url, user, amount, plan_type, network, mobile_number):
        headers = {'Authorization': f"Token {token}", 'Content-Type': 'application/json'}
    
        try:
            old_balance = user.balance
            if old_balance < amount:
                raise ValueError('Insufficient balance')
            
            response = requests.post(purchase_url, headers=headers, json=payload)
            response.raise_for_status()  # Raise HTTPError for non-2xx status codes
    
            new_balance = old_balance - amount
            user.balance = new_balance
            user.save()
    
            DataTransaction.objects.create(user=user, old_balance=old_balance, new_balance=new_balance, amount=amount, network=network, plan_type=plan_type, mobile_number=mobile_number)
    
            return Response({'message': response.json()}, status=status.HTTP_201_CREATED)
    
        except requests.HTTPError as e:
            response_data = e.response.json() if e.response else {}
            print(f"API request failed: {e}")
            return Response({'error': 'Transaction failed', 'response_data': response_data}, status=e.response.status_code if e.response else status.HTTP_500_INTERNAL_SERVER_ERROR)
    
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        user = self.request.user
        amount = request.data.get('amount')
        plan_type = request.data.get('plan_type')
        network = request.data.get("network")
        mobile_number = request.data.get('mobile_number')
        month_validate = request.data.get('month_validate')
        data_size = request.data.get('data_size')
        quantity = request.data.get(quantity)

        if network == "MTN":
            network_id = 1
        if network == "AIRTEL":
            network_id = 2
        if network == "GLO":
            network_id = 3
        if network == "9-MOBILE":
            network_id = 4

        try:
            obj = DataAPISetting.objects.get(network=network, plan_type=plan_type)
            plans_url = obj.plans_url
            purchase_url = obj.purchase_url
            api_name = obj.api_name
            token = obj.token


            if api_name == "gongoz-concept" or "maskawa-sub" or "hosmo-data" or "gladtiddings-data":
                dataplans = self.get_plans(plans_url, token)
                plan_id = self.search_plan(dataplans=dataplans, plan_network=network, plan_type=plan_type, month_validate=month_validate, plan=data_size)
                payload = {"network": network_id, "mobile_number": mobile_number, "plan": plan_id, "Ported_number": True}
                return self.handle_request(token, payload, purchase_url, user, amount, plan_type, network, mobile_number)
            
            elif api_name == "VTPASS":
                if network == 'Smile':
                    service_id = f'{network.lower()}-direct'
                elif network == 'Spectranet':
                    service_id = f'{network.lower()}'
                else:
                    service_id = f'{network.lower()}-direct'
                result = self.get_service_variations(service_id, plans_url)

                pattern = f'{network} N{amount} {data_size}'
                compiled_pattern = re.compile(pattern, re.IGNORECASE)

                for variation in result:
                    name = variation.get("name", "")
                    variation_code = variation.get("variation_code", "")

                    if compiled_pattern.search(name):
                        request_id = f'Data_{uuid.uuid4().hex[:15]}'
                        if network == 'spectranet':
                            payload = {
                                'request-id': request_id,
                                'serviceID': service_id,
                                'billersCode': mobile_number,
                                'variation_code': variation_code,
                                'quantity': quantity,
                                'phone': mobile_number
                            }
                        else:
                            payload = {
                                'request-id': request_id,
                                'serviceID': service_id,
                                'billersCode': mobile_number,
                                'variation_code': variation_code,
                                'phone': mobile_number
                            }

                        return self.handle_request(token, payload, plans_url, user, amount, plan_type, network, mobile_number)

                print("No matching variation found.")

            else:
                return Response({'error': 'Invalid API name'}, status=status.HTTP_400_BAD_REQUEST)

        except DataAPISetting.DoesNotExist:
            return Response({'error': 'Data API setting not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

class BuyAirtimeViewSet(ViewSet):
    def handle_request(self, token, payload, url, user, amount, airtime_type, network, mobile_number):
        headers = {'Authorization': f"Token {token}", 'Content-Type': 'application/json'}
    
        try:
            old_balance = user.balance
            if old_balance < amount:
                raise ValueError('Insufficient balance')
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()  # Raise HTTPError for non-2xx status codes
    
            new_balance = old_balance - amount
            user.balance = new_balance
            user.save()
    
            AirtimeTransaction.objects.create(user=user, old_balance=old_balance, new_balance=new_balance, amount=amount, network=network, airtime_type=airtime_type, mobile_number=mobile_number)
    
            return Response({'message': response.json()}, status=status.HTTP_201_CREATED)
    
        except requests.HTTPError as e:
            response_data = e.response.json() if e.response else {}
            print(f"API request failed: {e}")
            return Response({'error': 'Transaction failed', 'response_data': response_data}, status=e.response.status_code if e.response else status.HTTP_500_INTERNAL_SERVER_ERROR)
    
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        user = self.request.user
        amount = request.data.get('amount')
        airtime_type = request.data.get('airtime_type')
        network_id = request.data.get("network_id")
        network = request.data.get("network_name")
        mobile_number = request.data.get('mobile_number')
        airtime_type = request.data.get('airtime_type')


        try:
            obj = AirtimeAPISetting.objects.get(network=network, airtime_type=airtime_type)
            url = obj.purchase_url
            api_name = obj.api_name
            token = obj.token

            if api_name == "gongoz-concept" or "maskawa-sub" or "hosmo-data" or "gladtiddings-data":
                payload = {
                    "network": network_id,
                    "amount": amount,
                    "mobile_number": mobile_number,
                    "Ported_number": True,
                    "airtime_type": airtime_type
                }
                return self.handle_request(token, payload, url, user, amount, network, mobile_number)
            
            elif api_name == "VTPASS":
                service_id = f'{network.lower()}'
                request_id = f'Data_{uuid.uuid4().hex[:15]}'
                payload = {
                    'request-id': request_id,
                    'serviceID': service_id,
                    'amount': amount,
                    'phone': mobile_number
                }

                return self.handle_request(token, payload, url, user, amount, airtime_type, network, mobile_number)


            else:
                return Response({'error': 'Invalid API name'}, status=status.HTTP_400_BAD_REQUEST)

        except AirtimeAPISetting.DoesNotExist:
            return Response({'error': 'Data API setting not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)











@permission_classes([IsAuthenticated])
class BillPaymentView(ViewSet):
    def handle_request(self, payload, url, token, user, amount, meter_type, meter_number, disco_name):
        headers = {
            'Authorization': f"Token {token}",
            'Content-Type': 'application/json'
        }
    
        try:
            old_balance = user.balance
            if old_balance < amount:
                raise ValueError('Insufficient balance')
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()

    
            # Assuming the response contains JSON data, access it using response.json()
            response_data = response.json()
    
            if response.status_code == 201 or response.status_code == 200:
                # Update user's balance only if the status code is 201
                new_balance = old_balance - amount
                user.balance = new_balance
                user.save()
    
                ElectricityTransaction.objects.create(user=user, old_balance=old_balance, new_balance=new_balance, amount=amount, meter_type=meter_type, meter_number=meter_number, disco_name=disco_name)
                return Response({'message': response_data}, status=status.HTTP_201_CREATED)

            if response.status_code == 200:
                # Update user's balance only if the status code is 201
                new_balance = old_balance - amount
                user.balance = new_balance
                user.save()
    
                ElectricityTransaction.objects.create(user=user, old_balance=old_balance, new_balance=new_balance, amount=amount, meter_type=meter_type, meter_number=meter_number, disco_name=disco_name)
                return Response({'message': response_data}, status=status.HTTP_200_OK)
            else:
                # Raise an exception for other status codes
                response.raise_for_status()
    
        except requests.HTTPError as e:
            # Handle HTTPError, including 400 status codes
            response_data = e.response.json()
            return Response({'error': 'Transaction failed', 'response_data': response_data}, status=e.response.status_code)
    
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
            
    def create(self, request, *args, **kwargs):
        # Validate and deserialize data using the serializer
        user = self.request.user
        disco_name = request.data.get('disco_name')
        amount = request.data.get('amount')
        meter_number = request.data.get("meter_number")
        mobile_number = request.data.get("mobile_number")
        meter_type = request.data.get("meter_type")

        try:
            obj = ElectricityAPISetting.objects.all().first()
            url = obj.purchase_url
            token = obj.token 
            api_name = obj.api_name
            if api_name == "gongoz-concept" or "maskawa-sub" or "hosmo-data" or "gladtiddings-data":
                # Manually construct the payload using the received data
                payload = {
                    "disco_name": disco_name,
                    "amount": amount,
                    "meter_number": meter_number,
                    "MeterType": meter_type
                }

            if api_name == "VT-Pass":
                request_id = f'Data_{uuid.uuid4().hex[:15]}'
                # Manually construct the payload using the received data
                payload = {
                    "request_id": request_id,
                    "serviceID": disco_name,
                    "billersCode": meter_number,
                    "variation_code": meter_type,
                    "amount": amount,
                    "phone": mobile_number
                }


            return self.handle_request(payload, url, token, user, amount, meter_type, meter_number, disco_name)

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)



@permission_classes([IsAuthenticated])
class CableSubscriptionView(ViewSet):
    def get_plans(plans_url, token):
        headers = {
            'Authorization': f"Token {token}",
            'Content-Type': 'application/json'
        }
    
        response = requests.get(plans_url, headers=headers)
    

    def search_cable_plan_id(plans, cable=None, package=None, plan_amount=None):
        for p in plans:
            if (not cable or p["cable"] == cable) and \
            (not package or p["package"] == package):
                return p["cableplan_id"]  # Return the first matching plan found

        return None  # Return None if no matching plan is found

    def handle_request(payload, purchase_url, token, user, amount, cablename, smart_card_number, package):

        headers = {
            'Authorization': f"Token {token}",
            'Content-Type': 'application/json'
        }
    
        try:
            old_balance = user.balance
            if old_balance < amount:
                raise ValueError('Insufficient balance')
            
            response = requests.post(purchase_url, headers=headers, json=payload)
            response.raise_for_status()
    
            # Assuming the response contains JSON data, access it using response.json()
            response_data = response.json()
    
            if response.status_code == 201:
                # Update user's balance only if the status code is 201
                new_balance = old_balance - amount
                user.balance = new_balance
                user.save()
    
                CableTransaction.objects.create(user=user, old_balance=old_balance, new_balance=new_balance, amount=amount, cablename=cablename, smart_card_number=smart_card_number, package=package)
                return Response({'message': response_data}, status=status.HTTP_201_CREATED)
            elif response.status_code == 200:
                # Do something specific if the status code is 200
                # Update user's balance only if the status code is 201
                new_balance = old_balance - amount
                user.balance = new_balance
                user.save()
    
                CableTransaction.objects.create(user=user, old_balance=old_balance, new_balance=new_balance, amount=amount, cablename=cablename, smart_card_number=smart_card_number, package=package)
                return Response({'message': response_data}, status=status.HTTP_200_OK)
            else:
                # Raise an exception for other status codes
                response.raise_for_status()
    
        except requests.HTTPError as e:
            # Handle HTTPError, including 400 status codes
            response_data = e.response.json()
            return Response({'error': 'Transaction failed', 'response_data': response_data}, status=e.response.status_code)
    
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)

    def create(self, request, *args, **kwargs):
        # Validate and deserialize data using the serializer
        user = self.request.user
        cablename = request.data.get('cablename')
        package = request.data.get('package')
        smart_card_number = request.data.get('smart_card_number')
        amount = request.data.get('amount')
        subscription_type = request.data.get('subscription_type')
        mobile_number = request.data.get('mobile_number')

        try:
            obj = CableAPISetting.objects.all().first()
            plans_url = obj.plans_url
            purchase_url = obj.purchase_url
            token = obj.token 
            api_name = obj.api_name
            if api_name == "gongoz-concept" or "maskawa-sub" or "hosmo-data" or "gladtiddings-data":
                if cablename == 'DSTV':
                    cablename_id = 1
                if cablename == 'GOTV':
                    cablename_id = 2
                if cablename == 'STARTIMES':
                    cablename_id = 3
                plans = self.get_plans(plans_url, token)
                cableplan_id = self.search_cable_plan_id(plans, cable=cablename, package=package)
                # Manually construct the payload using the received data
                payload = {
                    "cablename": cablename_id,
                    "cableplan": cableplan_id,
                    "smart_card_number": smart_card_number
                    }

            elif api_name == "VT-PASS":
                if cablename == 'DSTV' or 'GOTV':
                    service_id = f'{cablename.lower()}-data'
                    result = self.get_service_variations(service_id, plans_url)

                    pattern = f'{package} N{amount}'
                    compiled_pattern = re.compile(pattern, re.IGNORECASE)

                    for variation in result:
                        name = variation.get("name", "")
                        variation_code = variation.get("variation_code", "")

                        if compiled_pattern.search(name):
                            request_id = f'Data_{uuid.uuid4().hex[:15]}'
                            if subscription_type == 'change':
                                payload = {
                                    'request-id': request_id,
                                    'serviceID': service_id,
                                    'billersCode': smart_card_number,
                                    'variation_code': variation_code,
                                    'amount': amount,
                                    'phone': mobile_number,
                                    'subscription_type': subscription_type
                                }
                            elif subscription_type == 'renew':
                                payload = {
                                    'request-id': request_id,
                                    'serviceID': service_id,
                                    'billersCode': smart_card_number,
                                    'amount': amount,
                                    'phone': mobile_number,
                                    'subscription_type': subscription_type
                                }
                            return self.handle_request(payload, purchase_url, token, user, amount, cablename, smart_card_number, package)


                if cablename == 'STARTIMES':
                    service_id = f'{cablename.lower()}-data'
                    result = self.get_service_variations(service_id, plans_url)

                    pattern = f'{package} N{amount}'
                    compiled_pattern = re.compile(pattern, re.IGNORECASE)

                    for variation in result:
                        name = variation.get("name", "")
                        variation_code = variation.get("variation_code", "")

                        if compiled_pattern.search(name):
                            request_id = f'Data_{uuid.uuid4().hex[:15]}'
                            payload = {
                                'request-id': request_id,
                                'serviceID': service_id,
                                'billersCode': smart_card_number,
                                'variation_code': variation_code,
                                'phone': mobile_number,
                            }
                            return self.handle_request(payload, purchase_url, token, user, amount, cablename, smart_card_number, package)

                if cablename == 'SHOWMAX':
                    service_id = f'{cablename.lower()}-data'
                    result = self.get_service_variations(service_id, plans_url)

                    pattern = f'{package} N{amount}'
                    compiled_pattern = re.compile(pattern, re.IGNORECASE)

                    for variation in result:
                        name = variation.get("name", "")
                        variation_code = variation.get("variation_code", "")
   
                        if compiled_pattern.search(name):
                            request_id = f'Data_{uuid.uuid4().hex[:15]}'
                            payload = {
                                'request-id': request_id,
                                'serviceID': service_id,
                                'billersCode': smart_card_number,
                                'variation_code': variation_code,
                            }
                            return self.handle_request(payload, purchase_url, token, user, amount, cablename, smart_card_number, package)


        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    


           





class ValidateIUC(ViewSet):
    def create(self, request):
        smart_card_number = request.data.get('smart_card_number')
        cablename = request.data.get('cablename')
        obj = CableAPISetting.objects.all().first()
        base_url = obj.validate_url
        token = obj.token 
        api_name = obj.api_name
        if api_name == "gongoz-concept" or "maskawa-sub" or "hosmo-data" or "gladtiddings-data":
            headers = {
                'Authorization': f"Token {token}",
                'Content-Type': 'application/json'
            }


            url = f'{base_url}?smart_card_number={smart_card_number}&cablename={cablename}'
            # Make the GET request
            response = requests.post(url, headers=headers)
    

            if response.status_code == status.HTTP_200_OK:
                return Response(response.json(), status=status.HTTP_200_OK)
        elif api_name == "VT-Pass":
            service_id = f'{cablename.lower()}-data'
            headers = {
                'Authorization': f"Token {token}",
                'Content-Type': 'application/json'
            }
            payload = {
                'billersCode': smart_card_number,
                'serviceID': service_id,
            }


            # Make the GET request
            response = requests.post(base_url, headers=headers)
    

            if response.status_code == status.HTTP_200_OK:
                return Response(response.json(), status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Failed to validate iuc'}, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([IsAuthenticated])
class ValidateMeterView(ViewSet):
    def create(self, request):
        meternumber = request.data.get('meternumber')
        disconame = request.data.get('disconame')
        metertype = request.data.get('metertype')
        
        obj = ElectricityAPISetting.objects.all().first()
        base_url = obj.validate_url
        token = obj.token 
        api_name = obj.api_name
        if api_name == "gongoz-concept" or "maskawa-sub" or "hosmo-data" or "gladtiddings-data":
            headers = {
                'Authorization': f"Token {token}",
                'Content-Type': 'application/json'
            }


            url = f'{base_url}?meternumber={meternumber}&disconame={disconame}&mtype={metertype}'
            # Make the GET request
            response = requests.post(url, headers=headers)
    

            if response.status_code == status.HTTP_200_OK:
                return Response(response.json(), status=status.HTTP_200_OK)
        elif api_name == "VT-Pass":
            service_id = f'{disconame.lower()}-data'
            headers = {
                'Authorization': f"Token {token}",
                'Content-Type': 'application/json'
            }
            payload = {
                'billersCode': meternumber,
                'serviceID': service_id,
                'type': type
            }


            # Make the GET request
            response = requests.post(base_url, headers=headers)
    

            if response.status_code == status.HTTP_200_OK:
                return Response(response.json(), status=status.HTTP_200_OK)

        else:
            return Response({'error': 'Failed to validate meter'}, status=status.HTTP_400_BAD_REQUEST)
        









class ValidateEmailForSmileDirectViewSet(ViewSet):
    def create(self, request):
        plan_type = request.data.get('plan_type')
        network = request.data.get("network")
        smile_emaail = request.data.get("smile_email")
        obj = DataAPISetting.first(network=network, plan_type=plan_type)
        base_url = obj.validate_url
        token = obj.token 
        service_id = f'{network.lower()}-direct'
        headers = {
            'Authorization': f"Token {token}",
            'Content-Type': 'application/json'
        }
        payload = {
            'billersCode': smile_emaail,
            'serviceID': service_id,
        }


        # Make the GET request
        response = requests.post(base_url, headers=headers)


        if response.status_code == status.HTTP_200_OK:
            return Response(response.json(), status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Failed to validate iuc'}, status=status.HTTP_400_BAD_REQUEST)