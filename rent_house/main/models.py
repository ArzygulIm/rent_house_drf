from django.db import models
from django.contrib.auth.models import User

class House(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rooms = models.IntegerField()
    floors = models.IntegerField()
    floor = models.IntegerField()
    is_booked = models.BooleanField(default=False)
    img = models.ImageField(upload_to='houses/', null=True, blank=True)

    class Meta:
        verbose_name = "Дом"
        verbose_name_plural = "Дома"

    def __str__(self):
        return self.name


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.user.username} booked {self.house.name}"

    class Meta:
        verbose_name = "Бронь"
        verbose_name_plural = "Броня"
