# storage/templates/models.py
from django.db import models

class Template(models.Model):
    TEMPLATE_TYPES = [
        ('pdf', 'PDF Document'),
        ('png', 'PNG Image'),
        ('svg', 'SVG Vector Image'),
    ]
    
    name = models.TextField()
    version = models.TextField()
    type = models.CharField(max_length=10, choices=TEMPLATE_TYPES, default='pdf')

    def __str__(self):
        return self.name

class Page(models.Model):
    UNIT_CHOICES = [
        ('mm', 'Millimeters'),
        ('px', 'Pixels'),
    ]
    
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='pages')
    name = models.TextField()
    html = models.TextField()
    width = models.IntegerField()
    height = models.IntegerField()
    units = models.CharField(max_length=5, choices=UNIT_CHOICES, default='mm')
    bleeds = models.IntegerField(null=True, blank=True)  # Optional for PDF

class PageAsset(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='assets')
    file = models.FileField(upload_to='page_assets/')

class Field(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='fields')
    name = models.TextField()
    label = models.TextField()
    required = models.BooleanField(default=False)

class PageSettings(models.Model):
    """Format-specific settings for pages"""
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='settings')
    key = models.CharField(max_length=50)  # e.g. 'dpi', 'transparency'
    value = models.TextField()
    
    class Meta:
        unique_together = ('page', 'key')

class GeneratedTemplate(models.Model):
    """Renamed from GeneratedPdf to support multiple formats"""
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='generated_templates')
    file = models.FileField(upload_to='generated_templates/')
    format = models.CharField(max_length=10)  # 'pdf', 'png', 'svg'
    created_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(blank=True, null=True)  # Data used to generate the template
    
    def __str__(self):
        return f"{self.format.upper()} для {self.template.name} от {self.created_at.strftime('%d.%m.%Y %H:%M')}"