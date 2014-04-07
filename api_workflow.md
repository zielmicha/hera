
POST /disk
size=10L
-->
{"status": "ok", "id": 1}

POST /vm
owner=me&memory=128&timeout=10&disk=123
-->
{"status": "ok", "id": "e928c895-aaff-40db-bbdf-3f60aae30da9"}

POST /vm/e928c895-aaff-40db-bbdf-3f60aae30da9/exec
args=["/bin/busybox", "ls", "/"]&chroot=false&stdout=text&stderr=text
-->
{"status": "ok", "stdout": "/bin\n/init", "stderr": null, "code": 0}

POST /vm/e928c895-aaff-40db-bbdf-3f60aae30da9/exec
args=["/bin/busybox", "ls", "/"]&chroot=false&stderr=to_stdout
-->
{"status": "ok", "stdout": "http://proxy.example.com/data/20752019529842"}

POST /vm/e928c895-aaff-40db-bbdf-3f60aae30da9/exec
args=["/bin/busybox", "yes"]&chroot=false&async&stderr=to_stdout
-->
{"status": "ok", "stdout": "http://proxy.example.com/stream/20752019529842"}
