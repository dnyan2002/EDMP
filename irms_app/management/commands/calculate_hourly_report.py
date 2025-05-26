from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.timezone import localtime
from datetime import timedelta
from irms_app.models import PIDData, FeedstockCost, PowerCost, BiogasPlantReport
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
import time

class Command(BaseCommand):
    help = 'Generates hourly Biogas Plant Report every hour if not already created'

    def handle(self, *args, **kwargs):
        self.stdout.write("⏳ Starting hourly biogas report checker...")

        while True:
            now = timezone.now()
            local_now = localtime(now)
            hour_start = local_now.replace(minute=0, second=0, microsecond=0)
            hour_end = hour_start + timedelta(hours=1)

            self.stdout.write(f"\n🕒 Checking for hour: {hour_start} to {hour_end}")

            if BiogasPlantReport.objects.filter(report_time=hour_start).exists():
                self.stdout.write(self.style.NOTICE("📁 Report already exists for this hour. Waiting..."))
            else:
                self.stdout.write("📌 No report for this hour, generating...")
                self.run_report_logic(hour_start, hour_end)

            time.sleep(3600)  # Sleep for an hour (3600 seconds)

    def run_report_logic(self, start_time, end_time):
        try:
            pid_data = PIDData.objects.filter(created_at__range=(start_time, end_time))
            if not pid_data.exists():
                self.stdout.write(self.style.WARNING("⚠ No PIDData found for this hour."))
                return

            feed_cost = FeedstockCost.objects.filter(date_recorded__lte=start_time).latest('date_recorded')
            power_cost = PowerCost.objects.filter(date_recorded__lte=start_time).latest('date_recorded')

            aggregates = pid_data.aggregate(
                raw_biogas=Sum('mass_flow_meter_gas_flow_rate'),
                clean_gas=Sum('mass_flow_meter_gas_flow_total'),
                feedstock_used=Sum('feedstock_input_ton'),
                power_used=Sum('power_consumption_kwh'),
                methane_content=Sum('methane_content_percent'),
                fom_bag_count=Sum('bagging_unit'),
                co2_savings_mt=Sum('analyzer_CO2')
            )

            raw_biogas = aggregates['raw_biogas'] or 0.0
            clean_gas = aggregates['clean_gas'] or 0.0
            feedstock_used = aggregates['feedstock_used'] or 0.0
            power_consumed = aggregates['power_used'] or 0.0
            methane_content = aggregates['methane_content'] or 0.0
            fom_bag_count = aggregates['fom_bag_count'] or 0.0
            co2_savings_mt = aggregates['co2_savings_mt'] or 0.0

            expected_clean_gas = raw_biogas * (methane_content / 100)
            purification_loss = expected_clean_gas - clean_gas
            purification_loss_percent = (purification_loss / expected_clean_gas) * 100 if expected_clean_gas else 0

            total_feed_cost = feedstock_used * float(feed_cost.cost_per_ton)
            total_power_cost = power_consumed * float(power_cost.cost_per_unit)

            expected_cbg = expected_clean_gas * 0.75
            actual_cbg = expected_cbg - (expected_cbg * 0.08)
            methane_loss = expected_cbg - actual_cbg
            methane_loss_percent = (methane_loss / expected_cbg) * 100 if expected_cbg else 0

            BiogasPlantReport.objects.create(
                date=start_time.date(),
                report_time=start_time,
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
                power_consumption_kwh=power_consumed,
                power_cost_per_unit=power_cost.cost_per_unit,
                total_power_cost=total_power_cost,
                co2_savings_mt=co2_savings_mt,
                fom_bag_count=fom_bag_count,
                cbg_sale_dispatch_ton=0.0,
                running_time=timedelta(minutes=55),  # Example estimate
                stoppage_time=timedelta(minutes=5),  # Example estimate
                shift='General Shift'
            )

            self.stdout.write(self.style.SUCCESS("✅ Hourly report saved."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error generating report: {e}"))
