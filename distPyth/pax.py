from pathlib import Path
import socket
import threading
import sys
import functools
import json
import time


#leader_flag is a variable for the optimized Paxos
leader_flag = 0
highest_log_num = 0

#debug allows print statements
debug = 1

#exit thread variable
exit_flag = 0

#majority required
majority_var = 0

#lock to ensure no simultaneous clock/dict/log file r/w
mutex = threading.Lock()

#dictionary elements are stored as [name, day, start, end, [participant1,participant2,...]]
dictionary = []

# working_dictionary
w_dict = {}

#log elements are stored as [log number, name, day, start, end, [participant1,participant2,...]]
log = []

#global list of sockets for messaging
prop_sock = []
sockets = []
ipz = []
portz = []
name = ""
globalMyIndex = -1

#number of events in log
number_of_events = 0

# next log spot to be filled
next_log_spot = 0

#json string encoding / decoding for writing data to files
encoder = json.JSONEncoder()
decoder = json.JSONDecoder()

# should be populated by uncancelled meetings
not_cancelled = []

#busy waiter to insert log
busy_log = 0

# my index
ind = -6

# proposer inbox for messages
proposer_inbox = []

# learner inbox for messages
learner_inbox = []

#lets users view latest checkpoint
chp_var = []

# votes
vote_list= []

def update_dict(key, val):
    global w_dict
    if debug:
        print("updating dictionary\n", w_dict)
    w_dict[key] = val
    make_dict_table()

def make_dict_table():
    global w_dict
    keys = list(w_dict.keys())
    val  = list(w_dict.values())
    dict_table = []
    if debug:
        print()
        print("making dictionary list to be written")
        print(w_dict)
        print(keys)
        print(val)

    for x in range(len(w_dict)):
        dict_table.append([keys[x],val[x]])

    writeDict(dict_table)

def writeDict(dict_table):
    if debug:
        print("updating m_v dict")
    mutex.acquire()
    with open(name + "_V_and_M.txt", 'w') as f:
        f.write(encoder.encode(dict_table))
    mutex.release()

def list_to_dic(dict_table):
    global w_dict
#    print("w_dict: ",w_dict)
#    print("dict_table:\n",dict_table)

    for x in range(len(dict_table)):
        w_dict[dict_table[x][0]] = dict_table[x][1]

    if debug:
        print("w_dict looks like this:\n", w_dict)

def exitMessage(msg):
    print("Error: {0}".format(msg))
    sys.exit()

def checkConflict2(message, amCreator):

    global dictionary
    sm = message.split()


    meetingName=sm[1]
    day=sm[2].split("/")[1]
    startTime=sm[3]
    endTime=sm[4]
    participants=sm[5].split(",")



    #if we are the creator we check for conflicts for everyone; otherwise, we only check for conflicts that involve us in both meetings
    for i in range(len(dictionary)):
        timesConflict = (day == dictionary[i][3]) and ((startTime == dictionary[i][4] and endTime == dictionary[i][5]) or ((startTime < dictionary[i][5]) and (endTime > dictionary[i][4])))
        if (not timesConflict):
            continue
        if (amCreator):
            #when we are the creator we care about all conflicts (I think)?
            conflicting = len(set(participants).intersection(dictionary[i][6])) > 0
        else:
            #when we are not the creator we only care about conflicts involving us (I think)?
            conflicting = name in set(participants).intersection(dictionary[i][6])
        if (conflicting):
            return -1
#           return i if (dictionary[i][0] > meetingName) and (not amCreator) else -1
    return -2

def recvall(sock):
    return sock.recv(4096).decode('utf-8')

def receiveMessage(conn):
    return recvall(conn)

def setIpPorts(hostList):
    ipz = []  # list of ips
    portz = []  # list of ports
    for i in range(0, len(hostList), 2):
        if (hostList[i] == name):
            ind = int(i / 2)
            global globalMyIndex
            globalMyIndex = ind
            # print("I am " + hostList[i] + " " + hostList[i+1])
            port = hostList[i + 1]
        ipz.append(hostList[i])
        portz.append(hostList[i + 1])
    return ipz, portz, port, ind

def readFileContents(fileName):
    f = open(fileName, "r")
    if f.mode != 'r':
        exitMessage("file not found")

    text = f.read()
    f.close()

    return text.strip().replace('\n', ' ').split(' ')

def dictLexiComp(a,b):
    #sort by day first
    if a[1] < b[1]:
        return -1
    if (a[1] > b[1]):
        return 1
    #sort by start time next
    if a[2] < b[2]:
        return -1
    if (a[2] > b[2]):
        return 1
    #finally sort by name
    if (a[0] < b[0]):
        return -1
    elif (a[0] > b[0]):
        return 1
    return 0

def listMeetings(justMe = False):
    global dictionary
    #print("TODO: listMeetings: test my output compared to spec output")
    sortedDict = sorted(dictionary,key = functools.cmp_to_key(dictLexiComp))
    for i in sortedDict:
        if ((not justMe) or name in i[6]):
            print("{0} 10/{1}/2018 {2} {3} {4}".format(
                i[2],
                i[3],
                i[4],
                i[5],
                i[6].__str__()[1:-1].replace(' ','').replace("'","")
                ))

def listCheck(justMe = False):
    global chp_var
    #print("TODO: listMeetings: test my output compared to spec output")
    sortedCheck = sorted(chp_var,key = functools.cmp_to_key(dictLexiComp))
    for i in sortedCheck:
        if ((not justMe) or name in i[6]):
            print("{0} 10/{1}/2018 {2} {3} {4}".format(
                i[2],
                i[3],
                i[4],
                i[5],
                i[6].__str__()[1:-1].replace(' ','').replace("'","")
                ))

def findMeetingIndexInDictionary(MeetingName):
    for i in range(len(dictionary)):
        if (dictionary[i][0] == MeetingName):
            return i
    return -1

def listLog():
    #print("TODO: listLog: test my output compared to spec output")
    global log
    log =  sorted(log, key=lambda l: l[0], reverse=False)

    if debug:
        for i in log:
            print("{0} {1} {2} 10/{3}/18 {4} {5} {6}".format(
                i[0],
                i[1],
                i[2],
                i[3],
                i[4],
                i[5],
                i[6].__str__()[1:-1].replace(' ', '').replace("'", "")
                ) if i[1] == "schedule" else "{0} cancel {1}".format(i[0],i[2]))
    else:
        for i in log:
            print("{0} {1} 10/{2}/18 {3} {4} {5}".format(
                i[1],
                i[2],
                i[3],
                i[4],
                i[5],
                i[6].__str__()[1:-1].replace(' ','').replace("'","")
                ) if i[1] == "schedule" else "cancel {0}".format(i[2]))

def copy_into_check():
    global chp_var
    global dictionary

    for x in range(len(chp_var)):
        del(chp_var[0])

    for x in range(len(dictionary)):
        chp_var.append(dictionary[x])

def find_next_log_entry():
    global log
    global next_log_spot
    global highest_log_num
    log =  sorted(log, key=lambda l: l[0], reverse=False)

    i = 0
    if len(log)>0:
        highest_log_num = log[(len(log)-1)][0]
    if debug:
        print()
        print("FINDING LOG ENTRY")
        print("current log:",log)
        print("current next log spot",next_log_spot)
        print("highest log number in log:",highest_log_num)

    w = -1
    while i < (len(log)):
#        print("log:",log[i][0])
#        print("i",i)
        if i != int(log[i][0]):
            w = i
            next_log_spot = i
            if debug:
                print("hole found at", i)
            i = len(log)
        i = i + 1
    if w == -1:
        if debug:
            print("end of log found:", i, "now next log spot")
            next_log_spot = i

    if debug:
        print("value of next log proposal = ", next_log_spot)
        print("END FIND ENTRY")
        print()

def file_check_and_load():
    log_file_name = name+"_log.txt"
    fn = Path(log_file_name)
    # if there is no file and it is first execution
    if fn.exists():  # file exists
        readStableStorage()
    else:
        writeStableStorage(True)

def recovery_1():
    global log
    global dictionary
    global highest_log_num
    global w_dict

    log = sorted(log, key=lambda l: l[0], reverse=False)
    dictionary = sorted(dictionary, key=lambda l: l[0], reverse=False)
    if len(log)!= 0:
        highest_log_entry = log[len(log)-1]

    start = len(log)
    while start%5!=0:
        start = start-1

    if debug:
        print("schedule length:", len(dictionary))
        print("log length:", len(log))
        if len(log) != 0:
            print("highest log entry:", highest_log_entry)

    while start < len(log):
        index = start
        log_entry = log[index]
        print(log_entry)
        if log_entry[1]=="cancel":
#            print("canceling...")
            cancel_meeting(log_entry[2])
        if log_entry[1]=="schedule":
#            print("scheduling...")
            meeting_info = w_dict.get(log_entry[0])[1].split()

            meeting_info.insert(0,index)
            print(meeting_info)
            schedule_meeting(meeting_info)
        start = start+1
    find_next_log_entry()
    proposer_inbox.append([-1, next_log_spot])

def readStableStorage():
    global log
    global dictionary
    global w_dict
    global debug
    global proposer_inbox
    global next_log_spot
    global chp_var

    mutex.acquire()
    with open(name + "_log.txt", 'r') as f:
        log = decoder.decode(f.read())
    with open(name + "_dict.txt", 'r') as f:
        dictionary = decoder.decode(f.read())
    with open(name + "_dict.txt", 'r') as f:
        chp_var = decoder.decode(f.read())
    with open(name + "_V_and_M.txt", 'r') as f:
        dict_table = decoder.decode(f.read())
    print("dict table", dict_table)
    list_to_dic(dict_table)
    if debug:
        print("working_dict\n",w_dict)
        print("log\n",log)
        print("schedule:\n",dictionary)
        print("initiating recovery...")
 #       print("checkpoint:\n",chp_var)
    find_next_log_entry()
    recovery_1()
    mutex.release()

def writeStableStorage(hi):
    global dictionary
    global chp_var
    mutex.acquire()
    if hi==True:
        with open(name + "_log.txt", 'w') as f:
            f.write(encoder.encode(log))
        with open(name + "_dict.txt", 'w') as f:
            f.write(encoder.encode(dictionary))
        copy_into_check()
#        sys.exit()
#    with open(name + "_V_and_M.txt", 'w') as f:
#        w_dict
#        f.write(encoder.encode(w_dict))
    else:
        with open(name + "_log.txt", 'w') as f:
            f.write(encoder.encode(log))

    mutex.release()
    make_dict_table()

def thread_learner(ip, port, ind, ipz, portz):
    global learner_inbox
    global proposer_inbox
    global next_log_spot
    global highest_log_num
    global log
    global chp_var
    if debug:
        print("learner ready")
    var = []
    while var!="exit":
        while len(learner_inbox)==0:
            a = 1
        message = learner_inbox[0]
        if debug:
            print("message", message, "incoming")
        if message[0] == "exit":
            if debug:
                print("exiting learner...")
            sys.exit()
        elif message[0] == "filled":
            if debug:
                print("recovered received!")
            writeStableStorage(False)
            del (learner_inbox[0])

        elif message[0] == "commit":
            if debug:
                print("committing...")
            writeStableStorage(False)
            if (len(log))%5 == 0:
                print("LENGTH OF LOG IS", len(log))
                print("HIGHEST ENTRY IS", highest_log_num)
                find_next_log_entry()
                temp = highest_log_num # suspicious
                if temp == len(log)-1: # suspicious
                    writeStableStorage(True)
                else:
                     proposer_inbox.append([-1,temp])
            del (learner_inbox[0])

        else:
            print("did not understand:",message)

def thread_proposer(ip, port, ind, ipz, portz):
    global proposer_inbox
    if debug:
        print("proposer ready")
    var = []
    while var!="exit":
        while len(proposer_inbox)==0:
            a = 1
        message = proposer_inbox[0]
        if debug:
            print("message", message, "incoming")
        if message[0] == "exit":
            if debug:
                print("exiting proposer!")
            sys.exit()
        else:
            complete = synod(message[0],message[1])
            if complete == 1:
                if debug:
                    print("deleting ", proposer_inbox[0])
                del(proposer_inbox[0])

def thread_acceptor(ip, port, ind, ipz, portz):
    #print("binding to port " + str(port))
    global exit_flag
    global debug
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
    while not exit_flag :
        data = decoder.decode(receiveMessage(sock))
        parse = data[0]

        if debug:
            print("acceptor received: ",parse)

        if (data == None):
            print("received None value from receiveMessage; this probably isn't intended")
            continue
        elif parse == "prepare":
            promise(data,sock)
        elif parse == "accept":
            recv_accept_send_ack(data,sock)
        elif parse == "commit":
            learn_and_checkpoint(data,sock)

    if debug:
        print("exiting acceptor")

def thread_recver_prom(log_num,k):
    global prop_sock
    global vote_list
    print("begin recv")
    start = time.clock()
    end   = time.clock()
    while (end-start) < 2 or error_flag:
        error_flag = 0
        end = time.clock()
        try:
            new_data = decoder.decode(prop_sock[0].recv(4096).decode('utf-8'))
        except socket.timeout:
            error_flag = 1
        if error_flag == 0:
            if new_data[0] == "promise":
                if new_data[1] == log_num:
                    if new_data[3] == k:
                        vote_list.append(new_data)
    print("receiving..and exiting")
    sys.exit()

def thread_recver_accept(log_num,k):
    global prop_sock
    global vote_list
    start = time.clock()
    end   = time.clock()
    while (end-start) < 3 or error_flag:
        error_flag = 0
        end = time.clock()
        try:
            new_data = decoder.decode(prop_sock[0].recv(4096).decode('utf-8'))
        except socket.timeout:
            error_flag = 1
        if error_flag == 0:
            if new_data[0] == "ack":
                if new_data[1] == log_num:
                    if new_data[2] == k:
                        vote_list.append(new_data)
    sys.exit()

def thread_sender(socket ,ip, port, data):
    print("begin send")
    sendToFull(socket, data.encode(), (ip, port))
    print("sending...and exit")
    sys.exit()

def sendToFull(sock, data, addr):
    if debug:
        print("sending this to full:", len(data),data, addr[0],int(addr[1]))

    ret = len(data) - sock.sendto(data, (addr[0],int(addr[1])))
    if ret > 0:
        return sendToFull(sock, data[ret:], (addr[0],int(addr[1])))
    else:
        return None

def send_all(data,ipz,portz,):
    global sockets
    data = encoder.encode(data)  # .encode()
    for i in range(len(ipz)):
        sendToFull(sockets[i], data.encode(), (ipz[i], portz[i]))

def cancel_meeting(event_name):
    global dictionary
    global log
    global not_cancelled

    i = 0
    del_flag = 0
#    print(event_name)
#    print()
    while i < len(dictionary):
#        print(dictionary[i])
#        print(dictionary[i][2])
        if event_name == dictionary[i][2]:
            if debug:
                print("entry",dictionary[i][2],"found")
            del dictionary[i]
            del_flag = 1
        i = i + 1

    if del_flag == 0:
        if debug:
            print("entry not found, adding cancel to list of not cancelled events")
        not_cancelled.append(name)

def schedule_meeting(msg):
    global dictionary
    global not_cancelled


    i = 0
    dontadd_flag = 0
    msg[3] = msg[3].split("/")[1]
    msg[6] = msg[6].split(",")

    if debug:
        print("event being scheduled: ", msg)

    while i < len(not_cancelled):
        if msg[0] == not_cancelled[i]:
            dontadd_flag = 1
            del(not_cancelled[i])
        i = i+1
    if dontadd_flag == 0:
        dictionary.append(msg)

def learn_and_checkpoint(data,sock):

    global w_dict
    global ipz
    global portz
    global ind
    global log
    global busy_log
    global highest_log_num
    global leader_flag
    global learner_inbox

    if debug:
        print()
        print("LEARNING START")
        print("received", data)
    reply = data[1]
    log_number = data[2]
    message = data[3]
    split = message[1].split()
    split.insert(0,log_number)
    log = sorted(log, key=lambda l: l[0], reverse=False)
#    print(log)
    found = 0
    for x in range(len(log)):
        if log[x][0] == split[0]:
            busy_log = 0
            found = 1

    if found == 0:
        update_dict(log_number, message)
        log.append(split)
    else:
        if reply == ind:
            if debug:
                print("duplicate log, ignoring", data )
        return 0

    if split[1] == "cancel":
        if debug:
            print("cancelling meeting: ",split[2] )
        event = split[2]
        cancel_meeting(event)


    if split[1] == "schedule":
        if debug:
            print("scheduling:", split[2])
#        not_or = schedule_meeting(split)
        schedule_meeting(split)

    learner_inbox.append(["commit", log_number])
    if reply == ind:
        if debug:
            print("releasing var")
            print(highest_log_num,log_number)
        if highest_log_num+1 == log_number:
            if debug:
                print("setting leader")
            leader_flag = 1
        busy_log = 0
    else:
        leader_flag = 0

def recv_accept_send_ack(data,sock):

    global w_dict
    global ipz
    global portz
    global ind

    reply_index = data[1]
    m_and_message = data[2]
    log_num = data[3]
    if debug:
        print()
        print("RECEIVE ACCEPTED")
        print("received:",m_and_message, "from", ipz[reply_index], "for log ", log_num)
        print("aka", data)
    ack = []
    old_m_and_msg = w_dict.get(log_num)
    if old_m_and_msg is None:
        update_dict(log_num,m_and_message)
        old_m_and_msg = w_dict.get(log_num)

    if old_m_and_msg[0]<= m_and_message[0]:
        update_dict(log_num,m_and_message)
        ack.append("ack")
        ack.append(log_num)
        ack.append(data[4])
        ack =encoder.encode(ack)
        sendToFull(sock, ack.encode(), (ipz[reply_index], int(portz[reply_index]) + 1))
    else:
        if debug:
            print("message failed to pass m check, refusing to reply")

    if debug:
        print(w_dict)
        print("RECEIVE END")
        print()

def send_accept(m_and_msg, log_num):

    global ind
    global majority_var
    global sockets
    global ipz
    global portz
    global prop_sock
    global leader_flag
    global vote_list

    vote_list = []
    k = 0

    while k < 3:
        data = []
        data.append("accept")
        data.append(ind)
        data.append(m_and_msg)
        data.append(log_num)
        data.append(k)
        data = encoder.encode(data)  # .encode()
        rec_thread = threading.Thread(target=thread_recver_accept, args=(log_num, k,))
        rec_thread.start()
        for i in range(len(sockets)):
            thread = threading.Thread(target=thread_sender, args=(sockets[i], ipz[i], portz[i], data,))
            thread.start()
        start = time.clock()
        end = time.clock()
        while (end - start) < 3:
            end = time.clock()

        if (majority_var <= len(vote_list)):
            k = 8
        else:
            vote_list = []
        k = k + 1

    if debug:
        print("number of votes:", len(vote_list))
        print("votes:\n",vote_list)

    if majority_var <= len(vote_list):
        return 1
    else:
        leader_flag = 0
        return -3

def promise(data,sock):

    global w_dict
    global ipz
    global portz
    global ind
    log_number = (data[3])

    m_val_in_log = []
    m_val_in_log.append(w_dict.get(log_number))
    m_val_to_send = []
    m_val_to_send.append("promise")
    m_val_to_send.append(log_number)

    if debug:
        print()
        print("PROMISE")
        print("received prepare from",ipz[data[1]])
        print("received data:",data)
        print("m value:", m_val_in_log)

    if m_val_in_log[0] is None:
        if debug:
            print("no m val found in",ipz[ind] )
#        w_dict[log_number] = [data[1], -1] #overwrite in dictionary, a1
        update_dict(log_number,[-1, -1])#overwrite in dictionary, a1
        m_val_to_send.append(w_dict[log_number])
        m_val_to_send.append(data[4])
        m_val_to_send = encoder.encode(m_val_to_send)
        sendToFull(sock,m_val_to_send.encode() , (ipz[data[1]], int(portz[data[1]])+1))
    elif m_val_in_log[0][0] >= data[2]:
        if debug:
            print("sent m_val too small, sending nack from",ipz[ind] )
        m_val_to_send.append([m_val_in_log[0][0],"nack"])
        m_val_to_send.append(data[4])
        m_val_to_send = encoder.encode(m_val_to_send)
        sendToFull(sock,m_val_to_send.encode() , (ipz[data[1]], int(portz[data[1]])+1))

    elif m_val_in_log[0][0] < data[2]:
        if debug:
            print("sent m_val is acceptable, sending event from",ipz[ind] )
        m_val = [m_val_in_log[0][0],m_val_in_log[0][1]]# overwrite m, keep v
        w_dict[log_number] = m_val
        m_val_to_send.append(m_val)
        m_val_to_send.append(data[4])
        print(m_val_to_send)
        m_val_to_send = encoder.encode(m_val_to_send)
        sendToFull(sock,m_val_to_send.encode() , (ipz[data[1]], int(portz[data[1]])+1))
        #send promise and message

    if debug:
        print(w_dict)
        print("END PROMISE")
        print()

def prepare_wait_for_promise(m,log_num):

    global next_log_spot
    global ind
    global majority_var
    global sockets
    global ipz
    global portz
    global prop_sock
    global vote_list

    votes_list = []
    data = []
    data.append("prepare")
    data.append(ind)
    data.append(m)
    data.append(log_num)
    prop_sock[0].settimeout(2)
#    for i in range(len(ipz)):
    k = 0


    while k < 3 :
        data = []
        data.append("prepare")
        data.append(ind)
        data.append(m)
        data.append(log_num)
        data.append(k)
        data = encoder.encode(data)  # .encode()
        rec_thread = threading.Thread(target=thread_recver_prom, args=( log_num,k,))
        rec_thread.start()
        for i in range(len(sockets)):
            thread = threading.Thread(target=thread_sender, args=(sockets[i], ipz[i], portz[i], data,))
            thread.start()
        start = time.clock()
        end = time.clock()
        while (end-start)<3:
            end = time.clock()


        if(majority_var <= len(vote_list)):
            k = 8
        else:
            vote_list = []
        k=k+1

    if debug:
        print("number of votes:", len(vote_list))
        print("votes:\n",vote_list)
        print("exiting...")


    if majority_var <= len(vote_list):
        p_msg = sorted(vote_list, key=lambda l: l[2][0], reverse=True) #sort by m, pick largest
        p_msg = p_msg[0]
        if debug:
            print("largest elements sent:\n",p_msg)

        if p_msg[2][1] == "nack":
            if debug:
                print("nack received, try again with higher number")
            return -1, p_msg[2]

        elif p_msg[2][0]<= m and p_msg[2][1] == -1:
            if debug:
                print("msg accepted, continue with synod")
            return 1, [m,p_msg[2][1]]

        elif p_msg[2][0]<= m:
            if debug:
                print("m_value accepted, but other message already accepted.")
            return -2, [m,p_msg[2][1]]


    else:
#        print("Too many servers down, could not add to log, try again.")
        return -3, [-3,-3]

def commit(log_num, message):

    global ind
    global majority_var
    global sockets
    global ipz
    global portz
    global prop_sock

    data = []
    data.append("commit")
    data.append(ind)
    data.append(log_num)
    data.append(message)
    data = encoder.encode(data)  # .encode()

    for i in range(len(ipz)):
        sendToFull(sockets[i], data.encode(), (ipz[i], portz[i]))

def catch_all_logic(message, m_and_msg):

    global log
    global learner_inbox
    cancel_flag = 0

    if message == -1:
        if debug:
            print("recovered.")
        learner_inbox.append(["filled", 0])
        return -3

    if m_and_msg[1] != -1:
        print("ERROR, SHOULD BE -1, BUT IS: ", m_and_msg[1])
        return -3

    quick_split = message.split()
#    print("split :",quick_split)
#    print("length of log: ", len(log))
    if quick_split[0] == "schedule":
        conflict_check = checkConflict2(message, 1)
        if debug:
            print("CONFLICT METER ", conflict_check)
        if conflict_check != -2:
#            print("could not schedule meeting")
            if debug:
                print("Schedule conflict")
            return -3
    if quick_split[0] == "cancel":
        for x in range(len(log)):
            print(log[x])
            if log[x][2] == quick_split[1]:
                cancel_flag = 1

        for x in range(len(log)):
            if log[x][1] == quick_split[0] and log[x][2] == quick_split[1]:
                cancel_flag = -1

        if cancel_flag == 0:
            if debug:
                print("Event does not exist, cannot cancel.")
            return -3
        if cancel_flag == -1:
            if debug:
                print("Event already cancelled.")
            return -3

    if debug:
        print("event gets passed filters, continues to accept phase")
    return 1

def synod(message,log_num):

    global leader_flag
    global ind
    global next_log_spot
    global busy_log
    global learner_inbox

    if debug:
        print()
        print("SYNOD")

    if leader_flag == 1: # am leader
        m_and_msg = [0,-1]
        catch = catch_all_logic(message, m_and_msg)
        if catch == -3:
            if debug:
                print("Can't schedule, conflict.")
            split = message.split()
            if split[0] == "schedule":
                print("Unable to schedule meeting",split[1])
                return 1
            if split[0] == "cancel":
                print("Unable to cancel meeting", split[1])
        m_and_msg = [100,message]
        enough_votes = send_accept(m_and_msg,log_num)
        if enough_votes == -3:
            leader_flag = 0
            if debug:
                print("Not enough servers, no longer leader")
        else:
            busy_log = 1
            commit(log_num, m_and_msg)
            if debug:
                print("Leader ")

            start = time.clock()
            end = time.clock()
            while busy_log == 1 or (end - start) > 1:
                end = time.clock()
            find_next_log_entry()

            if debug:
                print("leader synod over")
            return 1

    promise_flag = -1

    while promise_flag != 1: #
        promise_flag = -1
        m = ind+1
        while promise_flag ==-1:
            promise_flag, m_and_msg = prepare_wait_for_promise(m,log_num)
            if promise_flag == -3: #message failed
                return 0
            if debug:
                print("promise flag:",promise_flag)
                print("m_value:", m_and_msg)
            if promise_flag == -1:
                m = m_and_msg[0] +ind+1

        if debug:
            print("values chosen for accept: "+ str(m_and_msg[0]) + ", message: "+ str(m_and_msg[1]))

        if promise_flag == 1:
            catch = catch_all_logic(message, m_and_msg)
            if catch == -3:
                if debug:
                    print()
                    print("Can't schedule, conflict.")
                    print()
                if message != -1:
                    split = message.split()
                    if split[0] == "schedule":
                        print("Unable to schedule meeting", split[1])
                    if split[0] == "cancel":
                        print("Unable to cancel meeting", split[1])

                return 1
            m_and_msg[1] = message

        if debug:
            print("about to send", m_and_msg, "to everyone!")

        enough_votes = send_accept(m_and_msg,log_num)

        if enough_votes == -3:
#            print("not enough servers live to commit")
            return 0
        busy_log = 1
        commit(log_num,m_and_msg)
        if debug:
            print("promise flag is",promise_flag, "taking appropriate action hopefully")
        #
        start = time.clock()
        end = time.clock()
        while busy_log == 1 or (end-start)>2.0 :
#            end = time.clock()
#            if (end-start)>2.0:
#                busy_log = 0
            a=1
        find_next_log_entry()
        log_num = next_log_spot

    if debug:
        print("synod over")
    return 1

def main():

    if len(sys.argv) != 2:
        exitMessage("Expected one argument specifying this site's hostname.")

    global debug
    global name
    global exit_flag
    global sockets
    global ind
    global majority_var
    global ipz
    global portz
    global prop_sock
    global next_log_spot
    global proposer_inbox
    global learner_inbox
    global checkpoint_var


    if debug:
        print("debug mode enabled")
        print("to turn off, type \'debug\'")
#    else:
#        print("debug mode off, type debug for debug messages")
    name = sys.argv[1]
    hostList = readFileContents("hosts.txt")
    ipz, portz, port, ind = setIpPorts(hostList)
    dim = len(ipz)
    majority_var = (dim//2)+1
    file_check_and_load()
    main_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)#
    main_sock.bind((ipz[ind],int(portz[ind])+1))
    prop_sock = [(main_sock),ipz[ind],int(portz[ind])+1]
    if debug:
        print("ips:\n", ipz)
        print("ports:\n", portz)
        print("prop sock:\n", prop_sock[1], prop_sock[2])
        print("hi! you have " + str(int(len(hostList) / 2 - 1)) + " other servers listening in!")
    for i in range(len(ipz)):
        sockets.append(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
    MESSAGE = ""

    acceptor = threading.Thread(target=thread_acceptor, args=((name), int(port), ind, ipz, portz,))
    acceptor.start()
    learner = threading.Thread(target=thread_learner, args=((name), int(port), ind, ipz, portz,))
    learner.start()
    proposer = threading.Thread(target=thread_proposer, args=((name), int(port), ind, ipz, portz,))
    proposer.start()
#    comm_thread1 = threading.Thread(target=thread_accepter, args=((name), int(port), ind, ipz, portz,))
#    comm_thread1.start()


    while MESSAGE!= "exit":
        MESSAGE = input()
        splitMESSAGE = MESSAGE.split()
#        event = MESSAGE.split(" ", 1)
        if debug:
            print("got input:\n",splitMESSAGE)
        if len(splitMESSAGE) == 0:
            print("enter a message.")
        elif splitMESSAGE[0]=="exit":
            splitMESSAGE= "exit"
            splitMESSAGE = encoder.encode(splitMESSAGE)
            proposer_inbox.append(["exit", 1])
            learner_inbox.append(["exit", 1])
            sendToFull(sockets[ind],splitMESSAGE.encode(),(ipz[ind], portz[ind]))
            exit_flag = 1

        elif splitMESSAGE[0]=="debug":
            debug = (debug+1)%2

        elif splitMESSAGE[0] == "schedule":
            #parse schedule
            find_next_log_entry()
            if len(splitMESSAGE) != 6:
                print("Error: incorrect number of 'schedule' parameters ; received {0}, but expected {1}".format(len(splitMESSAGE)-1,5))
                continue
#            synod(MESSAGE,next_log_spot)
            proposer_inbox.append([MESSAGE, next_log_spot])

        elif splitMESSAGE[0] == "cancel":
            #parse cancel
            find_next_log_entry()
            if len(splitMESSAGE) != 2:
                print("Error: incorrect number of parameters for message type 'cancel'; received {0} params, but expected {1} params".format(len(splitMESSAGE)-1,1))
                continue
#            synod(MESSAGE,next_log_spot)
            proposer_inbox.append([MESSAGE, next_log_spot])

        elif splitMESSAGE[0] == "view":
            #parse view
            listMeetings()
        elif splitMESSAGE[0] == "myview":
            #parse myview
            listMeetings(True)
        elif splitMESSAGE[0] == "log":
            #parse log
            listLog()
        elif splitMESSAGE[0] == "checkpoint":
             listCheck()

        elif splitMESSAGE[0] == "mv":
            print(w_dict)

        elif splitMESSAGE[0] == "leader":
            if leader_flag:
                print("I am leader")
            else:
                print("I am not the leader")

        else:
            print("Error: input {0} not recognized as a valid command".format(MESSAGE))
#         send_all(splitMESSAGE,ipz,portz)

    if debug:
        print("exiting main :p")

if __name__ == "__main__":
    main()
