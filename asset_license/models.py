from django.db import models
from django.utils import timezone
from common.models import ProofModel


class AssetUser(models.Model):
    """
    Employees or internal assignees allocated company hardware assets.
    """
    full_name = models.CharField(max_length=150, unique=True)
    email = models.EmailField(blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['full_name']

    def __str__(self):
        return self.full_name


class AssetBrand(models.Model):
    """
    Hardware manufacturers (e.g., Apple, Dell, Lenovo, HP).
    """
    name = models.CharField(max_length=80, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class AssetModel(models.Model):
    """
    Hardware models categorized under a specific manufacturer brand.
    """
    brand = models.ForeignKey(AssetBrand, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=120)

    class Meta:
        unique_together = ('brand', 'name')
        ordering = ['brand', 'name']

    def __str__(self):
        return f"{self.brand.name} {self.name}"


class HardwareAsset(ProofModel):
    """
    Normalized IT hardware asset inventory tracking specifications,
    lifecycle status, deployment history, and proof audit records.
    """
    class AssetStatus(models.TextChoices):
        WORKING = 'WORKING', 'Working Perfectly'
        MANAGED_FAULT = 'MANAGED_FAULT', 'Has Faults But Being Managed'
        KEPT_FOR_REPAIR = 'KEPT_FOR_REPAIR', 'Kept for Repair'
        IN_REPAIR = 'IN_REPAIR', 'In Repair'
        SCRAPPED = 'SCRAPPED', 'Scrapped / Obsolete'

    class AssetType(models.TextChoices):
        LAPTOP = 'LAPTOP', 'Laptop'
        DESKTOP = 'DESKTOP', 'Desktop / Workstation'
        SERVER = 'SERVER', 'Server / Appliance'
        MONITOR = 'MONITOR', 'Monitor / Display'
        OTHER = 'OTHER', 'Other Accessory'

    tag_id = models.CharField(max_length=50, unique=True)
    serial_number = models.CharField(max_length=100, unique=True)
    asset_type = models.CharField(max_length=20, choices=AssetType.choices, default=AssetType.LAPTOP)

    brand = models.ForeignKey(AssetBrand, on_delete=models.PROTECT, related_name='assets')
    model = models.ForeignKey(AssetModel, on_delete=models.PROTECT, related_name='assets')
    current_user = models.ForeignKey(
        AssetUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_assets'
    )

    processor = models.CharField(max_length=100)
    ram_gb = models.PositiveIntegerField()
    storage_type = models.CharField(max_length=50, default='SSD')
    storage_capacity = models.CharField(max_length=50)  # e.g., 512GB, 1TB

    status = models.CharField(max_length=30, choices=AssetStatus.choices, default=AssetStatus.WORKING)
    status_details = models.TextField(blank=True, null=True)
    date_bought = models.DateField(null=True, blank=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    last_info_updated_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        self.last_info_updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.tag_id}] {self.brand.name} {self.model.name} ({self.serial_number})"


class AssetAssignmentHistory(models.Model):
    """
    Lifecycle log tracking user assignments, handover dates, and returns.
    """
    asset = models.ForeignKey(HardwareAsset, on_delete=models.CASCADE, related_name='assignment_history')
    user = models.ForeignKey(AssetUser, on_delete=models.CASCADE, related_name='asset_history')
    assigned_date = models.DateField(default=timezone.localdate)
    returned_date = models.DateField(null=True, blank=True)
    notes = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-assigned_date']

    def __str__(self):
        return f"{self.asset.tag_id} -> {self.user.full_name} ({self.assigned_date})"


class SoftwareLicense(ProofModel):
    """
    Software and SaaS license tracker monitoring renewal deadlines,
    annual spend, optimization strategies, and active subscriptions.
    """
    software_name = models.CharField(max_length=120)
    vendor = models.CharField(max_length=120)
    annual_cost_usd = models.DecimalField(max_digits=12, decimal_places=2)
    renewal_date = models.DateField()
    is_active = models.BooleanField(default=True)
    optimization_plan = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['renewal_date']

    def __str__(self):
        return f"{self.software_name} ({self.vendor}) - ${self.annual_cost_usd}/yr"
