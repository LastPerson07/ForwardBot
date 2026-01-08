import os
from os import environ

class Config:
    API_ID = environ.get("API_ID", "")
    API_HASH = environ.get("API_HASH", "")
    BOT_TOKEN = environ.get("BOT_TOKEN", "") 
    BOT_SESSION = environ.get("BOT_SESSION", "AutoForwardX") 
    
    # FIX: Checks both common names for the MongoDB string
    DATABASE_URI = environ.get("DATABASE_URI", environ.get("DATABASE", ""))
    DATABASE_NAME = environ.get("DATABASE_NAME", "ForwardBot")
    
    BOT_OWNER_ID = [int(id) for id in environ.get("BOT_OWNER_ID", '8496419402').split()]
    LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-1003656791142'))
    FORCE_SUB_CHANNEL = environ.get("FORCE_SUB_CHANNEL", "THEUPDATEDGUYS") 
    FORCE_SUB_ON = environ.get("FORCE_SUB_ON", "False")
    
    # Ensure PORT is an integer for Gunicorn/Web server
    PORT = int(environ.get('PORT', '8080'))

class temp(object): 
    lock = {}
    CANCEL = {}
    forwardings = 0
    BANNED_USERS = []
    IS_FRWD_CHAT = []
