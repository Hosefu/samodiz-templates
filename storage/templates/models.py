from django.db import models

class Template(models.Model):
    name = models.TextField()
    version = models.TextField()

    def __str__(self):
        return self.name

class Page(models.Model):
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='pages')
    name = models.TextField()
    html = models.TextField()
    width = models.IntegerField()
    height = models.IntegerField()
    bleeds = models.IntegerField()

class PageAsset(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='assets')
    file = models.FileField(upload_to='page_assets/')

class Field(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='fields')
    name = models.TextField()
    label = models.TextField()
    required = models.BooleanField(default=False)