from django.db import models

import uuid

from .choices import StatusChoices

# Create your models here.

class BaseModel(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=StatusChoices, default=StatusChoices.ACTIVE)
    
    class Meta:
        abstract = True
    
    
# class BaseModelWithSlug(BaseModel):
#     # slug = AutoSlugField(populate_from=generate_user_organization_slug, unique=True)
#     class Meta:
#         abstract = True

