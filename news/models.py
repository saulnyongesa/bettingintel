from django.db import models

class NewsArticle(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField(unique=True) # Prevent duplicates
    image_url = models.URLField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    published_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=50, default='Pulse Sports')

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title