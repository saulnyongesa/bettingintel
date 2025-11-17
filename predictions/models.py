from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.db.models import Count


class League(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    # Add this line below:
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(f"{self.country}-{self.name}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.country} - {self.name}"

class Source(models.Model):
    """Tracks the accuracy of the websites you scrape."""
    name = models.CharField(max_length=100)
    url = models.URLField()
    accuracy_score = models.FloatField(default=0.0)  # Percentage (0-100)

    def __str__(self):
        return self.name


class Match(models.Model):
    STATUS_CHOICES = (('scheduled', 'Scheduled'), ('finished', 'Finished'))

    league = models.ForeignKey(League, on_delete=models.CASCADE)
    home_team = models.CharField(max_length=100)
    away_team = models.CharField(max_length=100)
    start_time = models.DateTimeField(db_index=True)  # Indexed for speed
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')

    class Meta:
        ordering = ['start_time']
        unique_together = ('home_team', 'away_team', 'start_time')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.home_team}-vs-{self.away_team}-{self.start_time.strftime('%Y-%m-%d')}")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('match_detail', kwargs={'slug': self.slug})

    # --- THE ADSENSE VALUE GENERATOR ---
    def get_consensus_data(self):
        """Returns the percentage of votes for Home, Draw, Away based on scraped tips."""
        tips = self.tips.all()
        total = tips.count()
        if total == 0:
            return None

        counts = tips.values('prediction').annotate(c=Count('prediction'))
        data = {'1': 0, 'X': 0, '2': 0}

        for item in counts:
            data[item['prediction']] = (item['c'] / total) * 100

        return data


class Tip(models.Model):
    PREDICTION_CHOICES = (('1', 'Home'), ('X', 'Draw'), ('2', 'Away'))

    match = models.ForeignKey(Match, related_name='tips', on_delete=models.CASCADE)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    prediction = models.CharField(max_length=5, choices=PREDICTION_CHOICES)
    analysis_text = models.TextField(blank=True, null=True)  # Short unique text

    def __str__(self):
        return f"{self.match} - {self.prediction}"