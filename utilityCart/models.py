from django.db import models
from django.conf import settings


class Charge(models.Model):
    DATA = 'data'
    AIRTIME = 'airtime'
    BILL = 'bill'
    CABLE = 'cable'


    CHARGE_TYPE_CHOICES = [
        (DATA, 'Data Charge'),
        (AIRTIME, 'Airtime Charge'),
        (BILL, 'Bill Charge'),
        (CABLE, 'Cable Charge')
        # Add more choices as needed
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    percentage = models.FloatField()
    charge_type = models.CharField(max_length=20, choices=CHARGE_TYPE_CHOICES)

    def __str__(self):
        return self.name
    
class DataTransaction(models.Model):
    network = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=15)
    amount = models.FloatField(null=True)
    plan_type = models.CharField(max_length=255)
    old_balance = models.FloatField(blank=True, null=True)
    new_balance = models.FloatField(blank=True, null=True)
    date = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.network_id} - {self.mobile_number} - {self.plan_id}"

class AirtimeTransaction(models.Model):
    network = models.CharField(max_length=255)
    amount = models.FloatField(null=True)
    mobile_number = models.CharField(max_length=15)
    airtime_type = models.CharField(max_length=255)
    old_balance = models.FloatField(blank=True, null=True)
    new_balance = models.FloatField(blank=True, null=True)
    date = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.network} - {self.amount} - {self.mobile_number} - {self.airtime_type}"


class CableTransaction(models.Model):
    cablename = models.IntegerField(null=True)
    smart_card_number = models.CharField(max_length=255, null=True)
    package = models.CharField(max_length=255, null=True)
    old_balance = models.FloatField(blank=True, null=True)
    new_balance = models.FloatField(blank=True, null=True)
    date = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.cablename} - {self.cableplan} - {self.smart_card_number}"



class ElectricityTransaction(models.Model):
    disco_name = models.IntegerField(null=True)
    amount = models.FloatField(blank=True, null=True)
    meter_number = models.BigIntegerField(null=True)  # Change to BigIntegerField
    old_balance = models.FloatField(blank=True, null=True)
    new_balance = models.FloatField(blank=True, null=True)
    meter_type = models.CharField(max_length=255, null=True)
    date = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.disco_name} - {self.amount} - {self.meter_number} - {self.meter_type}"



class DataAPISetting(models.Model):
    VTPASS = 'VT-Pass'
    GONGOZ_CONCEPT = 'gongoz-concept'
    MASKAWA_SUB = 'maskawa-sub'
    HUSMO_DATA = 'hosmo-data'
    SIM_HOSTING = 'sim-hosting'
    GLATIDDINGS_DATA = 'gladtiddings-data'


    API_NAME_CHOICES = [
        (VTPASS, 'VT-Pass API Endpoint'),
        (GONGOZ_CONCEPT, 'Gongoz-concept API Endpoint'),
        (MASKAWA_SUB, 'Masakawa-sub API Endpoint'),
        (HUSMO_DATA, 'Hosmo-data API Endpoint'),
        (SIM_HOSTING, 'Sim-Hosting API Endpoint'),
        (GLATIDDINGS_DATA, 'Glatiddings-data API Endpoint')
        # Add more choices as needed
    ]


    VTPASS_MTN_DATA_PLAN_URL = 'https://api-service.vtpass.com/api/service-variations?serviceID=mtn-data'
    VTPASS_AIRTEL_DATA_PLAN_URL = 'https://api-service.vtpass.com/api/service-variations?serviceID=airtel-data'
    VTPASS_GLO_DATA_PLAN_URL = 'https://api-service.vtpass.com/api/service-variations?serviceID=glo-data'
    VTPASS_9MOBILE_DATA_PLAN_URL = 'https://api-service.vtpass.com/api/service-variations?serviceID=etisalat-data'
    VTPASS_9MOBILE_SME_DATA_PLAN_URL = 'https://api-service.vtpass.com/api/service-variations?serviceID=etisalat-sme-data'
    VTPASS_SMILE_DATA_PLAN_URL = 'https://api-service.vtpass.com/api/service-variations?serviceID=smile-direct'
    VTPASS_SPECTRANET_DATA_PLAN_URL = 'https://api-service.vtpass.com/api/service-variations?serviceID=spectranet'
    GONGOZ_CONCEPT_PLAN_URL = 'https://www.gongozconcept.com/api/user/'
    MASKAWA_SUB_PLAN_URL = 'https://maskawasubapi.com/api/users/'
    HUSMO_DATA_PLAN_URL = 'https://husmodata.com/api/users/'
    GLATIDDINGS_DATA_PLAN_URL = 'https://www.gladtidingsdata.com/api/user/'




    DATA_PLANS_URL_CHOICES = [
        (VTPASS_MTN_DATA_PLAN_URL, 'VTPass mtn data url'),
        (VTPASS_AIRTEL_DATA_PLAN_URL, 'VTPass airtel data url'),
        (VTPASS_GLO_DATA_PLAN_URL, 'VTPass glo data url'),
        (VTPASS_9MOBILE_DATA_PLAN_URL, 'VTPass 9-mobile data url'), 
        (VTPASS_9MOBILE_SME_DATA_PLAN_URL, 'VTPass 9-mobile sme data url'),
        (VTPASS_SMILE_DATA_PLAN_URL, 'VTPass smile data url'), 
        (VTPASS_SPECTRANET_DATA_PLAN_URL, 'VTPass spectranet data url'), 
        (GONGOZ_CONCEPT_PLAN_URL, 'Gongoz-concept url'),
        (HUSMO_DATA_PLAN_URL, 'Hosmo-data url'),
        (GLATIDDINGS_DATA_PLAN_URL, 'Glatiddings-sub url'),
        (MASKAWA_SUB_PLAN_URL, 'Maskawa-sub url')
        # Add more choices as needed
    ]



    MTN = 'MTN'
    GLO = 'Glo'
    AIRTEL = 'Airtel'
    SMILE = 'Smile'
    ETISALAT = '9Mobile'
    ETISALAT_SME = '9Mobile SME'
    SPECTRANET = 'Spectranet'



    NETWORK_TYPE_CHOICES = [
        (MTN, 'MTN'),
        (GLO, 'Glo'),
        (AIRTEL, 'Airtel'),
        (SMILE, 'Smile'),
        (ETISALAT, '9Mobile'),
        (ETISALAT_SME, '9Mobile SME'),
        (SPECTRANET, 'Spectranet'),
    ]


    SME = 'SME'
    ALL = 'ALL'
    GIFTING = 'GIFTING'
    CORPORATE = 'CORPORATE'


    PLAN_TYPE_CHOICES = [
        (ALL, 'All plans'),
        (SME, 'SME Plans'),
        (GIFTING, 'Gifting Plans'),
        (CORPORATE, 'CORPORATE Plans')
        # Add more choices as needed
    ]


    VTPASS_DATA_PURCHASE_URL = 'https://api-service.vtpass.com/api/pay/'
    GONGOZ_CONCEPT_DATA_PURCHASE_URL = 'https://www.gongozconcept.com/api/data/'
    MASKAWA_SUB_DATA_PURCHASE_URL = 'https://maskawasubapi.com/api/data/'
    GLATIDDINGS_DATA_PURCHASE_URL = 'https://www.gladtidingsdata.com/api/data/'
    HUSMO_DATA_DATA_PURCHASE_URL = 'https://husmodata.com/api/data/'





    DATA_PURCHASE_URL_CHOICES = [
        (VTPASS_DATA_PURCHASE_URL, 'VT-Pass Data Purchase url'),
        (GONGOZ_CONCEPT_DATA_PURCHASE_URL, 'Gongoz-concept Data Purchase url'),
        (HUSMO_DATA_DATA_PURCHASE_URL, 'Hosmo-data Data Purchase url'),
        (GLATIDDINGS_DATA_PURCHASE_URL, 'Glatiddings-sub Data Purchase url'),
        (MASKAWA_SUB_DATA_PURCHASE_URL, 'Maskawa-sub Data Purchase url')
        # Add more choices as needed
    ]



    VTPASS_VALIDATE_SMILE_DIRECT_URL = 'https://api-service.vtpass.com/api/merchant-verify'






    DATA_VALIDATE_URL_CHOICES = [
        (VTPASS_VALIDATE_SMILE_DIRECT_URL, 'VT-Pass vaidate email for smile-direct url'),
        # Add more choices as needed
    ]

    network = models.CharField(max_length=255, null=True, choices=NETWORK_TYPE_CHOICES)
    plan_type = models.CharField(max_length=255, null=True, choices=PLAN_TYPE_CHOICES)
    api_name = models.CharField(max_length=255, null=True, choices=API_NAME_CHOICES)
    plans_url = models.CharField(max_length=255, null=True, choices=DATA_PLANS_URL_CHOICES)
    validate_url = models.CharField(max_length=255, null=True, choices=DATA_VALIDATE_URL_CHOICES)
    purchase_url = models.CharField(max_length=255, null=True, choices=DATA_PURCHASE_URL_CHOICES)
    token = models.CharField(max_length=255, blank=True, null=True)






class AirtimeAPISetting(models.Model):
    VTPASS = 'VT-Pass'
    GONGOZ_CONCEPT = 'gongoz-concept'
    MASKAWA_SUB = 'maskawa-sub'
    HUSMO_DATA = 'hosmo-data'
    SIM_HOSTING = 'sim-hosting'
    GLATIDDINGS_DATA = 'gladtiddings-data'


    API_NAME_CHOICES = [
        (VTPASS, 'VT-Pass API Endpoint'),
        (GONGOZ_CONCEPT, 'Gongoz-concept API Endpoint'),
        (MASKAWA_SUB, 'Masakawa-sub API Endpoint'),
        (HUSMO_DATA, 'Hosmo-data API Endpoint'),
        (SIM_HOSTING, 'Sim-Hosting API Endpoint'),
        (GLATIDDINGS_DATA, 'Glatiddings-data API Endpoint')
        # Add more choices as needed
    ]



    MTN = 'MTN'
    GLO = 'Glo'
    AIRTEL = 'Airtel'
    ETISALAT = 'Etisalat'



    NETWORK_TYPE_CHOICES = [
        (MTN, 'MTN'),
        (GLO, 'Glo'),
        (AIRTEL, 'Airtel'),
        (ETISALAT, '9-Mobile'),
        # Add more choices as needed
    ]

    VTPASS_DATA_PURCHASE_URL = 'https://api-service.vtpass.com/api/service-variations?serviceID=mtn-data'
    GONGOZ_CONCEPT_DATA_PURCHASE_URL = 'https://www.gongozconcept.com/api/topup/'
    MASKAWA_SUB_DATA_PURCHASE_URL = 'https://maskawasubapi.com/api/topup/'
    GLATIDDINGS_DATA_PURCHASE_URL = 'https://www.gladtidingsdata.com/api/topup/'
    HUSMO_DATA_DATA_PURCHASE_URL = 'https://husmodata.com/api/topup/'





    PURCHASE_DATA__URL_CHOICES = [
        (VTPASS_DATA_PURCHASE_URL, 'VT-Pass Data Purchase url'),
        (GONGOZ_CONCEPT_DATA_PURCHASE_URL, 'Gongoz-concept Data Purchase url'),
        (HUSMO_DATA_DATA_PURCHASE_URL, 'Hosmo-data Data Purchase url'),
        (GLATIDDINGS_DATA_PURCHASE_URL, 'Glatiddings-sub Data Purchase url'),
        (MASKAWA_SUB_DATA_PURCHASE_URL, 'Maskawa-sub Data Purchase url')
        # Add more choices as needed
    ]

    api = models.CharField(max_length=255, null=True, choices=API_NAME_CHOICES)
    network = models.CharField(max_length=255, null=True, choices=NETWORK_TYPE_CHOICES)
    purchase_url = models.CharField(max_length=255, null=True, choices=PURCHASE_DATA__URL_CHOICES)
    token = models.CharField(max_length=255, blank=True, null=True)



class CableAPISetting(models.Model):
    VTPASS = 'VT-Pass'
    GONGOZ_CONCEPT = 'gongoz-concept'
    MASKAWA_SUB = 'maskawa-sub'
    HUSMO_DATA = 'hosmo-data'
    SIM_HOSTING = 'sim-hosting'
    GLATIDDINGS_DATA = 'gladtiddings-data'


    API_NAME_CHOICES = [
        (VTPASS, 'VT-Pass API Endpoint'),
        (GONGOZ_CONCEPT, 'Gongoz-concept API Endpoint'),
        (MASKAWA_SUB, 'Masakawa-sub API Endpoint'),
        (HUSMO_DATA, 'Hosmo-data API Endpoint'),
        (SIM_HOSTING, 'Sim-Hosting API Endpoint'),
        (GLATIDDINGS_DATA, 'Glatiddings-data API Endpoint')
        # Add more choices as needed
    ]


    VTPASS_DSTV_PLANS = 'https://api-service.vtpass.com/api/service-variations?serviceID=dstv'
    VTPASS_STARTIMES_PLANS = 'https://api-service.vtpass.com/api/service-variations?serviceID=startimes'
    VTPASS_GOTV_PLANS = 'https://api-service.vtpass.com/api/service-variations?serviceID=gotv'
    VTPASS_SHOWMAX_PLANS = 'https://api-service.vtpass.com/api/service-variations?serviceID=showmax'
    GONGOZ_CONCEPT_CABLE_PLANS_URL = 'https://www.gongozconcept.com/api/user/'
    MASKAWA_SUB_CABLE_PLANS_URL = 'https://maskawasubapi.com/api/users/'
    HUSMO_DATA_CABLE_PLANS_URL = 'https://husmodata.com/api/users/'
    GLATIDDINGS_DATA_CABLE_PLANS_URL = 'https://www.gladtidingsdata.com/api/user/'




    CABLE_PLANS_URL_CHOICES = [
        (VTPASS_DSTV_PLANS, 'VT-Pass dstv cable plans url'),
        (VTPASS_STARTIMES_PLANS, 'VT-Pass startime cable plans url'),
        (VTPASS_GOTV_PLANS, 'VT-Pass gotv cable plans url'),
        (VTPASS_SHOWMAX_PLANS, 'VT-Pass showmax plans url'), 
        (GONGOZ_CONCEPT_CABLE_PLANS_URL, 'Gongoz-concept cable plans url'),
        (HUSMO_DATA_CABLE_PLANS_URL, 'Hosmo-data cable plans url'),
        (GLATIDDINGS_DATA_CABLE_PLANS_URL, 'Glatiddings-sub cable plans url'),
        (MASKAWA_SUB_CABLE_PLANS_URL, 'Maskawa-sub cable plans url')
        # Add more choices as needed
    ]

    DSTV = 'DSTV'
    STARTIMES = 'StarTimes'
    GOTV = 'GOTV'
    SHOWAX = 'SHow Max'


    CABLE_CHOICES = [
        (DSTV, 'DSTV Plans'),
        (STARTIMES, 'StarTimes Plans'),
        (GOTV, 'GOTV Plans'),
        (SHOWAX, 'Showmax Plans'),
        # Add more choices as needed
    ]


    VTPASS_CABLE_PURCHASE_URL = 'https://api-service.vtpass.com/api/pay/'
    GONGOZ_CONCEPT_CABLE_PURCHASE_URL = 'https://www.gongozconcept.com/api/cablesub/'
    MASKAWA_SUB_CABLE_PURCHASE_URL = 'https://maskawasubapi.com/api/cablesub/'
    GLATIDDINGS_CABLE_PURCHASE_URL = 'https://www.gladtidingsdata.com/api/cablesub/'
    HUSMO_DATA_CABLE_PURCHASE_URL = 'https://husmodata.com/api/cablesub/'





    CABLE_PURCHASE_URL_CHOICES = [
        (VTPASS_CABLE_PURCHASE_URL, 'VT-Pass cable Purchase url'),
        (GONGOZ_CONCEPT_CABLE_PURCHASE_URL, 'Gongoz-concept cable Purchase url'),
        (HUSMO_DATA_CABLE_PURCHASE_URL, 'Hosmo-data cable Purchase url'),
        (GLATIDDINGS_CABLE_PURCHASE_URL, 'Glatiddings-sub cable Purchase url'),
        (MASKAWA_SUB_CABLE_PURCHASE_URL, 'Maskawa-sub cable Purchase url')
        # Add more choices as needed
    ]


    VTPASS_VALIDATE_CABLE_URL = 'https://api-service.vtpass.com/api/merchant-verify'
    GONGOZ_CONCEPT_VALIDATE_CABLE_URL = 'https://www.gongozconcept.com/api/validate_iuc'
    MASKAWA_SUB_VALIDATE_CABLE_URL = 'https://maskawasubapi.com/api/validate_iuc'
    GLATIDDINGS_VALIDATE_CABLE_URL = 'https://www.gladtidingsdata.com/ajax/validate_iuc'
    HUSMO_DATA_VALIDATE_CABLE_URL = 'https://husmodata.com/api/validate_iuc'





    ELECTRICITY_VALIDATE_URL_CHOICES = [
        (VTPASS_VALIDATE_CABLE_URL, 'VT-Pass electyricity validate url'),
        (GONGOZ_CONCEPT_VALIDATE_CABLE_URL, 'Gongoz-concept electricity validate url'),
        (HUSMO_DATA_VALIDATE_CABLE_URL, 'Hosmo-data electricity validate url'),
        (GLATIDDINGS_VALIDATE_CABLE_URL, 'Glatiddings-sub electricity validate url'),
        (MASKAWA_SUB_VALIDATE_CABLE_URL, 'Maskawa-sub electricity validate url')
        # Add more choices as needed
    ]

    purchase_url = models.CharField(max_length=255, null=True, choices=CABLE_PURCHASE_URL_CHOICES)
    plans_url = models.CharField(max_length=255, null=True, choices=CABLE_PLANS_URL_CHOICES)
    validate_url = models.CharField(max_length=255, null=True, choices=ELECTRICITY_VALIDATE_URL_CHOICES)
    cable = models.CharField(max_length=255, null=True, choices=CABLE_CHOICES)
    api_name = models.CharField(max_length=255, null=True, choices=API_NAME_CHOICES)
    token = models.CharField(max_length=255, blank=True, null=True)





class ElectricityAPISetting(models.Model):
    VTPASS = 'VT-Pass'
    GONGOZ_CONCEPT = 'gongoz-concept'
    MASKAWA_SUB = 'maskawa-sub'
    HUSMO_DATA = 'hosmo-data'
    SIM_HOSTING = 'sim-hosting'
    GLATIDDINGS_DATA = 'gladtiddings-data'


    API_NAME_CHOICES = [
        (VTPASS, 'VT-Pass API Endpoint'),
        (GONGOZ_CONCEPT, 'Gongoz-concept API Endpoint'),
        (MASKAWA_SUB, 'Masakawa-sub API Endpoint'),
        (HUSMO_DATA, 'Hosmo-data API Endpoint'),
        (SIM_HOSTING, 'Sim-Hosting API Endpoint'),
        (GLATIDDINGS_DATA, 'Glatiddings-data API Endpoint')
        # Add more choices as needed
    ]

    VTPASS_ELECTRICITY_PURCHASE_URL = 'https://api-service.vtpass.com/api/pay/'
    GONGOZ_CONCEPT_ELECTRICITY_PURCHASE_URL = 'https://www.gongozconcept.com/api/billpayment/'
    MASKAWA_SUB_ELECTRICITY_PURCHASE_URL = 'https://maskawasubapi.com/api/billpayment/'
    GLATIDDINGS_ELECTRICITY_PURCHASE_URL = 'https://www.gladtidingsdata.com/api/billpayment/'
    HUSMO_DATA_ELECTRICITY_PURCHASE_URL = 'https://husmodata.com/api/billpayment/'





    ELECTRICITY_PURCHASE_URL_CHOICES = [
        (VTPASS_ELECTRICITY_PURCHASE_URL, 'VT-Pass electyricity Purchase url'),
        (GONGOZ_CONCEPT_ELECTRICITY_PURCHASE_URL, 'Gongoz-concept electricity Purchase url'),
        (HUSMO_DATA_ELECTRICITY_PURCHASE_URL, 'Hosmo-data electricity Purchase url'),
        (GLATIDDINGS_ELECTRICITY_PURCHASE_URL, 'Glatiddings-sub electricity Purchase url'),
        (MASKAWA_SUB_ELECTRICITY_PURCHASE_URL, 'Maskawa-sub electricity Purchase url')
        # Add more choices as needed
    ]


    VTPASS_VALIDATE_ELECTRICITY_URL = 'https://api-service.vtpass.com/api/merchant-verify'
    GONGOZ_CONCEPT_VALIDATE_ELECTRICITY_URL = 'https://www.gongozconcept.com/api/validate_meter_number'
    MASKAWA_SUB_VALIDATE_ELECTRICITY_URL = 'https://maskawasubapi.com/api/validate_meter_number'
    GLATIDDINGS_VALIDATE_ELECTRICITY_URL = 'https://www.gladtidingsdata.com/ajax/validate_meter_number'
    HUSMO_DATA_VALIDATE_ELECTRICITY_URL = 'https://husmodata.com/api/validate_meter_number'





    ELECTRICITY_VALIDATE_URL_CHOICES = [
        (VTPASS_VALIDATE_ELECTRICITY_URL, 'VT-Pass electyricity validate url'),
        (GONGOZ_CONCEPT_VALIDATE_ELECTRICITY_URL, 'Gongoz-concept electricity validate url'),
        (HUSMO_DATA_VALIDATE_ELECTRICITY_URL, 'Hosmo-data electricity validate url'),
        (GLATIDDINGS_VALIDATE_ELECTRICITY_URL, 'Glatiddings-sub electricity validate url'),
        (MASKAWA_SUB_VALIDATE_ELECTRICITY_URL, 'Maskawa-sub electricity validate url')
        # Add more choices as needed
    ]


    api_name = models.CharField(max_length=255, null=True, choices=API_NAME_CHOICES)
    purchase_url = models.CharField(max_length=255, null=True, choices=ELECTRICITY_PURCHASE_URL_CHOICES)
    validate_url = models.CharField(max_length=255, null=True, choices=ELECTRICITY_VALIDATE_URL_CHOICES)
    token = models.CharField(max_length=255, blank=True, null=True)




class DataPlan(models.Model):

    PLAN_TYPES = [
        ('CORPORATE', 'Corporate'),
        ('SME', 'SME'),
        ('GIFTING', 'Gifting'),
        # Add more plan types as needed
    ]

    NETWORK_CHOICES = [
        (1, 'MTN'),
        (2, 'GLO'),
        (3, '9MOBILE'),
        (4, 'AIRTEL'),
        # Add more networks as needed
    ]

    plan_type = models.CharField(max_length=50, choices=PLAN_TYPES)
    network = models.CharField(max_length=50, choices=NETWORK_CHOICES)
    data_size = models.CharField(max_length=20)
    price = models.CharField(max_length=20)
    validity_period = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.network} - {self.plan_type} ({self.data_size})'
    


class CablePlan(models.Model):
    # Define choices for the 'cable' field
    CABLE_CHOICES = [
        ('GOTV', 'GOTV'),
        ('DSTV', 'DSTV'),
        ('STARTIME', 'STARTIME'),
        # Add more choices as needed
    ]

    cableplan_id = models.CharField(max_length=50, unique=True)
    cable = models.CharField(max_length=50, choices=CABLE_CHOICES)
    package = models.CharField(max_length=100)
    plan_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.get_cable_display()} - {self.package}"


