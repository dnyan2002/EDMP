from django.db import models
from django.contrib.auth.models import AbstractUser, Permission, Group

class Role(models.Model):
    role_name = models.CharField(max_length=30, unique=True, verbose_name="Role")
    permissions = models.ManyToManyField(Permission, blank=True, related_name="role_permissions")  # Avoid name conflict

    def __str__(self):
        return self.role_name
    
    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"
        db_table = 'role'

class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=50, verbose_name="Full Name")
    company_name = models.CharField(max_length=70, verbose_name="Company Name")
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, verbose_name="Role", related_name="users")

    groups = models.ManyToManyField(Group, blank=True, related_name="customuser_groups")  # Fix conflict
    user_permissions = models.ManyToManyField(Permission, blank=True, related_name="customuser_permissions")
    status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Inactive', 'Inactive')])

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'users'

    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'user'

class Section(models.Model):
    section_name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Section"
        verbose_name_plural = "Sections"
        db_table = 'section'

class Equipment(models.Model):
    equipment_name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Equipment"
        verbose_name_plural = "Equipments"
        db_table = 'equipment'

class Parameter(models.Model):
    parameter_name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Parameter"
        verbose_name_plural = "Parameters"
        db_table = 'parameter'


class Plant(models.Model):
    plant_id = models.CharField(max_length=50, primary_key=True)
    plant_name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Plant"
        verbose_name_plural = 'plants'
        db_table = 'plant'

class Connection(models.Model):
    machine_name = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    port_no = models.IntegerField()
    status = models.CharField(max_length=50, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    plant_id = models.ForeignKey('Plant', on_delete=models.CASCADE)

    def __str__(self):
        return self.ip_address

    class Meta:
        verbose_name = "Connection"
        verbose_name_plural = "Connections"
        db_table = 'connection'

class FieldLink(models.Model):
    ip_address = models.ForeignKey(Connection, on_delete=models.CASCADE)
    field_name = models.CharField(max_length=255)
    field_description = models.TextField()
    plant_id = models.ForeignKey('Plant', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.ip_address}-{self.field_name}-{self.field_description}"
    class Meta:
        verbose_name = "Field Link"
        verbose_name_plural = "Field Links"
        db_table = 'field_link'


class LocalData(models.Model):
    ip_address = models.ForeignKey(Connection, on_delete=models.CASCADE)
    plant_id = models.ForeignKey(Plant, on_delete=models.CASCADE)
    value1 = models.FloatField()
    value2 = models.FloatField()
    value3 = models.FloatField()
    value4 = models.FloatField()
    value5 = models.FloatField()
    value6 = models.FloatField()
    value7 = models.FloatField()
    value8 = models.FloatField()
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Local Data"
        verbose_name_plural = "Local Data"
        db_table = 'local_data'

class PIDData(models.Model):
    crusher1_napier_tph = models.FloatField()
    crusher2_napier_tph = models.FloatField()
    feed_pump1_value = models.FloatField()
    feed_pump2_value = models.FloatField()
    water_pump1_value = models.FloatField()
    water_pump2_value = models.FloatField()
    fresh_water_pump1 = models.FloatField()
    fresh_water_pump2 = models.FloatField()
    mixer1_value = models.FloatField()
    mixer2_value = models.FloatField()
    level_switch1 = models.FloatField()
    level_switch2 = models.FloatField()
    water_flow_meter1 = models.FloatField()
    water_flow_meter2 = models.FloatField()
    fire_fighting_pump1 = models.FloatField()
    fire_fighting_pump2 = models.FloatField()
    pt_digester_feed_pump1_value = models.FloatField()
    pt_digester_feed_pump2_value = models.FloatField()
    pt_digester_feed_pump3_value = models.FloatField()
    pt_circulation_pump_value = models.FloatField()
    pt_sealing_pump1_value = models.FloatField()
    pt_sealing_pump2_value = models.FloatField()
    pt_level_switch1 = models.FloatField()
    pt_level_switch2 = models.FloatField()
    pt_slurry_flowmeter1 = models.FloatField()
    pt_slurry_flowmeter2 = models.FloatField()
    dt1_circulation_pump1 = models.FloatField()
    dt1_circulation_pump2 = models.FloatField()
    dt1_circulation_pump3 = models.FloatField()
    dt1_pt100_1 = models.FloatField()
    dt1_pt100_2 = models.FloatField()
    dt1_pr_tx_1 = models.FloatField()
    dt1_pr_tx_2 = models.FloatField()
    heat_pump1_value = models.FloatField()
    heat_pump2_value = models.FloatField()
    heat_pump3_value = models.FloatField()
    hot_water_pump1 = models.FloatField()
    hot_water_pump2 = models.FloatField()
    sealing_pump1 = models.FloatField()
    sealing_pump2 = models.FloatField()
    baloon_plc1 = models.FloatField()
    baloon_plc2 = models.FloatField()
    baloon_plc3 = models.FloatField()
    sls_feed_pump1 = models.FloatField()
    sls_feed_pump2 = models.FloatField()
    sls_circulation_pump = models.FloatField()
    sls_level_switch1 = models.FloatField()
    sls_level_switch2 = models.FloatField()
    sls_slurry_flowmeter = models.FloatField()
    gas_flowmeter1 = models.FloatField()
    gas_flowmeter2 = models.FloatField()
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'pid_data'
        verbose_name_plural = 'pid_data'
        db_table = 'pid_data'