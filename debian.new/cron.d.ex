#
# Regular cron jobs for the amigu package
#
0 4	* * *	root	[ -x /usr/bin/amigu_maintenance ] && /usr/bin/amigu_maintenance
