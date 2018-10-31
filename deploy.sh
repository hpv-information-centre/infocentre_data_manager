#!/bin/bash

# $REMOTE_SEVER -> Remote server to deploy app
# $REMOTE_USER 	-> Username to login to remote server
# $REMOTE_PATH 	-> Remote path to django apps/projects
# $APP_NAME 	-> App name
# $REFNAME		-> Refname of the commit to deploy

rsync -avrz --delete --exclude '.*/' ./ $REMOTE_USER@$REMOTE_SERVER:$REMOTE_PATH/$APP_NAME/

ssh $REMOTE_USER@$REMOTE_SERVER "
  python3 $REMOTE_PATH/$APP_NAME/setup.py sdist;
  echo \$(ls -t $REMOTE_PATH/$APP_NAME/dist/)
  pip3 install -U --user $REMOTE_PATH/$APP_NAME/dist/\$(ls -t $REMOTE_PATH/$APP_NAME/dist/);
  sudo service apache2 reload;
"
