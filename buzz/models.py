from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.db.utils import DatabaseError

from buzz.helpers import slugifyUniquely


#Choices
PREVIOUS_PRODUCT_COMMENTS = (
                                 (0,'No'),
                                 (1,'Yes'),
                                 (2,'Unknown'),
                            )

UPDATE_RATE = (
                  (0, 'Never'),
                  (1, 'Yearly'),
                  (2, 'Monthly'),
                  (3, 'Daily'),
                  (4, 'Hourly'),
                  (5, 'Unknown'),
              )

FEEDBACK_TYPES = (
                     (0, 'Very bad'),
                     (1, 'Bad'),
                     (2, 'Neutral'),
                     (3, 'Good'),
                     (4, 'Very good'),
                 )

#user profile related
class UserProfile(models.Model):
    user = models.OneToOneField(User)

    def __str__(self):
        return "%s's profile" % self.user

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        try:
            UserProfile.objects.get_or_create(user=instance)
        except DatabaseError:
            #skipping pre-south error
            pass

post_save.connect(create_user_profile, sender=User)


#manager for soft deletion
class EnabledManager(models.Manager):
    def get_query_set(self):
        query_set = super(self.__class__, self).get_query_set()
        return query_set.filter(disabled=False, duplicate_of=None)


class SoftDeletableModel(models.Model):
    objects = models.Manager()
    enabled = EnabledManager()

    class Meta:
        abstract = True


#sluggifier
class SluggedModel(SoftDeletableModel):
    def save(self):
        if not self.id:
            self.slug = slugifyUniquely(self.name, self.__class__)

        models.Model.save(self)

    class Meta:
        abstract = True


#models
class Product(SluggedModel):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    creation_date = models.DateTimeField(auto_now_add=True)
    creation_user = models.ForeignKey(User, null=True, blank=True)
    disabled = models.BooleanField(default=False)

    def save_model(self, request, obj, form, change):
        obj.creation_user = request.user
        obj.save()

    def __unicode__(self):
        return self.name


class ReportType(SluggedModel):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class Country(SluggedModel):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

    class Meta():
        verbose_name_plural = "Countries"


class File(SluggedModel):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    creation_date = models.DateTimeField(auto_now_add=True)
    creation_user = models.ForeignKey(User, null=True, blank=True)
    disabled = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class Source(SluggedModel):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    creation_date = models.DateTimeField(auto_now_add=True)
    creation_user = models.ForeignKey(User, null=True, blank=True)
    disabled = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class MentionType(SluggedModel):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    creation_date = models.DateTimeField(auto_now_add=True)
    creation_user = models.ForeignKey(User, null=True, blank=True)
    disabled = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class AuthorExpertise(SoftDeletableModel):
    name = models.CharField(max_length=100)
    creation_date = models.DateTimeField(auto_now_add=True)
    creation_user = models.ForeignKey(User, null=True, blank=True)
    disabled = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class Mention(SoftDeletableModel):
    creation_user = models.ForeignKey(User, related_name="creator", null=True,
                                      blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update_user = models.ForeignKey(User, related_name="updater")
    last_update_date = models.DateTimeField(auto_now=True)
    disabled = models.BooleanField(default=False)

    link = models.URLField()
    text = models.TextField()
    origin = models.ForeignKey(Source)
    type = models.ForeignKey(MentionType)
    author_expertise = models.ForeignKey(AuthorExpertise)
    feedback = models.IntegerField(max_length=1, choices=FEEDBACK_TYPES)
    previous_product_comments = models.IntegerField(max_length=1,
        choices=PREVIOUS_PRODUCT_COMMENTS)
    estimated_audience = models.IntegerField()
    relevant_audience = models.BooleanField()
    update_rate = models.IntegerField(max_length=1, choices=UPDATE_RATE)
    remarks = models.TextField()

    def __unicode__(self):
        return "%s @ %s" %(self.type, self.origin)


class FollowUpStatus(SluggedModel):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

    class Meta():
        verbose_name_plural = "Follow ups statuses"


class FollowUp(SluggedModel):
    creation_date = models.DateTimeField(auto_now_add=True)
    creation_user = models.ForeignKey(User, null=True, blank=True)
    status = models.ForeignKey(FollowUpStatus)
    disabled = models.BooleanField(default=False)
    mention = models.ForeignKey(Mention)
    remarks = models.TextField()

    def __unicode__(self):
        return self.name


class Report(SoftDeletableModel):
    name = models.CharField(max_length=100)
    creation_user = models.ForeignKey(User, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    report_type = models.ForeignKey(ReportType)

    def __unicode__(self):
        return self.name