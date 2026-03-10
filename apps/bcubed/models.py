from django.conf import settings
from django.db import models


class BcubedResult(models.Model):
    STAGE_CHOICES = [
        ('build', 'Build'),
        ('brand', 'Brand'),
        ('bank', 'Bank'),
    ]

    TOOL_LABELS = {
        'pitch': 'Business Pitch',
        'checklist': 'Startup Checklist',
        'niche': 'Niche Finder',
        'names': 'Business Names',
        'tagline': 'Tagline Creator',
        'copy': 'Marketing Copy',
        'logo': 'Logo Concept',
        'seo': 'SEO Tips',
        'pricing': 'Pricing Advisor',
        'budget': 'Budget Planner',
        'tax': 'Tax Guidance',
        'invoice': 'Invoice Template',
    }

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bcubed_results',
    )
    stage = models.CharField(max_length=10, choices=STAGE_CHOICES)
    tool = models.CharField(max_length=20)
    inputs = models.JSONField()
    result = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def tool_label(self):
        return self.TOOL_LABELS.get(self.tool, self.tool.title())
