Hi!

This is Paxos, mostly written by me. Framework was based on a previous project I had a partner for,
but we were given a B, the group disband, and there was some rewriting so the vast majority of it is my code 
at this point.

It's meant to be run through multiple terminals on the same network OR with docker images. I've done both.

When the program is executed, it creates .txt files containing the log, schedule, and dictionary. 

To run this you need to run the command "python pax.py name_of_host", 
where every available name is in the host.txt file along side the associated
port number to that name.

Remember to add the name you desire to your computer's host files. 
It will give an error otherwise.

The one word commands are as follows:

empty line: error
exit: quits application
debug: flips debug variable
view: gives view of schedule
myview: gives view of schedule that hostname has planned
log: gives log
mv: prints dictionary
checkpoint: gives saved event list
leader: tells you if this host is the last to commit

To put an event in the schedule:

schedule name_of_event day start end participants

day should be in month/day/year format and will always give format it as 10/chosen day/2018

start and end should be in 00:00 format using military time.

participants should be in the form of a comma seperated list like so:

ben,abby,ken,phoebe

An example of this command would be:

schedule practice 08:00 14:00 paul,george,john

To cancel an event:

cancel name_of_event


There was a heavy emphasis on checkpointing and fault tolerance. it should checkpoint every 5 events (schedules and cancels) 
and will only schedule events if half or more hosts are online and communicating. UDP protocal was used.
