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

class History(models.Model):
    programid = models.ForeignKey(Program)
    # duration = models.IntegerField() # duration time informed that if the program is prefered by the user
    like = models.IntegerField()
    
    def __unicode__(self):
        return '%d %s %s' % (self.like, self.programid.id, self.programid.title)

