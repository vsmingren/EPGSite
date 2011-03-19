from django.db import models
        
class Program(models.Model):
    title = models.CharField(max_length=50)
    channel = models.CharField(max_length=50)
    starttime = models.DateTimeField()
    stoptime = models.DateTimeField()
    type = models.IntegerField()
    description = models.CharField(max_length=2000)
    
    def __unicode__(self):
        return self.title



