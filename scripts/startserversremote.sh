#!/bin/bash

function servers-start
	{

	# NOTE a second galilserver process will appear when something connects to
	# it, like rts2 or fw-gui. It creates a fork for clients
	# Dont panic if you see two galilserver processes
	# Starts galilserver and puts the pid in file galil-pid.txt on bigartn
	echo "#### START-SERVERS: Starting galilserver on 10.30.1.1"
	ssh rts2obs@10.30.1.1 "nohup /usr/local/bin/galilserver > /dev/null 2>&1 &"
	if [ $? -ne 0 ]; then
  		printf '\033[31m FAILED \033[0m\n'
  		exit 1
	fi

	sleep 1

	# Start rts2
	echo "#### START-SERVERS: Starting rts2"
	sudo /usr/local/bin/rts2-start 

	sleep 1

	# Start the website for rts2 Scott
	# does not need sudo or nohup
	echo "#### START-SERVERS: Starting website"
	nohup /home/scott/git-clones/ARTN_RTS2_Proj/rts2www/__init__.py > /dev/null 2>&1 & 

	sleep 1

	# start the azcam monitor
	#if [ "`ping -c 1 10.30.1.10`" ]
	#then
	#		  echo azcam comnputer  is alive.  starting monitor
	#		  	sshpass -p "azcam" ssh azcam@10.30.1.10 "python c:\azcam\azcam-monitor\azcam_monitor\azcammonitor.py -configfile "/azcam/azcam-mont4k/bin/parameters_mont4k_monitor.ini"" &
	#			  else
	#				  	    echo azcam computer is dead
	#fi



	}

function servers-stop
	{
	
	# Want to run it from bigartn
	# kill galilserver and start it if killed
	echo "#### START-SERVERS: Killing galilserver on 10.30.1.1"
	ssh rts2obs@10.30.1.1 "killall -9 galilserver"
	if [ $? -ne 0 ]; then
  		printf '\033[31m FAILED \033[0m\n'
	fi

	sleep 1

	# Stopping rts2
	echo "#### START-SERVERS: Stopping rts2"
	sudo /usr/local/bin/rts2-stop
	if [ $? -ne 0 ]; then
  		printf '\033[31m FAILED \033[0m\n'
	fi

	sleep 1

	# Stop the website if it exists
	echo "#### START-SERVERS: Stopping website"
	pkill -f /home/scott/git-clones/ARTN_RTS2_Proj/rts2www/__init__.py
	if [ $? -ne 0 ]; then
  		printf '\033[31m FAILED \033[0m\n'
	fi

	sleep 1
	#stop the azcam monitor
	#pkill -f "sshpass -p zzzzz ssh azcam@10.30.1.10"
	#sleep 1
	}

function servers-restart
	{
	servers-stop
	sleep 1
	servers-start
	}

POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -s|--start)
	    echo "####  START-SERVERS: START CALLED ####"
    servers-start
    echo "OK"
    sleep 1
    exit
    ;;
    -k|--kill)
	    echo "####  START-SERVERS: KILL CALLED ####"
    servers-stop
    echo "OK"
    sleep 1
    exit
    ;;
    -r|--restart)
	    echo "####  START-SERVERS: RESTART CALLED ####"
    servers-restart
    echo "OK"
    sleep 1
    exit
    ;;
esac
done

echo "####  START-SERVERS: RESTART CALLED ####"
servers-restart
sleep 1
