from django.db import models


class ProofModel(models.Model):
    """
    Abstract base model that enforces audit trails, documentation,
    drive links, or email references across all operational records.
    """
    class ProofType(models.TextChoices):
        CLOUD_LINK = 'CLOUD_LINK', 'Cloud Folder / Drive Link'
        EMAIL_REF = 'EMAIL_REF', 'Email Subject / Sender Reference'
        DOC_URL = 'DOC_URL', 'Documentation / Confluence / Wiki URL'
        NOTE = 'NOTE', 'Text Note / Context Summary'

    proof_type = models.CharField(
        max_length=30,
        choices=ProofType.choices,
        default=ProofType.CLOUD_LINK
    )
    proof_reference = models.TextField(
        help_text="URL, email subject header, ticket ID, or note."
    )
    proof_description = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Brief label (e.g., 'Approved by Line Manager', 'Signed Acceptance PDF')"
    )

    class Meta:
        abstract = True
