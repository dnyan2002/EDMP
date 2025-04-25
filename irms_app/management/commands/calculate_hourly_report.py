from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.timezone import localtime
from datetime import timedelta
from irms_app.models import PIDData, LocalData, FeedstockCost, PowerCost, BiogasPlantReport
from django.core.exceptions import ObjectDoesNotExist

class Command(BaseCommand):
    help = 'Calculates and stores the hourly Biogas Plant Report'

    def handle(self, *args, **kwargs):
        self.stdout.write("⏳ Starting hourly biogas plant report calculation...")

        now = timezone.now()
        print(now)
        one_hour_ago = now - timedelta(hours=23)
        print("One Hour Ago:", one_hour_ago)

        # Handle latest cost entries safely
        try:
            feed_cost = FeedstockCost.objects.latest('date_recorded')
            self.stdout.write(f"✔ Feedstock cost found: ₹{feed_cost.cost_per_ton}/ton")
        except ObjectDoesNotExist:
            self.stdout.write(self.style.WARNING("⚠ No FeedstockCost entry found. Skipping report."))
            return

        try:
            power_cost = PowerCost.objects.latest('date_recorded')
            self.stdout.write(f"✔ Power cost found: ₹{power_cost.cost_per_unit}/kWh")
        except ObjectDoesNotExist:
            self.stdout.write(self.style.WARNING("⚠ No PowerCost entry found. Skipping report."))
            return

        # Fetch data from last hour
        pid_data = PIDData.objects.filter(created_at__range=(one_hour_ago, now))
        print(pid_data)
        # local_data = LocalData.objects.filter(created_at__range=(one_hour_ago, now))
        # print(local_data)

        if not pid_data.exists():
            self.stdout.write(self.style.WARNING('⚠ No PIDData found for the past hour. Skipping report.'))
            return

        # if not local_data.exists():
        #     self.stdout.write(self.style.WARNING('⚠ No LocalData found for the past hour. Skipping report.'))
        #     return

        self.stdout.write("✔ Data for past hour retrieved. Starting calculations...")
        from django.db.models import Sum

        aggregates = pid_data.aggregate(
            raw_biogas=Sum('gas_flowmeter1'),
            clean_gas=Sum('gas_flowmeter2')
        )

        raw_biogas = aggregates['raw_biogas'] or 0.0
        clean_gas = aggregates['clean_gas'] or 0.0

        print("Raw Biogas:", raw_biogas)
        print("Clean Gas:", clean_gas)

        methane_content = 55.0  # Fixed value for now
        expected_clean_gas = raw_biogas * (methane_content / 100)
        purification_loss = expected_clean_gas - clean_gas
        purification_loss_percent = (purification_loss / expected_clean_gas) * 100 if expected_clean_gas else 0

        feedstock_used = 5.0  # Placeholder
        total_feed_cost = feedstock_used * float(feed_cost.cost_per_ton)

        expected_cbg = expected_clean_gas * 0.75
        actual_cbg = expected_cbg - (expected_cbg * 0.08)
        methane_loss = expected_cbg - actual_cbg
        methane_loss_percent = (methane_loss / expected_cbg) * 100 if expected_cbg else 0

        # power_used = local_data.aggregate_power()  # Custom method
        total_power_cost = 1000 * float(power_cost.cost_per_unit)

        self.stdout.write("📊 Aggregated data and calculated required values. Saving report...")

        # Save the report
        BiogasPlantReport.objects.create(
            date=now.date(),
            feedstock_used_ton=feedstock_used,
            feedstock_cost_per_ton=feed_cost.cost_per_ton,
            total_feed_cost=total_feed_cost,
            raw_biogas_produced_nm3=raw_biogas,
            methane_content_percent=methane_content,
            expected_clean_gas_nm3=expected_clean_gas,
            actual_clean_gas_nm3=clean_gas,
            purification_loss_nm3=purification_loss,
            purification_loss_percent=purification_loss_percent,
            expected_production_kg=expected_cbg,
            actual_cbg_production_kg=actual_cbg,
            methane_loss_kg=methane_loss,
            methane_loss_percent=methane_loss_percent,
            gas_purity_percent=methane_content,
            power_consumption_kwh=1000,
            power_cost_per_unit=power_cost.cost_per_unit,
            total_power_cost=total_power_cost,
            co2_savings_mt=0.0,
            fom_bag_count=0,
            cbg_sale_dispatch_ton=0,
            running_time=timedelta(minutes=55),
            stoppage_time=timedelta(minutes=5)
        )

        self.stdout.write(self.style.SUCCESS('✅ Hourly report successfully stored.'))
