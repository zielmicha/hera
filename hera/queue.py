from concurrent.futures import ThreadPoolExecutor
from hera import models
from hera import settings
from hera import errors
from hera import util

import collections
import threading
import time
import requests
import logging

VmCreationRequest = collections.namedtuple('VmCreationRequest',
                                           'owner stats res_id')

def create_vm_object(request, response):
    vm = models.VM(
        stats=request.stats,
        creator=models.Account.objects.get(name=request.owner),
        vm_id=response[0],
        address=','.join(map(str, response[1:])))
    vm.save()
    return vm.vm_id

class Task:
    def __init__(self, created, request, params):
        self.request = request
        self.created = created
        self.params = params

    @property
    def current_priority(self):
        return self.params['priority'] + self.params['priority_growth'] * (time.time() - self.created)

    def finish(self, response):
        logging.info('finish!')
        vm_id = create_vm_object(self.request, response)
        models.QueuedCreation.objects.get(resource=self.request.res_id).delete()
        logging.info('submitting webhook to %s', self.params['webhook_url'])
        # TODO: retry the webhook and do this asynchronously
        resp = requests.post(self.params['webhook_url'], data={'id': vm_id, 'secret': self.params['webhook_secret']})
        logging.info('webhook returned %d', resp.status_code)

class CreateQueue:
    ''' Queue of creation requests '''
    def __init__(self):
        self.create_executor = ThreadPoolExecutor(max_workers=32)
        self.tasks = []
        self.lock = threading.Lock()
        self.init()

    def init(self):
        for creation in models.QueuedCreation.objects.all():
            req = VmCreationRequest(creation.owner.name, creation.stats, creation.resource.id)
            self.tasks.append(
                Task(created=util.datetime_to_unix(creation.created),
                     request=req,
                     params=creation.params))

    def queue(self, request, params):
        if len(self.tasks) > settings.QUEUE_LIMIT:
            raise errors.QueueFull()

        models.QueuedCreation(owner=models.Account.objects.get(name=request.owner),
                              stats=request.stats,
                              resource=models.DerivativeResource.objects.get(id=request.res_id),
                              params=params).save()
        self.tasks.append(Task(time.time(), request, params))

    def maybe_unqueue(self, spawner):
        # TODO: this may be too expensive if queue is really big
        with self.lock:
            tasks = list(self.tasks)
            tasks.sort(key=lambda k: -k.current_priority)

            for task in tasks:
                if spawner.check_estimates(task.request):
                    logging.info('submitting queued task %s', task.request)
                    self._submit(spawner, task)
                    self.tasks.remove(task)
                    break

    def start(self):
        pass

    def _requeue(self, task):
        self.tasks.append(task)

    def _submit(self, spawner, task):
        def execute():
            try:
                response = spawner.create_vm_if_possible(task.request)
                logging.info('sandbox created (response=%s)', response)
                if not response:
                    self._requeue(task)
                else:
                    task.finish(response)
            except:
                logging.exception('create vm from queue')
                raise

        self.create_executor.submit(execute).add_done_callback(lambda val: None)
