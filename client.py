from socket import *
import sys
import select 

host = sys.argv[1]
port = int(sys.argv[2])
Login_num = 0
ClientSocket_tcp = socket(AF_INET, SOCK_STREAM)
ClientSocket_udp = socket(AF_INET, SOCK_DGRAM)


try:
    ClientSocket_tcp.connect((host, port))
except socket.error as e:
    print(str(e))


recv_msg = ClientSocket_tcp.recv(2048)
print(recv_msg.decode('utf-8'))
recv_msg=recv_msg.split()
chat_port=int(recv_msg[-1])
chat_own=0
join=0

print('********************************\n** Welcome to the BBS server. **\n********************************')

def chatroom(chat_con = chat_port):
    global chat_own
    global join
    leave = False

    Chat_Socket = socket(AF_INET, SOCK_STREAM)
    Chat_Socket.connect((host, chat_con))
    Chat_Socket.send(str.encode(str(Login_num)))
    
    while True:
        if leave:
            break

        socket_list = [sys.stdin, Chat_Socket]
        read_sockets, write_socket, error_socket = select.select(socket_list,[],[])  
        
        for socks in read_sockets:
            if socks == Chat_Socket:
                recv_msg = socks.recv(2048).decode('utf-8')
                print(recv_msg)
                if 'the chatroom is close.' in recv_msg:
                    leave=True
                    break
            else: 
                Input = input()
                if Input == 'leave-chatroom':
                    if (chat_own == 1 and join==0):
                        Chat_Socket.send(str.encode(Input+' '+str(Login_num)+' own'))
                        chat_own = 0
                    else:
                        Chat_Socket.send(str.encode(Input+' '+str(Login_num)))
                        join=0
                    leave=True
                elif Input == 'detach' and chat_own == 1:
                    Chat_Socket.send(str.encode('detach own'))
                    leave=True
                else:
                    Chat_Socket.send(str.encode(Input+' '+str(Login_num)))

while True:
    try:
        Input = input('% ')
        Input_split=Input.split()
        
        #udp
        if Input_split[0] == 'register' or Input_split[0] == 'whoami' or Input_split[0] == 'list-chatroom':
            if Input_split[0] == 'register':
                if len(Input_split) != 4:
                    print('Usage: register <username> <email> <password>')
                    continue
                ClientSocket_udp.sendto(str.encode(Input),(host, port))
            
            elif Input_split[0] == 'whoami':
                if Login_num == 0:
                    print('Please login first.')
                    continue
                ClientSocket_udp.sendto(str.encode(Input+' '+str(Login_num)),(host, port))

            elif Input_split[0] == 'list-chatroom':
                if Login_num == 0:
                    print('Please login first.')
                    continue
                ClientSocket_udp.sendto(str.encode(Input),(host, port))

            recv_msg,addr = ClientSocket_udp.recvfrom(2048)
            print(recv_msg.decode('utf-8'))
        
        #tcp
        else:

            if Input_split[0] == 'exit':
                ClientSocket_tcp.send(str.encode(Input+' '+str(Login_num)))
                break

            elif Input_split[0] == 'login':
                if len(Input_split) != 3:
                    print('Usage: login <username> <password>')
                    continue
                if Login_num != 0:
                    print('Please logout first.')
                    continue
                
                ClientSocket_tcp.send(str.encode(Input))
                recv_msg = ClientSocket_tcp.recv(2048)
                recv_msg = recv_msg.decode('utf-8').split()
                Login_num = int(recv_msg[2])
                print(recv_msg[0]+' '+recv_msg[1])

            elif Input_split[0] == 'logout':
                if Login_num == 0:
                    print('Please login first.')
                    continue
                if chat_own == 1:
                    print('Please do "attach" and "leave-chatroom" first.')
                    continue

                ClientSocket_tcp.send(str.encode(Input+' '+str(Login_num)))
                Login_num=0
                recv_msg = ClientSocket_tcp.recv(2048)
                print(recv_msg.decode('utf-8'))
            
            elif Input_split[0] == 'list-user':
                ClientSocket_tcp.send(str.encode(Input))
                recv_msg = ClientSocket_tcp.recv(2048)
                print(recv_msg.decode('utf-8'))

            #HW2
            elif Input_split[0] == 'create-board':
                if len(Input_split)!=2:
                    print('create-board <name>')
                    continue
                if Login_num == 0:
                    print('Please login first.')
                    continue  

                ClientSocket_tcp.send(str.encode(Input+' '+str(Login_num)))
                recv_msg = ClientSocket_tcp.recv(2048)
                print(recv_msg.decode('utf-8'))

            elif Input_split[0] == 'create-post':
                if '--title' not in Input_split or '--content' not in Input_split:
                    print('create-post <board-name> --title <title> --content <content>')
                    continue
                if Login_num == 0:
                    print('Please login first.')
                    continue
                
                ClientSocket_tcp.send(str.encode(Input+' '+str(Login_num)))
                recv_msg = ClientSocket_tcp.recv(2048)
                print(recv_msg.decode('utf-8'))
            
            elif Input_split[0] == 'list-board':
                ClientSocket_tcp.send(str.encode(Input))
                recv_msg = ClientSocket_tcp.recv(2048)
                print(recv_msg.decode('utf-8'),end='')
            
            elif Input_split[0] == 'list-post':
                if len(Input_split)!=2:
                    print('list-post <board-name>')
                    continue
                
                ClientSocket_tcp.send(str.encode(Input))
                recv_msg = ClientSocket_tcp.recv(2048)
                print(recv_msg.decode('utf-8'),end='')
            
            elif Input_split[0] == 'read':
                if len(Input_split)!=2:
                    print('read <post-S/N>')
                    continue
                if not(Input_split[1].isdigit()):
                    print('read <post-S/N>')
                    continue 
                
                ClientSocket_tcp.send(str.encode(Input))
                recv_msg = ClientSocket_tcp.recv(2048)
                print(recv_msg.decode('utf-8'),end='')
            
            elif Input_split[0] == 'delete-post':
                if Login_num == 0:
                    print('Please login first.')
                    continue
                if len(Input_split)!=2:
                    print('delete-post <post-S/N>')
                    continue
                if not(Input_split[1].isdigit()):
                    print('delete-post <post-S/N>')
                    continue
                
                ClientSocket_tcp.send(str.encode(Input+' '+str(Login_num)))
                recv_msg = ClientSocket_tcp.recv(2048)
                print(recv_msg.decode('utf-8'))
            
            elif Input_split[0] == 'update-post':
                if Login_num == 0:
                    print('Please login first.')
                    continue
                if len(Input_split)<4:
                    print('update-post <post-S/N> --title/content <new>')
                    continue
                if not(Input_split[1].isdigit()) or not(Input_split[2]=='--title' or Input_split[2]=='--content'):
                    print('update-post <post-S/N> --title/content <new>')
                    continue
                
                
                ClientSocket_tcp.send(str.encode(Input+' '+str(Login_num)))
                recv_msg = ClientSocket_tcp.recv(2048)
                print(recv_msg.decode('utf-8'))
            
            elif Input_split[0] == 'comment':
                if Login_num == 0:
                    print('Please login first.')
                    continue
                if len(Input_split)<3:
                    print('comment <post-S/N> <comment>')
                    continue
                if not(Input_split[1].isdigit()):
                    print('comment <post-S/N> <comment>')
                    continue
                
                ClientSocket_tcp.send(str.encode(Input+' '+str(Login_num)))
                recv_msg = ClientSocket_tcp.recv(2048)
                print(recv_msg.decode('utf-8'))
            

            #Chatroom
            elif Input_split[0] == 'create-chatroom':
                if len(Input_split)==1:
                    print('create-chatroom <port>')
                    continue
                if Login_num == 0:
                    print('Please login first.')
                    continue
                
                ClientSocket_tcp.send(str.encode(Input+' '+str(Login_num)+' '+str(chat_port)))
                recv_msg = ClientSocket_tcp.recv(2048).decode('utf-8')
                print(recv_msg)

                if recv_msg != 'User has already created the chatroom.':
                    chat_own = 1
                    print('*************************\n** Welcome to the chatroom **\n*************************')
                    chatroom() 
                    print('Welcome back to BBS.')

            elif Input_split[0] == 'join-chatroom':
                if len(Input_split)==1:
                    print('join-chatroom <chatroom_name>')
                    continue
                if Login_num == 0:
                    print('Please login first.')
                    continue
                
                join=1
                ClientSocket_tcp.send(str.encode(Input+' '+str(Login_num)))
                recv_msg = ClientSocket_tcp.recv(2048).decode('utf-8')
                
                if recv_msg == 'The chatroom does not exist or the chatroom is close.':
                    print(recv_msg)
                    continue
                
                print('*************************\n** Welcome to the chatroom **\n*************************')
                chatroom(int(recv_msg.split()[-1]))
                print('Welcome back to BBS.')

            elif Input_split[0] == 'attach':
                if Login_num == 0:
                    print('Please login first.')
                    continue
                if chat_own == 0:
                    print('Please create-chatroom first.')
                    continue
                
                print('*************************\n** Welcome to the chatroom **\n*************************')
                chatroom()
                print('Welcome back to BBS.')

            elif Input_split[0] == 'restart-chatroom':
                if Login_num == 0:
                    print('Please login first.')
                    continue
                if chat_own == 1:
                    print('Your chatroom is still running.')
                    continue
        
                ClientSocket_tcp.send(str.encode(Input+' '+str(Login_num)))
                recv_msg = ClientSocket_tcp.recv(2048).decode('utf-8')
                if recv_msg == ' ':
                    chat_own = 1
                    print('*************************\n** Welcome to the chatroom **\n*************************')
                    chatroom()
                    print('Welcome back to BBS.')
                else:
                    print(Response)

            else:
                print('Command not found.')
    
    except Exception as e:
        print(str(e))

ClientSocket_tcp.close()
ClientSocket_udp.close()


