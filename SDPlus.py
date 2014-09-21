import urllib
from xml.dom import minidom
#https://docs.python.org/2/library/xml.dom.html
#https://docs.python.org/2/library/xml.dom.minidom.html

#Main Processing Section
apiURL = 'http://sdplus/servlets/RequestServlet'

def setupLoginParams(username, password, domain='NORTHBRISTOL', authType='AD_AUTH'): #sets up global params for use in send function. You MUST call this before others.
    global loginParams
    loginParams = {
        'username' : username,
        'password' : password,
        'DOMAIN_NAME' : domain,
        'logonDomainName' : authType, #AD_AUTH=active directory, "Local Authentication"=local authentication protocol
    }

def process(operation, params): #Sends and Parses all params. Requires global loginParams to be pre-populated.
    paramsToSend = {'operation' : operation}
    paramsToSend.update(params)
    return send(apiURL, paramsToSend)

def send(apiURL, params):   #Send & Parse data. Requires global loginParams to be pre-populated.
    params.update(loginParams)
    data = urllib.urlencode(params)
    rawxml = urllib.urlopen(apiURL, data)
    return parse(rawxml)

def parse(rawxml): #returns True/False and a dict of details (always including details['message'])
    xmlResponse = minidom.parse(rawxml)
    #print xmlResponse.toprettyxml()
    success = False
    status = xmlResponse.getElementsByTagName("operationstatus")
    status = status[0].firstChild.wholeText
    message = xmlResponse.getElementsByTagName("message")
    message = message[0].firstChild.wholeText
    details = {'message' : message}
    if status == "Success":
        success = True
        detailsElement = xmlResponse.getElementsByTagName("propname")
        if detailsElement:
            propnameKeys = dict(
                (item.getAttribute('key'), item.firstChild.data)
                for item in detailsElement if item.firstChild is not None
            )
            details.update(propnameKeys)
        returnedID = xmlResponse.getElementsByTagName("workorderid")
        if returnedID:
            details['workorderid'] = returnedID[0].firstChild.wholeText
    return success, details

#Main APIs:
def add(subject,
        description,
        requester,
        requesteremail,
        impact='3 Impacts Department',
        urgency='3 Business Operations Slightly Affected',
        subcategory='Other',
        reqtemplate='Default Request',
        requesttype='Service Request',
        status='',
        mode='@Southmead Brunel building',
        service='CERNER',
        category='',
        group='Back Office Third Party',
        technician='',
        technicianemail='',
        item='',
        impactdetails='',
        resolution='',
        priority='',
        level='',
        supplierRef=''):
    params = {
        'operation' : 'addrequest',
        'subject' : subject,
        'description' : description,
        'requester' : requester,
        'impact' : impact,
        'urgency' : urgency,
        'subcategory' : subcategory,
        'requesteremail' : requesteremail,
        'reqtemplate' : reqtemplate,
        'requesttype' : requesttype,
        'status' : status,
        'mode' : mode,  #=site
        'service' : service,    #=Service Category
        'category' : category,  #''=Self Service Incident
        'group' : group,
        'technician' : technician,
        'technicianemail' : technicianemail,
        'item' : item,
        'impactdetails' : impactdetails,
        'resolution' : resolution,
        'priority' : priority,
        'level' : level,
        'supplier ref' : supplierRef
    }
    return process('addrequest', params)

#Update a call
def update(workorderid,
        reqtemplate='',
        requesttype='',
        subject='',
        description='',
        resolution='',
        requester='',
        requesteremail='',
        priority='',
        level='',
        status='',
        impact='',
        urgency='',
        impactdetails='',
        mode='',
        service='',
        category='',
        subcategory='',
        item='',
        group='',
        technician='',
        technicianemail='',
        supplierRef=''):
    params = {
        'workOrderID' : workorderid,
        'reqtemplate' : reqtemplate,
        'requesttype' : requesttype,
        'subject' : subject,
        'description' : description,
        'resolution' : resolution,
        'requester' : requester,
        'requesteremail' : requesteremail,
        'priority' : priority,
        'level' : level,
        'status' : status,
        'impact' : impact,
        'urgency' : urgency,
        'impactdetails' : impactdetails,
        'mode' : mode,
        'service' : service,
        'category' : category,
        'subcategory' : subcategory,
        'item' : item,
        'group' : group,
        'technician' : technician,
        'technicianemail' : technicianemail,
        'supplier ref' : supplierRef
    }
    return process('updaterequest', params)

def assign(workorderid, technician):
    return update(workorderid, technician=technician)

def close(workorderid, closeComments=''):
    params = {
        'workOrderID' : workorderid,
        'closecomment' : closeComments
    }
    #return update(workorderid, status='Closed')
    return process('CloseRequest', params)

def delete(workorderid):   #get dictionary of a call's details
    params = {'workOrderID' : workorderid}
    return process('deleterequest', params)

def addNote(workorderid, notesText, isPublic=True):
    params = {
        'workOrderID' : workorderid,
        'notesText' : notesText,
        'isPublic' : isPublic   #True=public notes, False=private notes
    }
    return process('AddNotes', params)

def addWorkLog(workorderid,
        technician='',
        technicianemail='',
        description='',
        workhours='',
        workminutes='',
        cost='',
        executedtime=''):
    params = {
        'workOrderID' : workorderid,
        'technician' : technician,
        'technicianemail' : technicianemail,
        'description' : description,
        'workhours' : workhours,
        'workminutes' : workminutes,
        'cost' : cost,
        'executedtime' : executedtime,
    }
    return process('AddWorkLog', params)

def deleteWorkLog(workorderid, workLogID=''):
    params = {
        'workOrderID' : workorderid,
        'requestchargeid' : workLogID,    #work Log ID to delete
    }
    return process('deleteworklog', params)

def get(workorderid):   #get dictionary of a call's details
    params = {'workOrderID' : workorderid}
    return process('getrequestdetails', params)


'''
#===Usage===
#See http://www.manageengine.com/products/service-desk/help/adminguide/index.html for API details
#All calls return:
    #"status" =True/False as to whether it's worked or not)
    #"details" = a dictionary of reponses back from SDPlus. details['message'] will always exist for every call.

#---setup all the logins SDPlus needs---
#get windows username for SDPlus API login
import os
username = os.environ.get("USERNAME")
#this statement below is required always, before any api call (it sets up a global dictionary)
setupLoginParams(username, '[yourWindowsPassword]', 'NORTHBRISTOL', 'AD_AUTH')

#---Add a call---
#Takes in a number of parameters, most of which are optional. See code above for details.
status, details = add(
    subject='Simon Test automation subject 2',
    description='This is a a test call, created by Python\nSo there.',
    requester='Simon Crouch',
    requesteremail='simon.crouch@nbt.nhs.uk',
    status='Hold - Awaiting Third Party'
    )
#grab the new SDPlus number (aka workorderid)
workorderid = details['workorderid']

#---Update a call---
#Takes in a number of parameters, most of which are optional. See code above for details.
status, details = update(workorderid, supplierRef='')
print status
print details

#---Assign a new technician to a call---
status, details = assign(workorderid, 'Gareth Lawson')
print status
print details

#---Close a call (with close comments)---
status, details = close(workorderid, 'Closed by simon crouch through code')
print status
print details

#---Hard-delete a call---
#Will only work if you've the right permissions on sdplus
status, details = delete(workorderid)
print status
print details

#---Add a note to a call---
status, details = addNote(workorderid, notesText="This is some note content, added through code.")
print status
print details

#---Add a work log to a call---
#I've personally no idea what this is, but i've implemented it anyway
status, details = addWorkLog(workorderid, workhours='8', cost='11')
print status
print details

#---Delete a work log to a call---
#I've personally no idea what this is, but i've implemented it anyway
status, details = deleteWorkLog(workorderid, workLogID='12345')
print status
print details

#---Get details from a call---
workorderid = 12345
status, details = get(workorderid)
#example code to find the supplier reference
if status:  #if returned ok
    for key, value in details.iteritems():
        print key + " - " + value   #print everything for fun (not necessary)
        if key == 'supplier ref':
            print value
'''