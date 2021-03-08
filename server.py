from socket import *
import os
from _thread import *
from select import select
import random
from threading import Lock
import datetime
from datetime import datetime
import traceback
import sys

account_list = []
#username,email,passwd,[]
board_list = []
#board_name,user,[]
post_list = []
#sn[0],title,user,date,content,''
chatroom_list = []
#username,chatroom_port,'open',[]
sn = 1

host = '127.0.0.1'
port = int(sys.argv[1])
ThreadCount = 0
ServerSocket_tcp = socket(AF_INET, SOCK_STREAM)
ServerSocket_udp = socket(AF_INET, SOCK_DGRAM)


ServerSocket_tcp.bind((host, port))
ServerSocket_udp.bind((host, port))

print('Waiting for a Connection..')
ServerSocket_tcp.listen(15)

def get_time():
    now = datetime.now()
    time = now.strftime("%-H:%M")
    return time

def chatroom_thread(chat_client, addr, chatroom_port, client_list, account_list, chatroom_list):
    usernum = int(chat_client.recv(2048).decode('utf-8'))
    username=''
    for account in account_list:
        if usernum in account[3]:
            username=account[0]
            break

    chatroom_name=''
    for chatroom in chatroom_list:
        if chatroom[1]==chatroom_port:
            chatroom_name=chatroom[0]
            break

    for client in client_list:  
        if client != chat_client:
            if username != chatroom_name:
                client.send(str.encode('sys['+get_time()+']: ' +username+' join us.'))
    
    now_chat=0
    for i in range(len(chatroom_list)):
        if chatroom_name == chatroom_list[i][0]:
            now_chat=i
            chatroom=chatroom_list[i]
            if len(chatroom[3])<3:
                for msg in chatroom[3]:
                    chat_client.send(str.encode(msg+'\n'))
            
            #show last 3 msg
            else:
                chat_client.send(str.encode(chatroom[3][-3]+'\n'))
                chat_client.send(str.encode(chatroom[3][-2]+'\n'))
                chat_client.send(str.encode(chatroom[3][-1]+'\n'))
    
                
    while True:  
        try:  
            chat_msg = chat_client.recv(2048).decode('utf-8')
            chat_msg_spl=chat_msg.split()
            print(chat_msg_spl)
            if chat_msg_spl[0] == 'detach' and chat_msg_spl[-1] == 'own':
                client_list.remove(chat_client)
                break

            if chat_msg_spl[0] == 'leave-chatroom' and chat_msg_spl[-1] == 'own':
                print(str(chat_msg))
                for client in client_list:  
                    if client != chat_client:
                        #send notice to other
                        reply = 'sys['+get_time()+']: the chatroom is close.'
                        client.send(str.encode(reply))
                client_list.clear()
                usernum = int(chat_msg_spl[-2])
                username=''
                #get_username
                for account in account_list:
                    if usernum in account[3]:
                        username=account[0]
                        break
                #close_chatroom
                for chatroom in chatroom_list:
                    if chatroom[0]==username:
                        chatroom[2]='close'
                        break
                break
            usernum = int(chat_msg_spl[-1])
            username=''
            for account in account_list:
                if usernum in account[3]:
                    username=account[0]
                    break

            print("<" + username + ">: " + str(chat_msg))
            send_msg=''
            if chat_msg_spl[0] == 'leave-chatroom':
                client_list.remove(chat_client)
                send_msg = 'sys['+get_time()+']: '+username+' leave us.'
            else:
                msg=''
                for temp in chat_msg_spl[0:-1]:
                    msg+=(temp+' ')
                send_msg =  username + '['+get_time()+']: ' + msg
                chatroom_list[now_chat][3].append(send_msg)
            for client in client_list:
                if client != chat_client:  
                    try:  
                        client.send(str.encode(send_msg))
                    except:
                        traceback.print_exc()
                        client.close() 
                        client_list.remove(client)
        except Exception as e: 
            traceback.print_exc()
            break

def chatroom_server(Client, address, chat_port, account_list, chatroom_list):
    server = socket(AF_INET, SOCK_STREAM)
    server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    try:
        server.bind((host, 65000 + chat_port))
    except:
        pass
    server.listen(10)
    client_list = []
    chatroom_port = 65000+chat_port
    while True:
        chat_client, addr = server.accept()
        client_list.append(chat_client)
        print (str(addr[1]) + " connected.")
        start_new_thread(chatroom_thread, (chat_client,addr,chatroom_port,client_list,account_list,chatroom_list))
    chat_client.close()  
    server.close()

def udp_server(account_list, board_list, post_list,chatroom_list):
    while True:
        data,addr = ServerSocket_udp.recvfrom(2048)
        recv_udp = data.decode('utf-8')
        print("Recv UDP: %s" % recv_udp)
        recv_split = recv_udp.split()
                
        if recv_split[0] == 'register':
            username, email, passwd = recv_split[1], recv_split[2], recv_split[3]

            with Lock():
                success=True
                for account in account_list:
                    if account[0] == username:
                        ServerSocket_udp.sendto(str.encode("Username is already used."),(addr[0], addr[1]))
                        success=False
                        break
                if success:    
                    account_list.append([username,email,passwd,[]])
                    ServerSocket_udp.sendto(str.encode("Register successfully."),(addr[0], addr[1]))

        elif recv_split[0] == 'whoami': #whoami
            usernum = int(recv_split[1])

            with Lock():
                for account in account_list:
                    if usernum in account[3]:
                        ServerSocket_udp.sendto(str.encode(account[0]),(addr[0], addr[1]))
                        break
        else:#list-chatroom
            reply=''
            for  chat in chatroom_list:
                reply+=(chat[0]+'      ')
                reply+=chat[2]
                reply+='\n'
            ServerSocket_udp.sendto(str.encode("Chatroom_name    Status\n"+reply),(addr[0], addr[1]))




def tcp_server(Client, address, chat_port, account_list, board_list, post_list,chatroom_list):

    global sn
    Client.send(str.encode('Welcome to the Server. '+address[0]+' : '+str(address[1])+' default chatroom port:  '+str(65000+chat_port)))
    while True:
        data = Client.recv(2048)
        if not data:
            break

        recv_tcp = data.decode('utf-8')
        print("Receive from TCP: %s" % recv_tcp)
        recv_split = recv_tcp.split()
        reply = ''


        if recv_split[0] == 'login':
            login_name, passwd = recv_split[1], recv_split[2]
                    
            with Lock():
                success=False

                for account in account_list:
                    if account[0] == login_name and account[2] == passwd:
                        usernum = random.randint(1,2147483647)
                        reply = 'Welcome, '+account[0]+'. '+str(usernum)
                        account[3].append(usernum)
                        success=True
                        break
                if not success:
                    reply = 'Login failed. 0'
                Client.send(str.encode(reply))                         
                            
        elif recv_split[0] == 'logout':
            usernum = int(recv_split[1])
                    
            with Lock():
                for account in account_list:
                    if usernum in account[3]:
                        account[3].remove(usernum)
                        reply = 'Bye, '+account[0]+'.'
                        break
                Client.send(str.encode(reply))
                    
        elif recv_split[0] == 'list-user':
                    
            with Lock():
                reply = 'Name\tEmail\n'
                for info in account_list:
                    reply += (info[0]+'\t'+info[1]+'\n')
                Client.send(str.encode(reply))
                            
        elif recv_split[0] == 'exit':
            usernum = int(recv_split[1])
                    
            with Lock():
                for account in account_list:
                    #remove from list
                    if usernum in account[3]:
                        account[3].remove(usernum)
                        break
            break

        #Board_and_Post
        elif recv_split[0] == 'create-board':
            board_name,usernum = recv_split[1],int(recv_split[2])
                    
            with Lock():
                username=''
                success=True

                #find username
                for account in account_list:
                    if usernum in account[3]:
                        username=account[0]
                        break
                for board in board_list:
                    if board_name == board[0]:
                        success=False
                        break
                if not success:
                    reply = 'Board already exists.'
                else:
                    reply = 'Create board successfully.'
                    board_list.append([board_name,username,[]])
                Client.send(str.encode(reply))
                        
        elif recv_split[0] == 'create-post':
            board_name,usernum = recv_split[1],int(recv_split[-1])
            title = ''
            content = ''
                    
            for i in range(1,len(recv_split)-1):
                if recv_split[i] == '--title':
                    title_pos=i
                if recv_split[i] == '--content':
                    content_pos=i

            #range(a,b):a~b-1
            for i in range(title_pos+1,content_pos):
                title += (recv_split[i]+' ')
            for i in range(content_pos+1,len(recv_split)-1):
                content += (recv_split[i]+' ')
                    
            with Lock():
                username=''
                success=False

                for account in account_list:
                    if usernum in account[3]:
                        username=account[0]
                        break

                for board in board_list:
                    if board_name == board[0]:
                        success=True
                        break
                if not success:
                    reply = 'Board does not exist.'
                else:
                    reply = 'Create post successfully.'
                    #Date
                    date_tmp=str(datetime.date.today()).split('-')
                    date = date_tmp[1]+'/'+date_tmp[2]
                    post_list.append([sn,title,username,date,content,''])
                    for board in board_list:
                        if board_name == board[0]:
                            board[2].append(sn)
                            break
                    sn+=1
                Client.send(str.encode(reply))
                        
        elif recv_split[0] == 'list-board':
                    
            with Lock():
                reply = 'Index\t\tName\t\t\tModerator\n'
                index=1

                for board in board_list:
                    reply += (str(index)+'\t\t'+board[0]+'\t\t\t'+board[1]+'\n')
                    index+=1
                Client.send(str.encode(reply))
             
        elif recv_split[0] == 'list-post':
            board_name = recv_split[1]
                    
            with Lock():
                success=False

                for board in board_list:
                    if board_name == board[0]:
                        board_post=board[2]
                        success=True
                        break
                if not success:
                    reply = 'Board does not exist.\n'
                else:
                    reply='S/N\t\tTitle\t\t\tAuthor\t\tDate\n'
                    for post in post_list:
                        if post[0] in board_post:
                            reply += (str(post[0])+'\t\t'+post[1]+'\t\t\t'+post[2]+'\t\t'+post[3]+'\n')
                Client.send(str.encode(reply))
                
        elif recv_split[0] == 'read':
            post_sn = int(recv_split[1])
                    
            with Lock():
                reply=''
                success=False
                        
                for post in post_list:
                    if post[0] == post_sn:
                        reply += 'Author: '+post[2]+'\n'
                        reply += 'Title: '+post[1]+'\n'
                        reply += 'Date: '+post[3]+'\n'
                        reply += '--\n'
                        reply += post[4].replace('<br>','\n')
                        reply += '\n--\n'
                        reply += post[5]
                        success=True
                        break
                if not success:
                    reply = 'Post does not exist.\n'
                Client.send(str.encode(reply))
                
        elif recv_split[0] == 'delete-post':
            post_sn, usernum = int(recv_split[1]), int(recv_split[2])
                    
            with Lock():
                username=''
                success=False

                for account in account_list:
                    if usernum in account[3]:
                        username=account[0]
                        break

                for post in post_list:
                    if post[0] == post_sn:
                        if post[2] == username:
                            reply = 'Delete successfully.'
                            post_list.remove(post)
                        else:
                            reply = 'Not the post owner.'
                        success=True
                        break
                if not success:
                    reply = 'Post does not exist.'
                            
                Client.send(str.encode(reply))
                

        elif recv_split[0] == 'update-post':
            post_sn, usernum = int(recv_split[1]), int(recv_split[-1])
                    
            with Lock():
                username=''
                update=0
                update_info=''
                success=False

                for account in account_list:
                    if usernum in account[3]:
                        username=account[0]
                        break
                        
                if recv_split[2] == '--content':
                    update=1
                        
                for i in range(3,len(recv_split)-1):
                    update_info+=(recv_split[i]+' ')

                for post in post_list:
                    if post[0] == post_sn:
                        if post[2] == username:
                            reply = 'Update successfully.'
                            if update == 0: # title
                                post[1] = update_info
                            else: # content
                                post[4] = update_info
                        else:
                            reply = 'Not the post owner.'
                        success=True
                        break
                if not success:
                    reply = 'Post does not exist.'
                            
                Client.send(str.encode(reply))
                
        elif recv_split[0] == 'comment':
            post_sn, usernum = int(recv_split[1]), int(recv_split[-1])
                    
            with Lock():
                name=''
                comment=''
                success=False

                for account in account_list:
                    if usernum in account[3]:
                        username=account[0]
                        break

                for i in range(2,len(recv_split)-1):
                    comment+=(recv_split[i]+' ')

                for post in post_list:
                    if post[0] == post_sn:
                        reply = 'Comment successfully.'
                        post[5]+=(username+': '+comment+'\n') 
                        success=True
                        break
                if not success:
                    reply = 'Post does not exist.'
                Client.send(str.encode(reply))

        #hw3
        elif recv_split[0] == 'create-chatroom':
            reply = 'start to create chatroom...'
            usernum, chatroom_port = int(recv_split[2]), int(recv_split[3])
            username=''
            for account in account_list:
                if usernum in account[3]:
                    username=account[0]
                    break
            empty=True
            for chatroom in chatroom_list:
                if username == chatroom[0]:
                    reply = 'User has already created the chatroom.'
                    empty=False
                    break
            if empty:
                chatroom_list.append([username,chatroom_port,'open',[]])
            Client.send(str.encode(reply))
    
        elif recv_split[0] == 'join-chatroom':
            chatroom_name, usernum = recv_split[1], int(recv_split[2])
            reply = ''
            chatroom_port=''
            op=False
            for chatroom in chatroom_list:
                if chatroom[0] == chatroom_name and chatroom[2] == 'open':
                    chatroom_port=str(chatroom[1])
                    op=True
                    break
            if op:
                Client.send(str.encode(reply+' '+chatroom_port))
            else:
                reply = 'The chatroom does not exist or the chatroom is close.'
                Client.send(str.encode(reply))
                
        elif recv_split[0] == 'restart-chatroom':
            usernum = int(recv_split[1])
            username=''
            for account in account_list:
                if usernum in account[3]:
                    username=account[0]
                    break

            exist=False
            for chatroom in chatroom_list:
                if chatroom[0] == username:
                    exist=True
                    chatroom[2]='open'
                    break
            reply = ' '
            if not exist:
                reply = 'Please create-chatroom first.'
            Client.send(str.encode(reply))
                
    
    Client.close()


start_new_thread(udp_server,(account_list, board_list, post_list,chatroom_list))
while True:
    Client, address = ServerSocket_tcp.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(tcp_server, (Client, address, ThreadCount, account_list, board_list, post_list, chatroom_list))
    start_new_thread(chatroom_server, (Client, address,  ThreadCount, account_list, chatroom_list))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))
ServerSocket.close()





















