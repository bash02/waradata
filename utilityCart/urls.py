from django.urls import path
from django.urls.conf import include
from rest_framework_nested import routers
from . import views


router = routers.DefaultRouter()


router.register('buy_data', views.BuyDataViewSet, basename='buy-data')
router.register('buy_airtime', views.BuyAirtimeViewSet, basename='buy-airtime')
router.register('pay_cable', views.CableSubscriptionView, basename='pay-cable')
router.register('pay_bill', views.BillPaymentView, basename='pay-bill')
router.register('validate_cable', views.ValidateIUC, basename='validate-iuc')
router.register('validate_meter', views.ValidateMeterView, basename='validate-meter')
router.register('validate_smile_email', views.ValidateEmailForSmileDirectViewSet, basename='validate-smile-email')

router.register('dataplans', views.DataPlanView, basename='data-plan')
router.register('cableplans', views.CablePlanView, basename='cable-plan')







urlpatterns = router.urls
