async_mode = None

from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import RoomSerializer
from .models import Room, Message
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.decorators import api_view
from django.db.models import Q

from .serializers import MessageSerializer

#Socket imports
import os
from django.http import HttpResponse
import socketio

# # basedir = os.path.dirname(os.path.realpath(__file__))
sio = socketio.Server(cors_allowed_origins="*", async_mode=async_mode)
thread = None

@api_view(['GET'])
def index(request):
    global thread
    if thread is None:
        thread = sio.start_background_task(background_thread)
    # return HttpResponse(open(os.path.join(basedir, 'static/index.html')))
    return HttpResponse('Connected')

def background_thread():
    count = 0
    while True:
        sio.sleep(10)
        count += 1
        sio.emit('my_response', {'data': 'Server generated event'},
                 namespace='/test')
        
@sio.event
def join(sid, message):
    room = message['room']
        
    
    sio.enter_room(sid, room)
    messages = Message.objects.filter(room_id=message['room']).all()

    sio.emit('my_response', {'data': f"{sid} Joined the Room",  'count': 0}, room=room, skip_sid=sid)

    if messages.count()==0:
        sio.emit('my_response', {'data': "Hey how may i help you",  'count': 0}, room=sid)
    else:
        for i in messages:
            sio.emit('my_response', {'data': str(i.message_data),  'count': 0}, room=sid)

@sio.event
def leave(sid, message):
    sio.leave_room(sid, message['room'])
    sio.emit('my_response', {'data': 'Left room: ' + message['room']},
             room=message['room'])

def close_room(sid, message):
    sio.emit('my_response',
             {'data': 'Room ' + message['room'] + ' is closing.'},
             room=message['room'])
    sio.close_room(message['room'])
    
# @sio.event
def message_event(sid, message):
    type = message['type']
    room_id = message['room_id']
    message_data = message['message_data']
    side = message['side']
    author = message['author']
    message_type = message['message_type']
    
    data = {
        "type": type,
        "room_id": room_id,
        "message_data": message_data,
        "side": side,
        "author": author,
        "message_type": message_type,
    }
    serializer = MessageSerializer(data=data)
    if serializer.is_valid():
        
        # field = {
        #     "room_id": room_id,
        #     "message_data": message_data,
        #     "side": side,
        #     "author": author,
        #     "message_type": message_type,
        #     "read": True,
        # }     
        # response = json.loads(dowellconnection(*chat, "insert", field, update_field=None))
        Message.objects.create(
            type = type,
            room_id = room_id,
            message_data = message_data,
            side = side,
            author = author,
            message_type = message_type
        )
        return sio.emit('my_response', {'data': message['message_data'], 'sid':sid},  room=message['room_id'])
    else:
        return sio.emit('my_response', {'data': 'Invalid Data', 'sid':sid}, room=message['room'])

    
# #   skip_sid=sid,      
@sio.event
def disconnect_request(sid):
    sio.disconnect(sid)


# message=["Hello Everyone", "This is the second message"]
    

@sio.event
def connect(sid, environ, query_para):
    # url = 'https://100096.pythonanywhere.com/api/v2/room-service/?type=get_messages&room_id=64f6ff29c4a02ffba74d1e2e'
    # response = requests.get(url)
    # res = json.loads(response.text)
    # message = res['response']['data']
    # for i in message:
    #     sio.emit('my_response', {'data': i['message_data'], 'count': 0}, room=sid)
    # print(query_para)
    # messages = Message.objects.filter(room_id="test123").all()
    # if messages.count()==0:
    #     sio.emit('my_response', {'data': "Hey how may i help you", 'count': 0}, room=sid)
    # else:
    #     for message in messages:
    #         sio.emit('my_response', {'data': str(message.message_data), 'count': 0}, room=sid)
    sio.emit('my_response', {'data': "Welcome to Dowell Chat", 'count': 0}, room=sid)


@sio.event
def disconnect(sid):
    print('Client disconnected')

""" WEB RTC SIGNALING SERVER SECTION"""

# Import necessary libraries
# import socketio
# import asyncio
# sio = socketio.Server(cors_allowed_origins="*", async_mode=async_mode)
# Create a Socket.io server with the /webrtc namespace
# webrtc_sio = sio.namespace('/webrtc')

# Dictionary to store peer connections
peer_connections = {}

# @sio.event(namespace='/webrtc')
# def offer(sid, message):
#     recipient_sid = message['recipient_sid']
#     offer = message['offer']

#     # Send the offer to the recipient
#     # sio.emit('offer', {'offer': offer}, room=recipient_sid, namespace='/webrtc')
#     sio.emit('offer', {'offer': offer, 'sender_sid': sid}, room=recipient_sid, namespace='/webrtc')


# @sio.event(namespace='/webrtc')
# def answer(sid, message):
#     # Handle answer message and send it to the sender
#     sender_sid = message['sender_sid']
#     answer = message['answer']

#     print(f"Sender is {sender_sid}")

#     # Send the answer to the sender
#     # sio.emit('receive_answer', answer, room=sender_sid, namespace='/webrtc')
#     # sio.emit('receive_answer', {'answer': answer}, room=sender_sid, namespace='/webrtc')
#     sio.emit('receive_answer', {'answer': answer, 'sender_sid': sid}, room=sender_sid, namespace='/webrtc')


# @sio.event(namespace='/webrtc')
# def ice_candidate(sid, message):
#     # Handle ICE candidate message and send it to the other peer
#     recipient_sid = message['recipient_sid']
#     ice_candidate = message['ice_candidate']

#     # Send the ICE candidate to the recipient
#     # sio.emit('receive_ice_candidate', ice_candidate, room=recipient_sid, namespace='/webrtc')
#     sio.emit('receive_ice_candidate', {'ice_candidate': ice_candidate, 'sender_sid': sid}, room=recipient_sid, namespace='/webrtc')

# Define a handler for when a client connects to the /webrtc namespace
@sio.event(namespace='/webrtc')
def connect(sid, environ, query_para):
    print(f"Client {sid} connected to /webrtc namespace")
    sio.emit('my_response', {'sid': sid,})
    print(sid)

# Define a handler for when a client disconnects from the /webrtc namespace
@sio.event(namespace='/webrtc')
def disconnect(sid):
    # Cleanup and remove the peer connection data
    if sid in peer_connections:
        recipient_sid = peer_connections[sid]["recipient_sid"]
        if recipient_sid in peer_connections:
            # Notify the recipient about the disconnect
            sio.emit('peer_disconnected', room=recipient_sid, namespace='/webrtc')
            del peer_connections[recipient_sid]
        del peer_connections[sid]
    print(f"Client {sid} disconnected from /webrtc namespace")


# Handle offer messages
@sio.event(namespace='/webrtc')
def offer(sid, message):
    recipient_sid = message['recipient_sid']
    offer = message['offer']

    # Store the offer in the peer_connections dictionary
    peer_connections[sid] = {"recipient_sid": recipient_sid, "offer": offer}

    # Forward the offer to the recipient
    sio.emit('offer', {'offer': offer, 'sender_sid': sid}, room=recipient_sid, namespace='/webrtc')

# Handle answer messages
@sio.event(namespace='/webrtc')
def answer(sid, message):
    sender_sid = message['sender_sid']
    answer = message['answer']

    # Forward the answer to the sender
    sio.emit('receive_answer', {'answer': answer, 'sender_sid': sid}, room=sender_sid, namespace='/webrtc')

@sio.event(namespace='/webrtc')
def ice_candidate(sid, message):
    recipient_sid = message['recipient_sid']
    ice_candidate = message['ice_candidate']

    # Forward the ICE candidate to the recipient
    sio.emit('receive_ice_candidate', {'ice_candidate': ice_candidate, 'sender_sid': sid}, room=recipient_sid, namespace='/webrtc')

