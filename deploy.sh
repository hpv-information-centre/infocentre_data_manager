#!/bin/bash

# $REMOTE_SEVER -> Remote server to deploy app
# $REMOTE_USER 	-> Username to login to remote server
# $REMOTE_PATH 	-> Remote path to django apps/projects
# $APP_NAME 	-> App name
# $REFNAME		-> Refname of the commit to deploy

rsync -avrz --delete --exclude '.*/' ./ $REMOTE_USER@$REMOTE_SERVER:$REMOTE_PATH/$APP_NAME/

ssh $REMOTE_USER@$REMOTE_SERVER "
  $REMOTE_PATH/$APP_NAME/scripts/install_package.sh;
  sudo service apache2 reload;
"
