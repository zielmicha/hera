import requests
import json
host = 'http://localhost:8080/'

resp = requests.post(host + 'sandbox/', data={
    'owner': 'foouser',
    'timeout': 15,
    'memory': 128,
    'disk': 'new,10M',
})
resp.raise_for_status()
resp = resp.json()
id = resp['id']
print(id)
resp = requests.post(host + 'sandbox/' + id + '/exec', data={
    'sync': 'true',
    'args': json.dumps(["/bin/busybox", "sh", "-c", "echo hello world; busybox cat /proc/cmdline"]),
    'stderr': 'stdout',
})
resp.raise_for_status()
print(resp.json()['stdout'])
