# x-seed

Requirement:
1. docker
2. docker-compose

Go into the root dir of this project and run:
```
run-services.sh
```

Open browser tab and connect to:
```
http://127.0.0.1:8888/
```

Here you can get messages that are pushed to the machine
from the queues message and the classification result

Open browser tab and connect to:
```
http://127.0.0.1:8888/sm?content=<your_message_content>
```

The classifier will return Good for 'a' or 'b', Bad for any other message
```
http://127.0.0.1:8888/sm?content=a
http://127.0.0.1:8888/sm?content=b
http://127.0.0.1:8888/sm?content=other
```
