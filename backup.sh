#!/bin/bash

# Simple backup script using borg and borgmatic
# This script is intended to be run by cron every hour or so
#
# It checks if the there was not a sucessful backup too soon
# and if the backup server is available, before starting a backup
# with borgmatic


BORG_REPO=backup@vm-borg-server:dell
last_backup=/var/run/borg-backup/last-backup
backup_interval=7200 # min interval in seconds between backups


# check if there was a backup made soon

if [ ! -f $last_backup ] ; then
	if [ ! -d $(dirname $last_backup) ] ; then
		if ! mkdir -p $(dirname $last_backup) ; then
			logger -t backup -p local0.error "Can not create $(dirname $last_backup)"
			exit 2
		fi
	fi
else
	last=$(cat $last_backup)
	now=$(date +%s)
	ago=$((now - last))
	if [[ $ago -lt $backup_interval ]] ; then
		logger -t backup -p local0.info "Last backup was too soon - $ago seconds ago. Skipping."
		exit 0
	fi
fi

# check if backup server is accessible

remote_host=${BORG_REPO%:*}
server_version=$(ssh $remote_host info --version)
if [ ! $? ] ; then
	logger -t backup -p local0.info "Backup server is not accessible"
	exit 0
fi

# run backup
logger -t backup -p local0.info "Stating backup at $(date)"

borgmatic

ret=$?
logger -t backup -p local0.info "Backup ended with $ret at $(date)"
if [ $ret == 0 ] ; then
	date +%s > $last_backup
fi


