from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter


# get info from the server. used to get messages.
def receive():
    while True:
        try:
            msg = client_socket.recv(BUFFER_SIZE).decode("utf8")  # decode msg from other clients
            msg_list.insert(tkinter.END, msg)  # add the received message to our chat
            msg_list.see(tkinter.END)
        except OSError:
            break


def send(event=None):  # binder passes event
    msg = my_msg.get()
    my_msg.set("")  # clear text field after sending a message
    global current_room
    if msg == "{quit}":  # check if the user decides to quit, if so, clean up
        msg_list.insert(tkinter.END, "Goodbye " + my_username)
        client_socket.send(bytes(my_username.get() + " terminated their client (thread)", "utf8"))
        client_socket.close()  # closes client thread on server.
        rootWindow.quit()
        return
    client_socket.send(bytes(my_username.get() + ": " + msg, "utf8"))  # otherwise, send message to server, let
    # server handle our message.


# send quit message to the server.
def on_closing(event=None):
    # Send server quit message.
    my_msg.set("{quit}")

    send()


def change_room():
    global current_room
    current_room = ((chatRoomSelected.get()).split(' '))[2]
    client_socket.send(bytes("/" + current_room, "utf8"))   # send msg to server to change our room
    msg_list.delete(0, tkinter.END)  # clear the chat
    msg_list.insert(tkinter.END, "Joining room " + str(current_room) + "...")  # tell user new room
    msg_list.see(tkinter.END)


# Global variables.
number_of_rooms = 0
current_room = 0

rootWindow = tkinter.Tk()
rootWindow.title("Group 14 Messenger")

messages_frame = tkinter.Frame(rootWindow)
my_msg = tkinter.StringVar()  # For the messages to be sent.
my_msg.set("")  # set our globals. This sets the users msg and username values from text input
my_username = tkinter.StringVar()
my_username.set("")

scrollbar = tkinter.Scrollbar(messages_frame)  # To see through previous messages.
# Messages container.
msg_list = tkinter.Listbox(messages_frame, height=30, width=100, yscrollcommand=scrollbar.set, bg="pink")
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()

username_label = tkinter.Label(rootWindow, text="Enter username: ")
username_label.pack()
username_field = tkinter.Entry(rootWindow, textvariable=my_username)
username_field.pack()

message_label = tkinter.Label(rootWindow, text="Enter message: ")
message_label.pack()
entry_field = tkinter.Entry(rootWindow, textvariable=my_msg, width=50)
entry_field.bind("<Return>", send)
entry_field.pack()
send_button = tkinter.Button(rootWindow, text="Send", command=send)
send_button.pack()

rootWindow.protocol("WM_DELETE_WINDOW", on_closing)

# Socket with given AWS parameters.
HOST = "192.168.56.102"
PORT = 3005
BUFFER_SIZE = 1024
ADDR = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)

# get number of rooms from the server and list them for the client
first_msg = client_socket.recv(BUFFER_SIZE).decode("utf8")
number_of_rooms = int(first_msg)
chatRoomSelected = tkinter.StringVar(rootWindow)
chatRoomSelected.set("Select Chat Room")
rooms_list = []
for i in range(number_of_rooms):
    rooms_list.append("Chat Room " + str(i + 1))

chat_rooms = tkinter.OptionMenu(rootWindow, chatRoomSelected, *rooms_list)
chat_rooms.pack()
change_button = tkinter.Button(rootWindow, text="Change Room", command=change_room)
change_button.pack()

receive_thread = Thread(target=receive)
receive_thread.start()
rootWindow.resizable(width=False, height=False)  # The client can't resize the window.
tkinter.mainloop()
