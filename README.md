# serverless-observatory
A zappa project for scoring output of threatresponse serverless profilers.


# Deploying from docker

> This is required because you can not push the OS X version of pycrypto into lambda.
Everything will break.  Don't do it.

1. Run the build.sh script to build the container
2. Run the aliased command `docker run -ti -e AWS_PROFILE=$AWS_PROFILE -v $(pwd):/var/task -v ~/.aws/:/root/.aws  --rm zappa-deploy bash`
3. Inside of docker

```
   pip install pip --upgrade
   pip install virtualenv --upgrade
   virtualenv -p /usr/bin/python27 venv27
   . venv27/bin/activate
   pip install -r requirements.txt
   zappa update
```
