from django.db import models
from django.contrib.auth.models import User

import pytz

class Beer(models.Model):

    beer_text = models.CharField('Beer',max_length=30)
    beer_type = models.CharField('Beer Type',blank=True,max_length=50)
    brewer = models.ManyToManyField(User,'Brewer/s',blank=True)

    brew_date = models.DateField('Brew Date',blank=True,null=True)
    bottle_date = models.DateField('Bottle Date',blank=True,null=True)
    pull_date = models.DateField('Pull Date',blank=True,null=True)

    brew_sg = models.DecimalField('Brew SG', max_digits=4,
                                  decimal_places=3,blank=True,null=True)
    bottle_sg = models.DecimalField('Bottle SG', max_digits=4,
                                    decimal_places=3,blank=True,null=True)
    max_abv = models.DecimalField('Max ABV', max_digits = 3,
                                  decimal_places=2,blank=True,null=True)
    brew_temp = models.DecimalField('Brew Temp',max_digits=3,
                                    decimal_places=1,blank=True,null=True)
    bottle_temp = models.DecimalField('Bottle Temp',max_digits=3,
                                    decimal_places=1,blank=True,null=True)

    light_amb_mod = models.CharField('Ambient Light Modifier',blank=True,max_length=20)
    pres_beer_mod = models.CharField('Beer Pressure Modifier',blank=True,max_length=20)
    temp_amb_mod = models.CharField('Ambient Temp Modifier',blank=True,max_length=20)
    temp_beer_mod = models.CharField('Beer Temp Modifier',blank=True,max_length=20)
    
    brew_notes = models.TextField('Brew Notes',blank=True)
    bottle_notes = models.TextField('Bottle Notes',blank=True)
    other_notes = models.TextField('Other Notes',blank=True)
    
    sugar_amount = models.CharField('Sugar Amount',blank=True,max_length=30)
    bottle_count = models.PositiveSmallIntegerField('Bottle Count',blank=True,
                                                    null=True)

    def __str__(self):
        return self.beer_text

    def save(self, *args, **kwargs):
        super(Beer, self).save(*args, **kwargs)
        if bool(self.brew_sg) and bool(self.bottle_sg):
            brew_sg = float(self.brew_sg)
            bottle_sg = float(self.bottle_sg)
            if bool(self.brew_temp):
                brew_temp = float(self.brew_temp)
                brew_sg += (0.000172414 * brew_temp - 0.0104828)
            if bool(self.bottle_temp):
                bottle_temp = float(self.bottle_temp)
                bottle_sg += (0.000172414 * bottle_temp - 0.0104828)
            if bool(False):
                max_abv = 131*(brew_sg-bottle_sg)
            else:
                max_abv = ((76.08*(brew_sg-bottle_sg)/(1.775-brew_sg))*(bottle_sg/0.794))
            self.max_abv = max_abv
        else:
            self.max_abv = None
        super(Beer, self).save(*args, **kwargs)

    def get_light_amb_mod(self):
        val = self.light_amb_mod
        out = parseList(val,'str')
        return out

    def get_pres_beer_mod(self):
        val = self.pres_beer_mod
        out = parseList(val,'str')
        return out

    def get_temp_amb_mod(self):
        val = self.temp_amb_mod
        out = parseList(val,'str')
        return out

    def get_temp_beer_mod(self):
        val = self.temp_beer_mod
        out = parseList(val,'str')
        return out

class Archive(models.Model):

    beer = models.ForeignKey(Beer)
    reading_date = models.DateField('Reading Date',db_index=True)
    instant_actual = models.TextField('Instant Actual')

    light_amb = models.TextField('Ambient Light')
    pres_beer = models.TextField('Beer Pressure')
    temp_amb = models.TextField('Ambient Temp')
    temp_beer = models.TextField('Beer Temp')

    light_amb_orig = models.TextField('Original Ambient Light')
    pres_beer_orig = models.TextField('Original Beer Pressure')
    temp_amb_orig = models.TextField('Original Ambient Temp')
    temp_beer_orig = models.TextField('Original Beer Temp')

    event_temp_amb = models.TextField('Amb Temp Events')
    event_temp_beer = models.TextField('Beer Temp Events')

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
        out = parseList(val,'str')
        return out

    def get_light_amb(self):
        val = self.light_amb
        out = parseList(val,'float')
        return out

    def get_pres_beer(self):
        val = self.pres_beer
        out = parseList(val,'float')
        return out

    def get_temp_amb(self):
        val = self.temp_amb
        out = parseList(val,'float')
        return out

    def get_temp_beer(self):
        val = self.temp_beer
        out = parseList(val,'float')
        return out

    def get_event_temp_beer(self):
        val = self.event_temp_beer
        out = parseList(val,'float')
        return out

    def get_event_temp_amb(self):
        val = self.event_temp_amb
        out = parseList(val,'float')
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

def parseList(val,form=None):
    if bool(val):
        out = val.split('^')
        del out[-1]
        if form == 'str':
            out = [str(n) for n in out]
        elif form == 'float':
            out = [(float(n) if bool(n) else None) for n in out]
        else:
            out = [n for n in out]
    else:
        out = None
    return out

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
    version = models.PositiveIntegerField('Version', default=0)

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

    light_amb_orig = models.DecimalField('Original Ambient Light', max_digits=5,
                                    decimal_places=2,blank=True,null=False,
                                    default=0)
    pres_beer_orig = models.DecimalField('Original Beer Pressure', max_digits=5,
                                   decimal_places=2,blank=True,null=False,
                                   default=0)
    temp_amb_orig = models.DecimalField('Original Ambient Temp',max_digits=5,
                                   decimal_places=2,blank=True,null=False,
                                    default=0)
    temp_beer_orig = models.DecimalField('Original Beer Temp',max_digits=5,
                                    decimal_places=2,blank=True,null=False,
                                    default=0)

    error_flag = models.NullBooleanField('Error?')
    error_details = models.CharField('Error Details',blank=True,max_length=150)
    event_temp_amb = models.ForeignKey('Event',null=True,blank=True,related_name='reading_to_temp_amb')
    event_temp_beer = models.ForeignKey('Event',null=True,blank=True,related_name='reading_to_temp_beer')

    def __str__(self):
        fmt = '%Y-%m-%d %H:%M:%S %Z%z'
        cst = pytz.timezone('America/Chicago')
        time = self.instant_actual.astimezone(cst).strftime(fmt)
        name = str(self.beer) + ' - ' + str(time)
        return name

    def save(self, *args, **kwargs):
        super(Reading, self).save(*args, **kwargs)
        if bool(self.instant_override):
            self.instant_actual = self.instant_override
        else:
            self.instant_actual = self.instant
        self.instant_actual_iso = self.instant_actual.isoformat()
        self.version += 1
        super(Reading, self).save(*args, **kwargs)

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

    def get_light_amb(self):
        value = self.light_amb
        return float(value)

    def get_pres_beer(self):
        value = self.pres_beer
        return float(value)

    #Break out conversion into a new function, combine with get_temp_beer
    def get_temp_amb_orig(self):
        if self.temp_unit is 'F' or self.temp_unit is None:
            return float(self.temp_amb_orig)
        else:
            return float(self.temp_amb_orig*9/5+32)

    #Break out conversion into a new function, combine with get_temp_amb
    def get_temp_beer_orig(self):
        if self.temp_unit is 'F' or self.temp_unit is None:
            return float(self.temp_beer_orig)
        else:
            return float(self.temp_beer_orig*9/5+32)

    def get_light_amb_orig(self):
        value = self.light_amb_orig
        return float(value)

    def get_pres_beer_orig(self):
        value = self.pres_beer_orig
        return float(value)

    def get_version(self):
        value = self.version
        return str(value)

    def get_unique_ident(self):
        value = str(self.get_instant_actual()) + '|' + str(self.get_version())
        return value

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
    temp_beer_dev = models.DecimalField('Beer Temp Deviation', max_digits=5,
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

    def save(self, *args, **kwargs):
        import monitor.do as do
        super(Config, self).save(*args, **kwargs)
        active_beer = self.beer
        reading_key = do.genReadingKey(active_beer)
        archive_key = do.genArchiveKey(active_beer)
        self.reading_key = reading_key
        self.archive_key = archive_key
        super(Config, self).save(*args, **kwargs)

class Event(models.Model):

    cat_choices = (
        ('Bounds','Bounds'),
        ('Missing','Missing'),
    )
    cat_sensors = (
        ('temp_amb','temp_amb'),
        ('temp_beer','temp_beer'),
    )

    beer = models.ForeignKey(Beer)
    reading = models.ForeignKey(Reading,null=True,blank=True,related_name='event_to_reading')
    instant = models.DateTimeField('Instant',auto_now_add=True)
    category = models.CharField('Category',max_length=50,
                                choices=cat_choices)
    sensor = models.CharField('Sensor',max_length=50,
                              choices=cat_sensors,blank=True,null=True)
    details = models.CharField('Error Details',blank=True,max_length=150)

    def __str__(self):
        fmt = '%Y-%m-%d %H:%M:%S %Z%z'
        cst = pytz.timezone('America/Chicago')
        time = self.instant.astimezone(cst).strftime(fmt)
        name = str(self.beer) + ' - ' + str(self.category) + ' - ' + str(time)
        return name
