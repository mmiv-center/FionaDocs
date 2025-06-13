sh/heartbeat.sh
===============


create a heart beat for the storescp
One way it can fail is if multiple associations are requested.
If the timeout happens the connection will be unusable afterwards.
Here we simply use echoscu to test the connection and if that
fails we will kill a running storescp (hoping that monit will start it again).

In order to activate put this into the crontab of processing (every minute)
*/1 * * * * /usr/bin/nice -n 3 /var/www/html/server/bin/heartbeat.sh


read in the configuration file
