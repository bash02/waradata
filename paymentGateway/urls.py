from django.urls import path
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('users_virtual_accounts', views.ViewUserAccouts, basename='user-accounts')
router.register('transactions', views.TransactionViewSet, basename='transactions')
router.register('create_reserve_account', views.CreateReserveAccountView, basename='create-reserve-account')
router.register('transaction_webhook', views.TrasanctionWebhookView, basename='transaction-webhook')
router.register('banks', views.BanksViewSet, basename='banks')
router.register('validate_account_number', views.ValidateAccountNumberViewSet, basename='validate-account-number')
router.register('notification', views.NotificationViewSet, basename='notification')
router.register('transfer_to_wallet', views.WalletTransferViewSet, basename='transfer-to-wallet')
router.register('funding_disbursement', views.DisbursementViewSet, basename='disbursement')
router.register('webhook_disbursement', views.WebhookDisbursementView, basename='disbursement-webohook')
router.register('funding_refund', views.RefundViewSet, basename='refund')
router.register('refund_webhook', views.WebhookRefundView, basename='refund-webhook')
router.register('initialize_transaction_for_future_save', views.InitializeTransacionForFutureSaveView, basename='initialize-transaction')
router.register('fund_with_cart', views.FunWalletWithCardView, basename='fund-with-cart')
router.register('saving_with_cart', views.FutureSavingWithCardView, basename='saving-with-cart')
router.register('saving', views.SavingViewSet, basename='saving')
router.register('view_saving', views.ViewSaving, basename='view-saving')
router.register('validate_saving_withdraw', views.ValidateWithDrawSaving, basename='validate-withdraw-funding')
router.register('disburse_from_saving_wallet', views.DisbursementFromSavingWalletHandlerViewSet, basename='disburse-from-saving-wallet')
router.register('refund_from_saving_wallet', views.RefundFromSavingWalletViewSet, basename='refund-from-saving-wallet')
urlpatterns = router.urls