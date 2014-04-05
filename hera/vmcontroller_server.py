import uuid

from hera import vmcontroller

def spawn(request):
    return str(uuid.uuid4())
