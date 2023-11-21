import json
import sys


def task_handler(event, context):
    print('Hello, World!\n'
          f'Event: {event}\n'
          f'Context: {context}\n'
          f'Python version: {sys.version}')
    return {'success': True}
