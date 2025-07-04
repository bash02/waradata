# Generated by Django 5.0.4 on 2024-05-06 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utilityCart', '0002_rename_buyairtime_airtimetransaction_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plan_type', models.CharField(choices=[('CORPORATE', 'Corporate'), ('SME', 'SME'), ('GIFTING', 'Gifting')], max_length=50)),
                ('network', models.IntegerField(choices=[(1, 'MTN'), (2, 'GLO'), (3, '9MOBILE'), (4, 'AIRTEL')])),
                ('data_size', models.CharField(max_length=20)),
                ('price', models.CharField(max_length=20)),
                ('validity_period', models.CharField(max_length=20)),
            ],
        ),
        migrations.AlterField(
            model_name='airtimeapisetting',
            name='token',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='cableapisetting',
            name='api_name',
            field=models.CharField(choices=[('VTPass', 'VTPass Cable plan'), ('gongoz', 'Maskawa Cable plans'), ('maskawa', 'Maskawa Cable plans')], max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='cableapisetting',
            name='api_url',
            field=models.CharField(choices=[('https://api-service.vtpass.com/api/service-variations?serviceID=dstv', 'VTPass DSTV url Plans'), ('https://api-service.vtpass.com/api/service-variations?serviceID=startimes', 'VTPass StarTimes url Plans'), ('https://api-service.vtpass.com/api/service-variations?serviceID=gotv', 'VTPass GOTV url Plans'), ('https://api-service.vtpass.com/api/service-variations?serviceID=showmax', 'VTPass ShowMax url Plans'), ('https://www.gongozconcept.com/api/user/', 'Gongoz url'), ('https://www.gongozconcept.com/api/user/', 'Maskawa url')], max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='cableapisetting',
            name='cable',
            field=models.CharField(choices=[('DSTV', 'DSTV Plans'), ('StarTimes', 'StarTimes Plans'), ('GOTV', 'GOTV Plans'), ('SHow Max', 'Showmax Plans')], max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='cableapisetting',
            name='token',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='dataapisetting',
            name='api_name',
            field=models.CharField(choices=[('VTPass', 'VTPass API Endpoint'), ('GonGoz', 'Gongoz API Endpoint'), ('....', '.........'), ('...', '.........'), ('.....', '.........'), ('hosmodata', 'Hosmodata url')], max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='dataapisetting',
            name='api_url',
            field=models.CharField(choices=[('https://api-service.vtpass.com/api/service-variations?serviceID=mtn-data', 'VTPass mtn data url'), ('https://api-service.vtpass.com/api/service-variations?serviceID=airtel-data', 'VTPass airtel data url'), ('https://api-service.vtpass.com/api/service-variations?serviceID=glo-data', 'VTPass glo data url'), ('https://api-service.vtpass.com/api/service-variations?serviceID=etisalat-data', 'VTPass 9-mobile data url'), ('https://api-service.vtpass.com/api/service-variations?serviceID=etisalat-sme-data', 'VTPass 9-mobile sme data url'), ('https://api-service.vtpass.com/api/service-variations?serviceID=smile-direct', 'VTPass smile data url'), ('https://api-service.vtpass.com/api/service-variations?serviceID=spectranet', 'VTPass spectranet data url'), ('https://www.gongozconcept.com/api/user/', 'Gongoz url'), ('https://www.gongozconcept.com/api/user/', 'Hosmodata url'), ('https://www.gongozconcept.com/api/user/', 'Maskawa url')], max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='dataapisetting',
            name='network',
            field=models.CharField(choices=[('MTN', 'MTN'), ('Glo', 'Glo'), ('Airtel', 'Airtel'), ('Smile', 'Smile'), ('9Mobile', '9Mobile'), ('9Mobile SME', '9Mobile SME'), ('Spectranet', 'Spectranet')], max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='dataapisetting',
            name='plan_type',
            field=models.CharField(choices=[('ALL', 'All plans'), ('SME', 'SME Plans'), ('GIFTING', 'Gifting Plans'), ('CORPORATE', 'CORPORATE Plans')], max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='dataapisetting',
            name='token',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='electricityapisetting',
            name='token',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
