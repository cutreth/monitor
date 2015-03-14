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
    light_amb = models.DecimalField('Ambient Light', max_digits=5,
                                    decimal_places=2,blank=True,null=False,
                                    default=0)
    temp_amb = models.DecimalField('Ambient Temp',max_digits=5,
                                   decimal_places=2,blank=True,null=False,
                                    default=0)
    temp_beer = models.DecimalField('Beer Temp',max_digits=5,
                                    decimal_places=2,blank=True,null=False,
                                    default=0)
    temp_unit = models.CharField('Temp Unit',max_length=1,
                                 choices=temp_choices,default='F')
                                 
    error_flag = models.NullBooleanField('Error?')
    error_details = models.SlugField('Error Details',blank=True)
    
    def instant_actual(self):
        if self.instant_override is not None:
            return self.instant_override
        else:
            return self.instant
            
    def get_temp_amb(self):
        if self.temp_unit is 'F':
            return float(self.temp_amb)
        else:
            return float(self.temp_amb*9/5+32)
    
    def get_temp_beer(self):
        if self.temp_unit is 'F':
            return float(self.temp_beer)
        else:
            return float(self.temp_beer*9/5+32)
    
    def __str__(self):
        return str(self.beer) + ': ' + \
        str(self.instant_actual().strftime("%Y-%m-%d %H:%M:%S"))

class Config(models.Model):
    
    beer = models.ForeignKey(Beer)
    temp_amb_base = models.DecimalField('Ambient Temp Baseline', max_digits=5,
                                        decimal_places=2,blank=True,null=True,
                                        default=None)
    temp_amb_dev = models.DecimalField('Ambient Temp Deviation', max_digits=5,
                                       decimal_places=2,blank=True,null=True,
                                       default=None)
    temp_beer_base = models.DecimalField('Beer Temp Baseline', max_digits=5,
                                         decimal_places=2,blank=True,null=True,
                                         default=None)
    temp_beer_dev = models.DecimalField('Ambient Temp Deviation', max_digits=5,
                                        decimal_places=2,blank=True,null=True,
                                        default=None)
    
    def __str__(self):
        return 'Config' + ': ' + str(self.pk)