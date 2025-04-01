# Generated by Django 4.2.6 on 2025-03-29 06:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('irms_app', '0002_localdata_created_at_piddata_created_at_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='piddata',
            options={'verbose_name': 'P&ID Data', 'verbose_name_plural': 'P&ID Data'},
        ),
        migrations.RemoveField(
            model_name='localdata',
            name='value7',
        ),
        migrations.RemoveField(
            model_name='localdata',
            name='value8',
        ),
        migrations.AlterField(
            model_name='connection',
            name='machine_name',
            field=models.CharField(max_length=45),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='equipment_name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='fieldlink',
            name='field_description',
            field=models.CharField(max_length=45),
        ),
        migrations.AlterField(
            model_name='fieldlink',
            name='field_name',
            field=models.CharField(max_length=35),
        ),
        migrations.AlterField(
            model_name='localdata',
            name='value1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='localdata',
            name='value2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='localdata',
            name='value3',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='localdata',
            name='value4',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='localdata',
            name='value5',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='localdata',
            name='value6',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='parameter',
            name='parameter_name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='baloon_plc1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='baloon_plc2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='baloon_plc3',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='crusher1_napier_tph',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='crusher2_napier_tph',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='dt1_circulation_pump1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='dt1_circulation_pump2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='dt1_circulation_pump3',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='dt1_pr_tx_1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='dt1_pr_tx_2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='dt1_pt100_1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='dt1_pt100_2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='feed_pump1_value',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='feed_pump2_value',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='fire_fighting_pump1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='fire_fighting_pump2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='fresh_water_pump1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='fresh_water_pump2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='gas_flowmeter1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='gas_flowmeter2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='heat_pump1_value',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='heat_pump2_value',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='heat_pump3_value',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='hot_water_pump1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='hot_water_pump2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='level_switch1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='level_switch2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='mixer1_value',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='mixer2_value',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='pt_circulation_pump_value',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='pt_digester_feed_pump1_value',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='pt_digester_feed_pump2_value',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='pt_digester_feed_pump3_value',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='pt_level_switch1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='pt_level_switch2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='pt_sealing_pump1_value',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='pt_sealing_pump2_value',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='pt_slurry_flowmeter1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='pt_slurry_flowmeter2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='sealing_pump1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='sealing_pump2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='sls_circulation_pump',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='sls_feed_pump1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='sls_feed_pump2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='sls_level_switch1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='sls_level_switch2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='sls_slurry_flowmeter',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='water_flow_meter1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='water_flow_meter2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='water_pump1_value',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='piddata',
            name='water_pump2_value',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plant',
            name='plant_name',
            field=models.CharField(max_length=45),
        ),
        migrations.AlterField(
            model_name='section',
            name='section_name',
            field=models.CharField(max_length=50),
        ),
    ]
