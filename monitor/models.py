from django.db import models

class Beer(models.Model):
    
    beer_text = models.CharField('Beer',max_length=30)
    brew_date = models.DateField('Brew Date',blank=True,null=True)
    bottle_date = models.DateField('Bottle Date',blank=True,null=True)
    
    def __str__(self):
        return self.beer_text
        
class Archive(models.Model):
    
    beer = models.ForeignKey(Beer)
    reading_date = models.DateField('Reading Date',db_index=True)
    instant_actual = models.TextField('Instant Actual')
    light_amb = models.TextField('Ambient Light')
    pres_beer = models.TextField('Beer Pressure')
    temp_amb = models.TextField('Ambient Temp')
    temp_beer = models.TextField('Beer Temp')
    count = models.PositiveIntegerField('Count', default=0)
    update_instant = models.DateTimeField('Last Updated',blank=True,
                                      null=True,default=None)    
    
    def __str__(self):
        value = str(self.beer) + ': '
        value = value + str(self.reading_date.strftime("%Y-%m-%d")) + ' ['
        value = value + str(self.count) + ']'
        return value
    
    def get_instant_actual(self):
        val = self.instant_actual
        if bool(val):
            out = val.split('^')
            del out[-1]
            out = [str(n) for n in out]
        return out     
        
    def get_light_amb(self):
        val = self.light_amb
        if bool(val):
            out = val.split('^')
            del out[-1]
            out = [float(n) for n in out]
        return out

    def get_pres_beer(self):
        val = self.pres_beer
        if bool(val):
            out = val.split('^')
            del out[-1]
            out = [float(n) for n in out]
        return out
        
    def get_temp_amb(self):
        val = self.temp_amb
        if bool(val):
            out = val.split('^')
            del out[-1]
            out = [float(n) for n in out]
        return out
        
    def get_temp_beer(self):
        val = self.temp_beer
        if bool(val):
            out = val.split('^')
            del out[-1]
            out = [float(n) for n in out]
        return out
        
    def get_count(self):
        value = self.count
        return value
    
    def get_update_instant(self):
        value = self.update_instant
        value = value.isoformat()
        return value
    
    def get_reading_date(self):
        value = self.reading_date
        value = value.isoformat()
        return value

    def get_unique_ident(self):
        value = str(self.get_reading_date()) + '|' + str(self.get_update_instant())
        return value        
        
class Reading(models.Model):

    temp_choices = (
        ('F', 'Fahrenheit'),
        ('C', 'Celcius'),
    )

    beer = models.ForeignKey(Beer)
    instant = models.DateTimeField('Instant',auto_now_add=True)
    instant_override = models.DateTimeField('Instant Override',blank=True,
                                            null=True,default=None)
    instant_actual = models.DateTimeField('Instant Actual',blank=True,
                                          null=True,default=None)
    instant_actual_iso = models.SlugField('Instant Actual (ISO)', blank = True,
                                          null=True,default=None,db_index=True)
    version = models.PositiveIntegerField('Version', default=1)                                          
                                          
    light_amb = models.DecimalField('Ambient Light', max_digits=5,
                                    decimal_places=2,blank=True,null=False,
                                    default=0)
    pres_beer = models.DecimalField('Beer Pressure', max_digits=5,
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
    error_details = models.CharField('Error Details',blank=True,max_length=150)
            
    def get_instant_actual(self):
        value = self.instant_actual_iso
        return value
        
    #Break out conversion into a new function, combine with get_temp_beer
    def get_temp_amb(self):
        if self.temp_unit is 'F' or self.temp_unit is None:
            return float(self.temp_amb)
        else:
            return float(self.temp_amb*9/5+32)
    
    #Break out conversion into a new function, combine with get_temp_amb
    def get_temp_beer(self):
        if self.temp_unit is 'F' or self.temp_unit is None:
            return float(self.temp_beer)
        else:
            return float(self.temp_beer*9/5+32)
    
    #Eventually remove the clipping code; this should be handled on the server
    def get_light_amb(self):
        value = self.light_amb
        if value > 200:
            return float(200)
        else:
            return float(self.light_amb)
            
    def get_pres_beer(self):
        value = self.pres_beer
        return float(value)
        
    def get_version(self):
        value = self.version
        return str(value)
    
    def get_unique_ident(self):
        value = str(self.get_instant_actual()) + '|' + str(self.get_version())
        return value  
    
    def __str__(self):
        value = str(self.beer) + ': '    
        value = value + str(self.instant_actual.strftime("%Y-%m-%d %H:%M:%S"))
        return value
        
    def save(self, *args, **kwargs):
              
        super(Reading, self).save(*args, **kwargs)
        
        if bool(self.instant_override):
            self.instant_actual = self.instant_override
        else:
            self.instant_actual = self.instant
        self.instant_actual_iso = self.instant_actual.isoformat()

        self.version += 1

        super(Reading, self).save(*args, **kwargs)

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
                                        
    read_missing = models.PositiveIntegerField('Missing Reading Warning (minutes)',
                                               default=0)
    read_last_instant = models.DateTimeField('Last Reading Instant',blank=True,
                                null=True,default=None)
                                        
    email_enable = models.BooleanField('Enable Email?',default=False)
    email_timeout = models.PositiveIntegerField('Email Timeout (minutes)',
                                                default=60)
    email_api_key = models.CharField("API Key",default='',blank=True,
                                     max_length=50)    
    email_sender = models.CharField("From",default='',blank=True,max_length=50)
    email_to = models.CharField("To",default='',blank=True,max_length=150)
    email_subject = models.CharField("Subject",default='',blank=True,
                                     max_length=150)
    email_last_instant = models.DateTimeField('Last Email Instant',blank=True,
                                null=True,default=None)
    
    api_server_url = models.CharField('Server URL',default='',blank=True,max_length=50)
    api_prod_key = models.CharField('Prod API Key',default='',blank=True,max_length=50)
    api_test_key = models.CharField('Test API Key',default='',blank=True,max_length=50)
    
    reading_key = models.TextField()
    archive_key = models.TextField()
    
    def __str__(self):
        return 'Config' + ': ' + str(self.pk)