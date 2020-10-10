'''
Each time this file is split with this:

## ----- Example: X ----- ##

It will be treated as a new file/example
'''

## ----- Example: Change call Retry Count ----- ##

'''
Built in is retry logic for when VRChat disconnects a call with no response
Default retries is 1 (so 1 call, then 1 retry if it fails)

To change retry count, use the method below.
'''

from vrcpy.request import Call

Call.call_retries = 5
