from django.db import models
from django.utils import timezone
from common.models import ProofModel


class KPIMaster(models.Model):
    class Perspective(models.TextChoices):
        FINANCE = 'FINANCE', '💰 Finance'
        CUSTOMER = 'CUSTOMER', '🎯 Customer'
        PROCESS = 'PROCESS', '⚙️ Process'
        LEARNING = 'LEARNING', '📚 Learning & Growth'
        BEHAVIORAL = 'BEHAVIORAL', '🤝 Behavioral'

    code = models.CharField(max_length=50, unique=True)
    perspective = models.CharField(max_length=30, choices=Perspective.choices)
    name = models.CharField(max_length=150)
    weight = models.DecimalField(max_digits=4, decimal_places=1)
    smart_target = models.TextField()

    class Meta:
        ordering = ['perspective', 'name']

    def __str__(self):
        return f"[{self.get_perspective_display()}] {self.name}"


class CustomWorkLog(ProofModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date_performed = models.DateField(default=timezone.localdate)
    hours_spent = models.DecimalField(max_digits=4, decimal_places=1, default=1.0)
    primary_kpi = models.ForeignKey(
        KPIMaster,
        on_delete=models.PROTECT,
        related_name='primary_work_logs',
        help_text="Primary KPI this entry fulfills (captures Perspective + Name)"
    )
    additional_kpis = models.ManyToManyField(
        KPIMaster,
        blank=True,
        related_name='secondary_work_logs'
    )
    impact_result = models.TextField(help_text="Measurable outcome achieved")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_performed', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.date_performed})"
