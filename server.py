import time
import eventlet
import socketio
from assistant import Assistant
from datetime import date
import handlers
import json

sio = socketio.Server(cors_allowed_origins='*')

app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'},
    '/styles.css': {'content_type': 'text/css', 'filename': 'styles.css'}
})

current_user = 'aleksandar.kirilov@proxym.fr'

projects = handlers.get_projects_for_user(
    '{"email": "' + current_user + '"}')

context = [
    {"role": "system",
     "content":
        f"""
Current date is: {date.today()}
Holidays: ["2024-01-01"]'

Currently connected user is '{current_user}'

This program helps user fill in their monthly activity reports. Each activity
report is associated to a project that user has worked on. Activities can be
reported in increments of 25% per day. A single day cannot have more than 100% of
 reported time - this includes activities and absences.
         """
     },
]

assistant = Assistant(context)


def send_client_callback(message):
    print("Callback called", message)

    if message["role"] == "system-confirm":
        sio.emit('system-confirm', {"response": message})
    else:
        sio.emit('assistant-message', {"response": message})


@sio.event
def connect(sid, environ):
    print('connect ', sid)
    sio.emit('system-context', assistant.messages)


@sio.on('confirm-message')
def confirm_message(sid, data):
    print('User confirms ', data)
    assistant.confirm(data["tool_id"], data["data"])

    if not assistant.function_calls:
        assistant.generate_message(send_client_callback)

        # if result["role"] == "system-confirm":
        #     sio.emit('system-confirm', {'data': result})
        # else:
        #     sio.emit('assistant-message', {'data': result})


@sio.on('client-message')
def client_message(sid, data):
    print('message ', data)
    assistant.function_calls.clear()
    assistant.generate_message(send_client_callback, data)


@sio.on('restart-conversation')
def restart(sid):
    print('restarting', )
    assistant.init()
    sio.emit('system-message', {'data': {'content': 'Conversation restarted'}})
    sio.emit('system-context', assistant.messages)


@sio.event
def disconnect(sid):
    print('disconnect ', sid)


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
