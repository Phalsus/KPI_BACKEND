from django.db import models
from common.models import ProofModel


class InHouseSystem(ProofModel):
    """
    Tracks internal development projects replacing third-party vendor software.
    Measures annual USD cost savings towards the $30,000 / 3 systems target,
    operational efficiency percentage, and packageability for external sale.
    """
    class DevelopmentStatus(models.TextChoices):
        PLANNING = 'PLANNING', 'Planning & Scoping'
        IN_DEV = 'IN_DEV', 'In Active Development'
        TESTING = 'TESTING', 'Testing / Staging'
        LIVE = 'LIVE', 'Live in Production'

    system_name = models.CharField(max_length=150)
    replaced_vendor_tool = models.CharField(max_length=150, help_text="Third-party tool replaced")
    annual_cost_saved_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    deployment_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=DevelopmentStatus.choices, default=DevelopmentStatus.PLANNING)
    efficiency_pct = models.DecimalField(max_digits=5, decimal_places=2, default=95.00)
    packageable_for_external_sale = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-annual_cost_saved_usd', '-created_at']

    def __str__(self):
        return f"{self.system_name} (Replaces: {self.replaced_vendor_tool}, Saved: ${self.annual_cost_saved_usd})"
