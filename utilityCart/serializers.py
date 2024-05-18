from rest_framework import serializers
from .models import DataAPISetting, AirtimeAPISetting, CableAPISetting, ElectricityAPISetting, DataPlan, CablePlan, DataTransaction, AirtimeTransaction, CableTransaction, ElectricityTransaction




class DataAPISettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataAPISetting
        fields = ['network', 'plan_type', 'api_url', 'api_name', 'token']

class AirtimeAPISettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirtimeAPISetting
        fields = ['api', 'network']

class CableAPISettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CableAPISetting
        fields = ['api_name', 'cable', 'api_url', 'token']

class ElectricityAPISettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElectricityAPISetting
        fields = ['api']


class DataPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataPlan
        fields = ['plan_type', 'network', 'data_size', 'price', 'validity_period']



class CablePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = CablePlan
        fields = ['id', 'cableplan_id', 'cable', 'package', 'plan_amount']





class DataTransactionSerializer(serializers.ModelSerializer):
    user_id =  serializers.IntegerField(read_only=True)
    old_balance =  serializers.FloatField(read_only=True)
    new_balance =  serializers.FloatField(read_only=True)
    date =  serializers.DateTimeField(read_only=True)
    class Meta:
        model = DataTransaction
        fields = ['id', 'network', "amount", 'mobile_number', 'plan_type', 'user_id', 'old_balance', 'new_balance', 'date']


class AirtimeTransactionSerializer(serializers.ModelSerializer):
    user_id =  serializers.IntegerField(read_only=True)
    old_balance =  serializers.FloatField(read_only=True)
    new_balance =  serializers.FloatField(read_only=True)
    date =  serializers.DateTimeField(read_only=True)
    class Meta:
        model = AirtimeTransaction
        fields = ['id', 'network', 'amount', 'mobile_number', 'airtime_type', 'user_id', 'old_balance', 'new_balance', 'date']

class CableTransactionSerializer(serializers.ModelSerializer):
    user_id =  serializers.IntegerField(read_only=True)
    old_balance =  serializers.FloatField(read_only=True)
    new_balance =  serializers.FloatField(read_only=True)
    date =  serializers.DateTimeField(read_only=True)
    class Meta:
        model = CableTransaction
        fields = ['id', 'cablename_id', 'cableplan_id', 'smart_card_number', 'user_id', 'old_balance', 'new_balance', 'date']


class ElectricityTransactionSerializer(serializers.ModelSerializer):
    user_id =  serializers.IntegerField(read_only=True)
    old_balance =  serializers.FloatField(read_only=True)
    new_balance =  serializers.FloatField(read_only=True)
    date =  serializers.DateTimeField(read_only=True)
    class Meta:
        model = ElectricityTransaction
        fields = ['id', 'disco_name', 'amount', 'meter_number', 'old_balance', 'new_balance', 'meter_type', 'date', 'user_id']