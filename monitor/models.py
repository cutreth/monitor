from django.db import models

class Beer(models.Model):
    
    beer_text = models.CharField('Beer',max_length=30)
    brew_date = models.DateField('Brew Date',blank=True,null=True)
    bottle_date = models.DateField('Bottle Date',blank=True,null=True)
    
    def __str__(self):
        return self.beer_text
    
class Reading(models.Model):

    temp_choices = (
        ('F', 'Fahrenheit'),
        ('C', 'Celcius'),
    )

    beer = models.ForeignKey(Beer)
    instant = models.DateTimeField('Instant',auto_now_add=True)
    instant_override = models.DateTimeField('Instant Override',blank=True,
                                            null=True,default=None)
    temp_amb = models.DecimalField('Ambient Temp',max_digits=5,
                                   decimal_places=2)
    temp_beer = models.DecimalField('Beer Temp',max_digits=5,
                                    decimal_places=2)
    temp_unit = models.CharField('Temp Unit',max_length=1,
                                 choices=temp_choices,default='F')
    
    def instant_actual(self):
        if self.instant_override is not None:
            return self.instant_override
        else:
            return self.instant
    
    def __str__(self):
        return str(self.beer) + ': ' + \
        str(self.instant_actual().strftime("%Y-%m-%d %H:%M:%S"))

class Config(models.Model):
    
    beer = models.ForeignKey(Beer)
    
    def __str__(self):
        return 'Config' + ': ' + str(self.pk)