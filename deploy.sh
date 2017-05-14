export AWS_PROFILE=default
docker build . -t zappa-deploy
alias zappashell='docker run -ti -e AWS_PROFILE=$AWS_PROFILE -v $(pwd):/var/task -v ~/.aws/:/root/.aws  --rm zappa-deploy bash'
