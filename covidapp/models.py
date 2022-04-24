from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone


# Create your models here.
class Suggestion(models.Model):
    suggestion = models.CharField(max_length = 400, default='',blank='true', null='true', verbose_name='Suggestions/Comments(if any)')
    email = models.EmailField(unique='true', verbose_name='Your Email', error_messages={'unique':"You have already reviewed. Thank you for the review!"})
    rating = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)], default=1,)
    date_posted = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date_posted']

    def __str__(self):
        return f"{self.email}, Rating : {self.rating}"