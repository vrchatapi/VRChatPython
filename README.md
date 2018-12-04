# VRChatPython
A Python library for the VRChat API.

Feel free to make commits and push requests!

# Quickstart Guide

Download the `VRChatPython.py` file and put it in your Python `site-packages` folder or just put it in your project's directory and import it from there.

## Setup

To initialize the VRChat Python interface, simply use the following code:
```
import VRChatPython

VRChatAPI_interface = VRChatPython.VRChatPython('username','password')
```
This code creates a `VRChatAPI_interface` object for interacting with the VRChat API. Replace `username` and `password` with your account's username and password. The interface object will handle the API key and authorization for you.

## The Functions

After initialization, there are only really 2 functions. Both of these will handle most of the work for you.

#### `VRChatPython.VRChatPython.make_request(url, parameters={}, header_dat={})`
This is the main function used for interaction with the VRChat API. See the [VRChat API documentation](https://github.com/VRChatAPI/vrchatapi.github.io) for different request options.

#### `VRChatPython.VRChatPython.save_image(url, file_name)`
The `save_image` function is used to download images and save them to the provided file name. (works with full paths too)

## Some Examples

### Outputing the names of the first 2 people on your friends list:
```
import VRChatPython
 
VRChatAPI_interface = VRChatPython.VRChatPython('username','passwird')
 
response = VRChatAPI_interface.make_request('/auth/user/friends',{'n':'2'})
 
for friend in response:
    print(friend['displayName'])
```

### Downloading your avatar preview:
```
import VRChatPython
 
VRChatAPI_interface = VRChatPython.VRChatPython('username','password')
 
response = VRChatAPI_interface.make_request('/auth/user')
 
VRChatAPI_interface.save_image(response['currentAvatarThumbnailImageUrl'],'test.png')
```

### Outputing your friend's status:
```
import VRChatPython
 
VRChatAPI_interface = VRChatPython.VRChatPython('username','password')

my_friend = 'username_of_friend'
 
response = VRChatAPI_interface.make_request('/users/' + my_friend + '/name')
 
print(response['status'])
```

## Some Notes
This library is somewhat limited because it can't handle any API methods other than `GET`. Since most of them use `GET`, VRChatPython should be able to cover most of the methods.
