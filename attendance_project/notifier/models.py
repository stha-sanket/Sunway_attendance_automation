# notifier/models.py
from django.db import models

class Attachment(models.Model):
    file = models.FileField(upload_to='attachments/')  # Store files in 'attachments/' directory inside MEDIA_ROOT
    name = models.CharField(max_length=255, blank=True, null=True)  # Store the name of the file, can be blank/null

    def __str__(self):
        return self.name if self.name else self.file.name  # Return the name or the file name if name is not provided

    def save(self, *args, **kwargs):
        if self.file:  # Ensure there's a file uploaded before trying to extract the name
            self.name = self.file.name
        super().save(*args, **kwargs) # Call the "real" save() method.