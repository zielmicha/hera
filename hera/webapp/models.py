from django.db import models
from hera import models as hera_models
import jsonfield

class TerminalRequest(models.Model):
    vm = models.ForeignKey(hera_models.VM)
    streams = jsonfield.JSONField()
