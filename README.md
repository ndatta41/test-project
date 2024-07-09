# test-project
## How to run
- Clone the repository
- Go to the root of the repository
- Type: ```docker-compose up --build```

3 container will be available in case of successful running.
### To see the logs
- Get the container id of producer and consumer using command ```docker ps```
- For producer: ```docker logs -f <producer container id>```
- For consumer: ```docker logs -f <consumer container id>```
