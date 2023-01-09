"""
DSCC Python Libraries: a collection of classes to initiate operations on the Data Services Cloud Console (DSCC).
    The whole Library is partioned into multiple classes:

    class DSCC                          - the base class
        class Audit(DSCC)               - Audit data, Events, issues
        class StorageSystem(DSCC)       - General Storage System operations  
        class Alletra6k(DSCC)           - Alletra 6k / Nimble specific command set
        class Alletra9k(DSCC)           - Alletra 9k / Primera specific command set
        class HCI(DSCC)                 - HCI command set
        class BRaaS(DSCC)               - BRaaS command set
        class ApplicationDashboar(DSCC) - Application Dashboard
        class User(DSCC)                - User commands
        class DualAuthorization(DSCC)   - Dual Authorization command set
        class FileServer(DSCC)          -   Fileserver command set
    class DsccError(Exception)          - DSCC class exception handling

    v0.2 (c) Thomas Beha, 01/09/2023
"""
from oauthlib.oauth2 import BackendApplicationClient       
from requests.auth import HTTPBasicAuth       
from requests_oauthlib import OAuth2Session 
import requests
import json 

class DSCC:
    """ 
    DSCC Base clase
    
    provides basic operations like: 
        getAccessToken
        doGet
        doPost
        doDelete
        doPatch
        doPut
        doSearch
        getTask
        getSettings
        getSettingDetail
        editSetting
        daSearch

    Internal variables:
        url             Base URL for all REST API calls
        access_token    Current access token for the DSCC access, expires every 2 hours
        headers         Rest API call header
        clientID        GreenLake Cloud Console Client Id
        clientSecret    GreenLake Cloud Console Client Secret

    The clientID and the clientSecret are needed to request a new access token.
    """

    def __init__(self, url, clientID=None, clientSecret=None):
        self.url = url                     # base URL   "https://eu1.data.cloud.hpe.com"
        self.access_token= ''               # session access token
        self.headers = {}                   # requests headers
        self.clientID = clientID
        self.clientSecret = clientSecret

    def getAccessToken(self):
        """
        Requests a new access token, updates the REST API call header 

        During the debug phase, the access token is stored in the file xmlfile, to avoid the creation of too many access token.
        Once the debug phase is completed, this feature will be removed.   
        """
        clientID = self.clientID
        clientSecret = self.clientSecret
        client = BackendApplicationClient(clientID)           
        oauth = OAuth2Session(client=client)       
        auth = HTTPBasicAuth(clientID, clientSecret)       
        self.access_token = oauth.fetch_token(token_url='https://sso.common.cloud.hpe.com/as/token.oauth2', auth=auth) 
        self.headers = {'Authorization':  'Bearer ' + str(self.access_token['access_token']), 
                        'Accept' : 'application/json'}

    def doGet(self, url):
        response = requests.get(url, verify=False, headers=self.headers)
        if(response.status_code == 200):
            return response.json()
        else:
            raise DsccError('doGet '+url, response.status_code, response)

    def doPost(self, url, body=None):
        if body:
            headers = self.headers
            headers['Content-Type'] = 'application/json'
            response = requests.post(url, headers=headers, verify=False, data=json.dumps(body))
        else:
            response = requests.post(url, verify=False, headers=self.headers)
        if((response.status_code == 200) or (response.status_code == 201) or (response.status_code == 202)):
            return response.json()
        else:
            raise DsccError('doPost '+url,response.status_code,response)        

    def doDelete(self, url):
        response = requests.delete(url, verify=False, headers=self.headers)
        if((response.status_code == 200) or (response.status_code == 201) or (response.status_code == 202)):
            return response.json()
        else:
            raise DsccError('doDelete '+url,response.status_code,response) 

    def doPatch(self, url, body=None):
        if body:
            headers = self.headers
            headers['Content-Type'] = 'application/json'
            response = requests.patch(url, headers=headers, verify=False, data=json.dumps(body))
        else:
            response = requests.patch(url, verify=False, headers=self.headers)
        if((response.status_code == 200) or (response.status_code == 201) or (response.status_code == 202)):
            return response.json()
        else:
            raise DsccError('doPost '+url,response.status_code,response)

    def doPut(self, url, body=None):           
        if body:
            headers = self.headers
            headers['Content-Type'] = 'application/json'
            response = requests.put(url,data=json.dumps(body, indent=4), verify=False, headers=headers)
        else:
            response = requests.put(url, verify=False, headers=self.headers)
        if((response.status_code == 200) or (response.status_code == 201) or (response.status_code == 202)):
            return response.json()
        else:
            raise DsccError('doPost '+url,response.status_code,response)

    def doSearch(self, query ):
        """
        Performs a search with the given query strings.
        The query parameter contains the text to search in objects. The query parameter should be url encoded.
        """
        return self.doGet(self.url+'/search', query)['items']

    def getTasks(self):
        """
        Returns a list of tasks that are visible to the user. 
        """
        return self.doGet(self.url+'/api/v1/tasks')

    def getSettings(self):
        """"
        Gets all the setting values for the current account.
        """
        return self.doGet(self.url+'/api/v1/settings')['items']
    
    def getSettingDetail(self, id):
        """
        Gets all the setting values for the current account. The service should check if the requesting user has the permission. 
        This API should also support filter, sort, select, limit and offset operations If any settings' data does not exist for 
        the current account in Settings table, return default values for all such settings.
        """
        return self.doGet(self.url+'/api/v1/settings/'+str(id))
    
    def editSetting(self, id, body):
        """
        Changes the value of the given setting.
        body:{
            "current value": "string
        }
        """
        return self.doPatch(self.url+'/api/v1/settings/'+str(id), body)

    def daSearch(self, key, value, dar):
        """
        Search a dictionary array dar for the entry where dictionary[key] == x 
        """
        for d in dar:
            if d[key] == value:
                return d
        return {"Error":"Key:Value pair -"+key+":"+value+" not found in the dataset!"}      

class DsccError(Exception):
    """ Base class for DSCC Class Errors """
    def __init__(self, location, status, message):
        self.expression = location
        self.message = message
        self.status = status

class Audit(DSCC):

    def getIssues(self):
        """
        Returns the active (state="CREATED") issues for the account, which are associated with the resource-types for 
        which the user has access. The user should also have the permission to view issues. Eg: if there are issues 
        associated with 50 resources (of different resource-types) for a customer (obtained from the request header), 
        and the user (obtained from the request headers), who has correct permissions to view the issues but has acceess 
        to only 20 of those resources (ie access to their resource types), this API will return only the issues associated with 
        those 20 resources. The grouped issues are places next to each other. The client will have to process them for any desired grouping
        """
        return self.doGet(self.url+'/api/v1/issues')

    def getIssuesMetaData(self):
        """
        Returns the list of values of category, services, and severity supported by Issues. Functionalities like query parameters, 
        filtering, sorting, grouping, and paging are not supported.
        """
        return self.doGet(self.url+'/api/v1/issues-metadata')
    
    def getIssueDetail(self, id):
        """
        Returns the active issue (state="CREATED") associated with the account (retrieved from the request headers) and with given Id
        """
        return self.doGet(self.url+'/api/v1/issues/'+str(id))       

    def getAuditEvents(self):
        # returns the audit events
        return self.doGet(self.url+'/api/v1/audit-events')

class StorageSystems(DSCC):

    def getStorageSystems(self):
        """
        Get all storage systems
        """
        return self.doGet(self.url+'/api/v1/storage-systems')["items"]
    
    def getStorageSystemDetails(self, id):
        """
        Get storage system object identified by {id}
        """
        return self.doGet(self.url+'/api/v1/storage-systems/'+str(id))

    def getAlletra9k(self):
        """
        Get all Primera / Alletra 9K storage systems
        """
        return self.doGet(self.url+'/api/v1/storage-systems/device-type1')["items"]
    
    def getAlletra6k(self):
        """
        Get all storage systems by Nimble / Alletra 6K
        """
        return self.doGet(self.url+'/api/v1/storage-systems/device-type2')["items"]
    
    def getStoragePools(self, systemId):
        """
        Get all storage pools for a device {systemId}
        """
        return self.doGet(self.url+'/api/v1/storage-systems/'+str(systemId)+'/storage-pools')['items']

    def getStorageTypes(self):
        """
        Get all device types
        """
        return self.doGet(self.url+'/api/v1/storage-systems/storage-types')

    def getVolumes(self):
        """
        Get all volumes
        """
        return self.doGet(self.url+'/api/v1/volumes')['items']

    def getVolumeSets(self):
        """
        Get all volumesets
        """
        return self.doGet(self.url+'/api/v1/volume-sets')['items']
    
    def getVolumeSetDetails(self, id):
        """
        Get volume-set identified by id
        """
        return self.doGet(self.url+'/api/v1/volume-sets/'+str(id))

    def getVolumeSetVolumes(self, id):
        """
        Get volumes identified by volume set id
        """
        return self.doGet(self.url+'/api/v1/volume-sets/'+str(id)+'/volumes')        

class Alletra6k(DSCC):

    def __init__(self, url, clientID, clientSecret, systemId ):
        super().__init__(url, clientID, clientSecret)
        self.systemId = str(systemId)
        self.systemurl = self.url+'/api/v1/storage-systems/device-type2/'+self.systemId

    # Events - Alarms

    def getEvents(self):
        # Get all events of Nimble / Alletra 6K
        return self.doGet(self.systemurl+'/events')['items']
    
    def getAlarms(self):
        # Get all alarms of Nimble / Alletra 6K
        return self.doGet(self.systemurl+'/alarms')

    def getAlarmsIdentified(self, alarmId):
        # Get all alarms of Nimble / Alletra 6K identified by {alarmId}
        return self.doGet(self.systemurl+'/alarms/'+str(alarmId))

    # Controllers

    def getControllers(self):
        # Get all controllers details by Nimble / Alletra 6K
        return self.doGet(self.systemurl+'/controllers')['items']
    
    def getControllerDetails(self, controllerId):
        # Get details of Nimble / Alletra 6K Controller identified by {controllerId}
        return self.doGet(self.systemurl+'/controllers/'+str(controllerId))

    def haltController(self, controllerId):
        # Perform halt of Nimble / Alletra 6K controller identified by {controllerId}
        return self.doPost(self.systemurl+'/controllers/'+str(controllerId)+'/actions/halt')

    # Disks

    def getDisks(self):
        # Get all disks details by Nimble / Alletra 6K
        return self.doGet(self.systemurl+'/disks')['items']

    def getDiskDetail(self, diskId):
        # Get details of Nimble / Alletra 6K disk identified by {diskId}
        return self.doGet(self.systemurl+'/disks/'+str(diskId))
    
    def editDiskDetails(self, diskId, parameter):
        """
        Edit details of Nimble / Alletra 6K disk identified by {diskId}
        Parameter (dictionary)
            disk_op string  The intended operation to be performed on the specified disk. Disk operation. Possible values: 'add', 'remove'.
            force   boolean Forcibly add a disk. Possible values: 'true', 'false'.
        """
        return self.doPost(self.systemurl+'/disks/'+str(diskId), parameter)
    
    # Performance Policy

    def getPerformancePolicies(self):
        """
        Get all performance-policies details by Nimble / Alletra 6K
        """
        return self.doGet(self.systemurl+'/performance-policies')['items']
    
    def createPerformancePolicy(self, policy):
        """
        Create Nimble / Alletra 6K performance policy in a system identified by {systemId}
        The policy is provided as a dictionary:
            app_category    string      Specifies the application category of the associated volume. Plain string. Defaults to 'Unassigned'.
            block_size      int64       Block Size in bytes to be used by the volumes created with this specific performance policy. Supported block sizes are 4096 bytes (4 KB), 8192 bytes (8 KB), 16384 bytes(16 KB), and 32768 bytes (32 KB). Block size of a performance policy cannot be changed once the performance policy is created. Defaults to 4096.
            cache           boolean     Flag denoting if data in the associated volume should be cached. Defaults to 'true'.
            cache_policy    string      Specifies how data of associated volume should be cached. Supports two policies, 'normal' and 'aggressive'. 'normal' policy caches data but skips in certain conditions such as sequential I/O. 'aggressive' policy will accelerate caching of all data belonging to this volume, regardless of sequentiality. Possible values:'normal', 'no_write', 'aggressive_read_no_write', 'disabled', 'aggressive'. Defaults to 'normal'.
            compress        boolean     Flag denoting if data in the associated volume should be compressed. Defaults to 'true'.
            dedupe_enabled  boolean     Specifies if dedupe is enabled for volumes created with this performance policy.
            description     string      Description of a performance policy. String of up to 255 printable ASCII characters.
            name            string      Name of the Performance Policy. String of up to 64 alphanumeric characters, - and . and : and space are allowed after first character.
            space_policy    string      Specifies the state of the volume upon space constraint violation such as volume limit violation or volumes above their volume reserve, if the pool free space is exhausted. Supports two policies, 'offline' and 'non_writable'. Possible values:'offline', 'login_only', 'non_writable', 'read_only', 'invalid'. Defaults to 'offline'.
        """
        return self.doPost(self.systemurl+'/performance-policies', policy)

    def getPerformancePolicyDetails(self, performancePolicyId):
        """
        Get details of Nimble / Alletra 6K performance-policy identified by {performancePolicyId}
        """
        return self.doGet(self.systemurl+'/performance-policies/'+str(performancePolicyId))
    
    def editPerformancePolicy(self,  performancePolicyId, policy):
        """
        Edit details of Nimble / Alletra 6K performance policy identified by {performancePolicyId}
        The policy data is provided as a dictionary.
        """
        # not yet implemented: PUT /api/v1/storage-systems/device-type2/{systemId}/performance-policies/{performancePolicyId}
        return "not yet implemented"    

    def deletePerformancePolicy(self,  performancePolicyId):
        """
        Remove performance-policies identified by {performancePolicyId} from Nimble / Alletra 6K
        """
        return self.doDelete(self.systemurl+'/performance-policies/'+str(performancePolicyId))

    # FC Session

    def getFCsessions(self):
        """
        Get all fibre channel sessions details of Nimble / Alletra 6K
        """
        return self.doGet(self.systemurl+'/fibre-channel-sessions')['items']
    
    def getFCsessionDetails(self, fcSessionId):
        """
        Get fibre channel session details of Nimble / Alletra 6K identified by {fcSessionId}.
        """
        return self.doGet(self.systemurl+'/fibre-channel-sessions/'+str(fcSessionId))
    
    # Network Interface

    def getNetworkInterfaces(self):
        """
        Get all network interfaces details by Nimble / Alletra 6K
        """
        return self.doGet(self.systemurl+'/network-interfaces')['items']
    
    def getNicDetails(self, networkInterfaceId):
        """
        Get all network interfaces details by Nimble / Alletra 6K identified by {networkInterfaceId}
        """
        return self.doGet(self.systemurl+'network-interfaces/'+str(networkInterfaceId))
    
    # Ports

    def getPorts(self):
        """
        Get all ports details of Nimble / Alletra 6K
        """
        return self.doGet(self.systemurl+'/ports')

    def getPortDetails(self, portId):
        """
        Get details of Nimble / Alletra 6K Port identified by {portId}.
        """
        return self.doGet(self.systemurl+'/ports/'+str(portId))
    
    def editFCport(self, portId, parameter):
        """
        Edit Nimble FC Port of Nimble / Alletra 6K
        Parameter (dictionary):
            online  boolean Identify whether the Fibre Channel interface is online.
        """
        return self.doPut(self.systemurl+'/ports/'+str(portId), parameter)
    
    # Shelves

    def getShelves(self):
        """
        Get all shelves details by Nimble / Alletra 6K
        """
        return self.doGet(self.systemurl+'/shelves')['items']

    # Storage Pools

    def getStoragePools(self):
        """
        Get all pools details by Nimble / Alletra 6K
        """
        return self.doGet(self.systemurl+'/storage-pools')['items']

    def createStoragePool(self, body):
        """
        Create storage pool from Nimble / Alletra 6K system identified by {systemId}
        body (dictionary):
            array_list          array   List of arrays identified by their IDs, in the pool.
                id              string  Identifier for array. A 42 digit hexadecimal number.
            dedupe_all_volumes  boolean Indicates if dedupe is enabled by default for new volumes on this pool. Defaults to false.
            description         string  Text description of pool. String of up to 255 printable ASCII characters. Defaults to empty string.
            name                string  Name of pool. String of up to 64 alphanumeric characters, - and . and : are allowed after first character.
        
        body example:
            {
                "array_list": [
                    {
                    "id": "2a0df0fe6f7dc7bb16000000000000000000004801"
                    }
                ],
                "dedupe_all_volumes": false,
                "description": "99.9999% availability",
                "name": "pool-1"
            }
        """
        return self.doPost(self.systemurl+'/storage-pools', body)
    
    def getStoragePoolDetails(self, storagePoolId):
        """
        Get details of Nimble / Alletra 6K pool identified by {storagePoolId}
        """
        return self.doGet(self.systemurl+'/storage-pools/'+str(storagePoolId))
    
    def editStoragePool(self, storagePoolId, body):
        """
        Edit details of Nimble / Alletra 6K pool identified by {storagePoolId}
        body (dictionary):
            array_list          array   List of arrays identified by their IDs, in the pool.
                id              string  Identifier for array. A 42 digit hexadecimal number.
            dedupe_all_volumes  boolean Indicates if dedupe is enabled by default for new volumes on this pool. Defaults to false.
            dedupe_capable      boolean Indicates whether the pool is capable of hosting deduped volumes.
            force               boolean Forcibly delete the specified pool even if it contains deleted volumes whose space is being reclaimed. Forcibly remove an array from array_list via an update operation even if the array is not reachable. There should no volumes currently in the pool for the forced update operation to succeed.
            is_default          boolean Indicates if this is the default pool.
            description         string  Text description of pool. String of up to 255 printable ASCII characters. Defaults to empty string.
            name                string  Name of pool. String of up to 64 alphanumeric characters, - and . and : are allowed after first character.
        """
        return self.doPut(self.systemurl+'/storage-pools/'+str(storagePoolId), body)

    def deleteStoragePool(self, storagePoolId):
        """
        Delete pool identified by {storagePoolId} from Nimble / Alletra 6K
        """
        return self.doDelete(self.systemurl+'/storage-pools/'+str(storagePoolId))

    def mergeStoragePool(self, storagePoolId, body):
        """
        Merge pool identified by {storagePoolId} from Nimble / Alletra 6K
        body:
            target_pool_id  string  ID of the target pool. A 42 digit hexadecimal number.
            force           boolean Forcibly merge the specified pool into target pool. Defaults to false.
        """
        return self.doPost(self.systemurl+'/storage-pools/'+str(storagePoolId)+'/actions/merge', body)
    
    def getStoragePoolCapacity(self, storagePoolId):
        """
        Get storage pool capacity trend data of Nimble / Alletra 6K storage pool identified by {storagePoolId}
        """
        return self.doGet(self.systemurl+'/storage-pools/'+str(storagePoolId)+'/capacity-history')

    def getStoragePoolPerformanceHistory(self, storagePoolId):
        """
        Get performance trend data of Nimble / Alletra 6K storage pool identified by {storagePoolId}
        """
        return self.doGet(self.systemurl+'/storage-pools/'+str(storagePoolId)+'/performance-history')

    def getStoragePoolPerformance(self, storagePoolId):
        """
        Get performance statistics of Nimble / Alletra 6K storage pool identified by {storagePoolId}
        """
        return self.doGet(self.systemurl+'/storage-pools/'+str(storagePoolId)+'/performance-statistics')

    # System

    def getSystem(self):
        """
        Get Nimble / Alletra 6K object 
        """
        return self.doGet(self.systemurl)

    def editSystem(self, body):
        """
        Edit settings of Nimble / Alletra 6K system
        body:
            auto_switchove_enabled                  boolean Whether automatic switchover of Group management services feature is enabled.
            autoclean_unmanaged_snapshots_enabled   boolean Whether auto-clean unmanaged snapshots feature is enabled.
            autoclean_unmanaged_snapshots_ttl_unit  int64   Unit for unmanaged snapshot time to live.
            cc_mode_enabled                         boolean Enable or disable Common Criteria mode.
            date                                    int64   Unix epoch time local to the group. Seconds since last epoch i.e. 00:00 January 1, 1970. Setting this along with ntp_server causes ntp_server to be reset.
            default_iscsi_target_scope              string  Newly created volumes are exported under iSCSI Group Target or iSCSI Volume Target.
            group_snapshot_ttl                      int64   Snapshot Time-to-live(TTL) configured at group level for automatic deletion of unmanaged snapshots. Value 0 indicates unlimited TTL.
            group_target_name                       string  Iscsi target name for this group. Plain string.
            name                                    string  Name of the group. String of up to 64 alphanumeric characters, - and . and : are allowed after first character.
            ntp_server                              string  Either IP address or hostname of the NTP server for this group.
            tdz_enabled                             boolean Is Target Driven Zoning (TDZ) enabled on this group.
            tdz_prefix                              string  Target Driven Zoning (TDZ) prefix for peer zones created by TDZ.
            timezone                                string  Timezone in which this group is located. Plain string.
            tlsv1_enabled                           boolean Enable or disable TLSv1.0 and TLSv1.1.
        """
        return self.doPut(self.systemurl, body)
    
    def getArrays(self):
        """
        Get all arrays details by Nimble / Alletra 6K
        """
        return self.doGet(self.systemurl+'/arrays')['items']

    def getCapacityHistory(self):
        """
        Get capacity trend data for a storage system Nimble / Alletra 6K
        """
        return self.doGet(self.systemurl+'/capacity-history')
    
    def getPerformanceHistory(self):

        """
        Get performance trend data for a storage system Nimble / Alletra 6K
        """
        return self.doGet(self.systemurl+'/performance-history')

    # Volumes

    def getVolumes(self):
        """
        Get details of volumes identified with {systemId}
        """
        return self.doGet(self.url+'/api/v1/storage-systems/'+self.systemId+'/volumes')['items']

class Alletra9k(DSCC):

    def __init__(self, url, clientID, clientSecret, systemId ):
        super().__init__(url, clientID, clientSecret)
        self.systemId = str(systemId)
        self.systemurl = self.url+'/api/v1/storage-systems/device-type1/'+self.systemId

    def getCertificates(self):
        """
        Get array certificates by Primera / Alletra 9K
        """
        return self.doGet(self.systemurl+'/certificates')['items']

    # System

    def getApplicationSummary(self):
        """
        Get Application Summary for a storage system Primera / Alletra 9K
        """
        return self.doGet(self.systemurl+'/application-summary')
    
    def getCapacity(self):
        """
        Get system capacity for a storage system Primera / Alletra 9K
        """
        return self.doGet(self.systemurl+'/capacity-summary')
    
    def getCapacityHistory(self):
        return self.doGet(self.systemurl+'/capacity-history')

    # Storage Pools

    def getStoragePools(self):
        """
        Get all storage-pools details by Primera / Alletra 9K
        """
        return self.doGet(self.systemurl+'/storage-pools')['items']
    
    def getStoragePoolDetails(self, id):
        """
        Get details of Primera / Alletra 9K storage-pool identified by {id}
        """
        return self.doGet(self.systemurl+'/storage-pools/'+str(id))

    def getStoragePoolVolumes(self, id):
        """
        Get all volumes for storage-pool identified by {id} of Primera / Alletra 9K
        """
        return self.doGet(self.systemurl+'/storage-pools/'+str(id)+'/volumes')

    # Volume Commands

    def getVolumes(self):
        """
        Get details of volumes identified with {systemId}
        """
        return self.doGet(self.url+'/api/v1/storage-systems/'+self.systemId+'/volumes')['items']
        #return self.doGet(self.systemurl+'/volumes') has a 400 Response (bad request) as a result!
    
    def createVolume(self, body):
        """
        Create volume for a storage system Primera / Alletra 9K
        body: (dictionary)
            comments                string      comments
            count                   int         Volumes count
            dataReduction           boolean     Data Reduction on/off
            name                    string      Volume name (required)
            sizeMib                 int         Size in MiB (required)
            snapCpg                 string      Snap CPG   
            snapshotAllocWarning    int         Snapshot Alloc Warning
            userAllocWarning        int         User Alloc Warning
            userCpg                 string      User CPG

            Example:
            {
                "comments": "test",
                "count": 2,
                "dataReduction": true,
                "name": "<resource_name>",
                "sizeMib": 16384,
                "snapCpg": "SSD_r6",
                "snapshotAllocWarning": 5,
                "userAllocWarning": 5,
                "userCpg": "SSD_r6"
            }    
        """
        return self.doPost(self.systemurl+'/volumes', body=body)

    def deleteVolume(self, volumeId):
        """
        Remove volume identified by {volumeId} from Primera / Alletra 9K
        """
        return self.doDelete(self.systemurl+'/volumes/'+str(volumeId))

    def getVolumeDetails(self, volumeId):
        """
        Get details of Primera / Alletra 9K Volume identified by {volumeId}
        """
        return self.doGet(self.systemurl+'/volumes/'+str(volumeId))

    def editVolume(self, volumeId, body):
        """
        Edit volume identified by {volumeId} from Primera / Alletra 9K

        body:

            dataReduction           boolean     Data Reduction on/off
            name                    string      Volume name (required)
            sizeMib                 int         Size in MiB (required)
            snapshotAllocWarning    int         Snapshot Alloc Warning
            userAllocWarning        int         User Alloc Warning
            userCpgName             string      User CPG  

        Attention: Only add the parameter that are changing into the body

        """
        return self.doPut(url=self.systemurl+'/volumes/'+str(volumeId), body=body)
    
    def exportVolume(self, volumeId, body):

        """
        Export vlun for volume identified by {volumeId} from Primera / Alletra 9K 

        body:
            autoLun         boolean     Auto Lun
            hostGroupIds    [string]    HostGroups
            maxAutoLun      int64       Number of volumes
            noVcn           boolean     No VCN
            override        boolean     Override
            position        string      Position
            proximity       enum        Host proximity setting for Active Peer Persistence configuration.
                                        Allowed: PRIMARY, SECONDARY, ALL
            
            Example:
            {
                "autoLun": true,
                "hostGroupIds": [
                    "string"
                ],
                "maxAutoLun": 1,
                "noVcn": true,
                "override": true,
                "position": "position_1",
                "proximity": "PRIMARY"
            }
        """
        return self.doPost(self.systemurl+'/volumes/'+str(volumeId)+'/export', body=body)

    def unexportVolume(self, volumeId, body):
        """
        Unexport vlun for volume identified by {volumeId} from Primera / Alletra 9K
        body:
            hostGroupIds    [string]    HostGroups 
        """
        return self.doPost(self.systemurl+'/volumes/'+str(volumeId)+'/un-export', body=body)

    def getVolumeCapacityHistory(self, volumeId):
        """
        Get volume capacity trend data of Primera / Alletra 9K Volume identified by {volumeId}
        """
        return self.doGet(self.systemurl+'/volumes/'+str(volumeId)+'/capacity-history')

    def getVolumePerformanceHistory(self, volumeId):
        """
        Get performance trend data of Primera / Alletra 9K Volume identified by {volumeId}
        """
        return self.doGet(self.systemurl+'/volumes/'+str(volumeId)+'/performance-history')

    def getVolumePerformance(self, volumeId):
        """
        Get performance statistics of Primera / Alletra 9K Volume identified by {volumeId}
        """
        return self.doGet(self.systemurl+'/volumes/'+str(volumeId)+'/performance-statistics')

    # Volume Sets Commands

    def getVolumeSets(self):
        """
        Get all volume sets 
        """
        return self.doGet(self.url+'/api/v1/storage-systems/'+self.systemId+'/volume-sets')['items']

    def getVolumeSetDetails(self, id):
        """
        Get volume set details identified by id
        """
        return self.doGet(self.systemurl+'/volume-sets/'+str(id))

    def getApplicationSets(self):
        """
        Get all applicationset details for Primera / Alletra 9K
        """
        return self.doGet(self.systemurl+'/applicationsets')['items']
    
    # Snapshot Commands

    def getVolumeSnapshots(self, volumeId):
        """
        Get snapshot details  of Primera / Alletra 9K Volume identified by {volumeId}
        """
        return self.doGet(self.systemurl+'/volumes/'+str(volumeId)+'/snapshots')        

    def createVolumeSnapshot(self, volumeId, body):
        """
        Create snapshot for volumes identified by {volumeId}
        body:
            comment         string      comment
            customName      customName  Snapshot name
            expireSecs      int         Expiration time in seconds
            namePattern     enaum       name pattern (required), Allowed: PARENT_TIMESTAMP, PARENT_SEC_SINCE_EPOCH, CUSTOM
            readOnly        boolean     Read only or Read/Write
            retainSecs      int64       retain time in seconds

            Example:
            {
                "comment": "",
                "customName": "snap1",
                "expireSecs": 86400,
                "namePattern": "PARENT_TIMESTAMP",
                "readOnly": false,
                "retainSecs": 86400
            }
        """
        return self.doPost(self.systemurl+'/volumes/'+str(volumeId)+'/snapshots')

    # Node Commands
    def getNodes(self):
        # Get details of Primera / Alletra 9K Nodes
        return self.doGet(self.systemurl+'/nodes')['items']

    def getNodeDetails(self, nodeId):
        # Get details of Primera / Alletra 9K Node identified by {id}
        return self.doGet(self.systemurl+'/nodes/'+str(nodeId))
    
    def locateNode(self, nodeId, locate):
        """
        Locate node of Primera / Alletra 9K identified by {id}
        Locae on/off will be controlled by the dictionary:
        locale={
            "locate":  true/false
        }
        """
        return self.doPost(self.systemurl+'/nodes/'+str(nodeId), locate)

    def getNodePerformance(self, nodeId):
        # Get component performance statistics details of Primera / Alletra 9K node idenfified by {nodeId}
        return self.doGet(self.systemurl+'/nodes/'+str(nodeId)+'/component-performance-statistics')

    def getNodeComponent(self, component, nodeId):
        # Get details of Primera / Alletra 9K Node components identified by {nodeId}
        # possible components: cards, cpus, drives, mcus, mems, powers, batteries 
        return self.doGet(self.systemurl+'/nodes/'+str(nodeId)+'/node-'+str(component))
    
    def getNodeComponentDetails(self, component, nodeId, id):
        # Get details of Primera / Alletra 9K Node component identified by {nodeId} and {id}
        # possible components: cards, cpus, drives, mcus, mems, powers, batteries 
        return self.doGet(self.systemurl+'/nodes/'+str(nodeId)+'/node-'+str(component)+'/'+str(id))
 
    # Enclosure Commands
    def getEnclosures(self):
        """
        Get details of Primera / Alletra 9K Enclosures
        """
        return self.doGet(self.systemurl+'/enclosures')['items']
    
    def getEnclosureDetails(self, enclosureId):
        """
        Get details of Primera / Alletra 9K Enclosure identified by {enclosureId}
        """
        return self.doGet(self.systemurl+'/enclosures/'+str(enclosureId))

    def getEnclosureCards(self, enclosureId):
        """
        Get details of Primera / Alletra 9K Enclosure Cards identified by {enclosureId}
        """
        return self.doGet(self.systemurl+'/enclosures/'+str(enclosureId)+'/enclosure-cards')

    def getEnclosureCardPorts(self, enclosureId):
        """
        Get details of Primera / Alletra 9K Enclosure Card Ports identified by {enclosureId}
        """
        return self.doGet(self.systemurl+'/enclosures/'+str(enclosureId)+'/enclosure-card-ports')

    def getEnclosureDisks(self, enclosureId):
        """
        Get details of Primera / Alletra 9K Enclosure Disks identified by {enclosureId}
        """
        return self.doGet(self.systemurl+'/enclosures/'+str(enclosureId)+'/enclosure-disks')

    def getEnclosureFans(self, enclosureId):
        """
        Get details of Primera / Alletra 9K Enclosure Disks identified by {enclosureId}
        """
        return self.doGet(self.systemurl+'/enclosures/'+str(enclosureId)+'/enclosure-fans')

    def getEnclosurePowers(self, enclosureId):
        """
        Get details of Primera / Alletra 9K Enclosure Powers identified by {enclosureId}
        """
        return self.doGet(self.systemurl+'/enclosures/'+str(enclosureId)+'/enclosure-powers')

    def getEnclosureSleds(self, enclosureId):
        """
        Get details of Primera / Alletra 9K Enclosure Sleds identified by {enclosureId}
        """
        return self.doGet(self.systemurl+'/enclosures/'+str(enclosureId)+'/enclosure-sleds')

    # Port Commands
    def getPorts(self):
        """
        Get details of Primera / Alletra 9K Ports
        """
        return self.doGet(self.systemurl+'/ports')['items']

    def getPortDetails(self, id):
        """
        Get details of Primera / Alletra 9K Port identified by {id}
        """
        return self.doGet(self.systemurl+'/ports/'+str(id))
    
    def changePortStatus(self, id, portStatus):
        """
        Port enable disable identified by {id} from Primera / Alletra 9K identified by {systemId}
        portStatus: Dictionary {"portEnable": true/false}
        """
        return self.doPost(self.systemurl+'/ports/'+str(id), portStatus)

    def clearPort(self, id, ipType):
        """
        Clear the details of the ports identified by {id} from Primera / Alletra 9K identified by {systemId}
        ipType string  For RCIP ports, the IP version of the address that needs to be cleared from the port. Either the IPv4 address or IPv6 address or both addresses can be cleared. Possible values: v4,v6,both
        """    
        return self.doPost(self.systemurl+'/ports/'+str(id)+'/clear', ipType)

    def editIscsiPort(self, id, parameter):
        """
        Edit iscsi ports identified by {id} from Primera / Alletra 9K identified by {systemId}
        Parameters (dictionary):
            gatewayAddress      ipv4    Gateway address to edit to for IPv4 address
            ipAddress           ipv4    IPv4 address to edit to
            label               string  label of the port to edit to
            mtu                 string  MTU to edit to. Possible Values: "1500", "9000"
            netMask             ipv4    NetMask address to edit to for IPv4 address
            sendTargetGroupTag  Uint32              
        """
        return self.doPut(self.systemurl+'/ports/'+str(id)+'/edit-iscsi', parameter)    
    
    def editRcipPort(self, id, parameter):
        """
        Edit rcip ports identified by {id} from Primera / Alletra 9K identified by {systemId}
        parameter dictionary:
            gatewayAddress      ipv4    Gateway address to edit to for IPv4 address
            gatewayAddressV6    string  Gateway address to edit to for IPv6 address
            ipAddress           ipv4    IPv4 address to edit to
            ipAddressV6         string  IPv6 address to edit to
            label               string  label of the port to edit to
            mtu                 string  MTU to edit to. Possible Values: "1500", "9000"
            netMask             ipv4    NetMask address to edit to for IPv4 address
            netMaskV6           string  NetMask address to edit to for IPv6 address
            speedConfigured     string  Configured speed. Possible Values: auto, "1", "2", "4", "8", "16", "32"
        """
        return self.doPut(self.systemurl+'/ports/'+str(id)+'/edit-rcip', parameter)

    def editFcPort(self, id, parameter):
        """
        Edit ports identified by {id} from Primera / Alletra 9K identified by {systemId}
        parameter dictionary:
            configMode          string  Configuration of Port. Possible Values: Disk, Host, RCFC, Peer
            connectionType      string  Port connection Type. Possible Values: Point, Loop
            interuptCoalesce    boolean Port interuptCoalesce enabled or not
            label               string  Port name
            speedConfigured     string  Port speed. Possible Values: auto, "4", "8", "16", "32"
            uniqueWWN           boolean Port uniquewwn enabled or not
            vcn                 boolean VLUN change notification enabled or not
        """
        return self.doPut(self.systemurl+'/ports/'+str(id)+'/fc', parameter)

    def initializePort(self, id):
        """
        Initialize the details of the ports identified by {id} from Primera / Alletra 9K identified by {systemId}
        """
        return self.doPost(self.systemurl+'/ports/'+str(id)+'/initialize')

    def pingIscsiPort(self, id, parameter):
        """
        Ping iscsi ports identified by {id} from Primera / Alletra 9K identified by {systemId}
        Parameter (dictionary)
            ipAddress   ipv4    IP Address to ping
            ipAddressv6 ipv6    IP Address to ping
            pingCount   int     ping count
        """
        return self.doPost(self.systemurl+'/ports/'+str(id)+'/ping-iscsi', parameter)
    
    def pingRcipPort(self, id, parameter):
        """
        Ping rcip ports identified by {id} from Primera / Alletra 9K identified by {systemId}
        Parameter (dictionary)
            ipAddress   ipv4    IP Address to ping
            ipAddressv6 ipv6    IP Address to ping
            pingCount   int     ping count
            PacketSize  int     Packet size of the ping
            WaitTime    int     Wait time   
        """
        return self.doPost(self.systemurl+'/ports/'+str(id)+'/ping-rcip', parameter)

    # System Setting

    def getAlertContacts(self):
        """
        Get alert-contact details for a storage system Primera / Alletra 9K
        """
        return self.doGet(self.systemurl+'/alert-contacts')
    
    def addAlertContact(self, body):
        """
        Add Alert/Mail contact details
        body {
            "company": "HPE",
            "companyCode": "HPE",
            "country": "US",
            "fax": "fax_id",
            "firstName": "john",
            "includeSvcAlerts": false,
            "lastName": "kevin",
            "notificationSeverities": [
            0
            ],
            "preferredLanguage": "en",
            "primaryEmail": "kevin.john@hpe.com",
            "primaryPhone": "98783456",
            "receiveEmail": true,
            "receiveGrouped": true,
            "secondaryEmail": "winny.pooh@hpe.com",
            "secondaryPhone": "23456789"
        }
        """
        return self.doPut(self.systemurl+'/alert-contacts', body)

    def deleteAlertContact(self, id):
        """
        Delete Alert/Email contact of storage system Primera / Alletra 9K identified by {id}
        """
        return self.doDelete(self.systemurl+'/alert-contacts/'+str(id))
    
    def editAlertContact(self, id, body):
        """
        Edit Alert/Email contact details of storage system Primera / Alletra 9K identified by {id}
        body {
            "company": "HPE",
            "companyCode": "HPE",
            "country": "US",
            "fax": "fax_id",
            "firstName": "john",
            "includeSvcAlerts": false,
            "lastName": "kevin",
            "notificationSeverities": [
            0
            ],
            "preferredLanguage": "en",
            "primaryEmail": "kevin.john@hpe.com",
            "primaryPhone": "98783456",
            "receiveEmail": true,
            "receiveGrouped": true,
            "secondaryEmail": "winny.pooh@hpe.com",
            "secondaryPhone": "23456789"
        }
        """
        return self.doPut(self.systemurl+'/alert-contacts/'+str(id), body)

class HCI(DSCC):

    def getLimits(self):
        # A Map (key: limit name, value: limit value) of limits returned. This is expected to be evolving map 
        # of limits. Sole limit returned today as an explicit map key is maxHypervisorClustersPerHciSystem, which 
        # indicates maximum number of hypervisor clusters that any HCI system can support.
        return self.doGet(self.url+'/hci-limits')
    
    def getClusterCapacity(self):
        # Get storage usage summary information across all the HCI systems for the customer. 
        # Get a distribution of HCI systems in different ranges of storage usage.
        return self.doGet(self.url+'/hci/v1/dashboard/capacity/clusters')

    def getVmCapacity(self):
        # Get storage usage summary information across all the Virtual machines in HCI systems for the customer. 
        # Get a distribution of Virtual machines in different ranges of storage usage.
        return self.doGet(self.url+'/hci/v1/dashboard/capacity/vms')

    def getVmPerformance(self):
        # Get IOPS and latency summary information across all the Virtual machines in HCI systems for the customer. 
        # Get TopN Virtual machines by IOPS and latency.
        return self.doGet(self.url+'/hci/v1/dashboard/performance/vms')
    
    def getProtection(self):
        # Get summary of protection (through Greenlake backup and recovery service) states of virtual machines across all the HCI systems for the customer.
        return self.doGet(self.url+'/hci/v1/dashboard/protection')

    def getSummary(self):
        # Get HCI systems count and count of Virtual Machines in all the HCI systems for the customer.
        return self.doGet(self.url+'/hci/v1/dashboard/summary')
    
    def getSystemsUtilization(self):
        # Get CPU and memory utilization information across all the HCI systems for the customer.
        return self.doGet(self.url+'/hci/v1/dashboard/utilization')
    
    def getSystems(self):
        # Returns a list of HCI system objects with aggregated information about associated storage, compute, networking and virtualization.
        return self.doGet(self.url+'/hci/v1/systems')

    def getSystemCapacity(self, systemId):
        # Show a HCI system's capacity in HCI system details page view.
        return self.doGet(self.url+'/hci/v1/systems/'+str(systemId)+'/capacity')

    def getSystemProtection(self, systemId):
        # Show summary of protection (through Greenlake backup and recovery service) states of a HCI system's virtual machines in HCI system details page view. 
        return self.doGet(self.url+'/hci/v1/systems/'+str(systemId)+'/protection')

    def getSystemRelatedInfo(self, systemId):
        # Show certain related information in HCI system details page view. 
        return self.doGet(self.url+'/hci/v1/systems/'+str(systemId)+'/related-info')

    def getSystemServer(self, systemId):
        # Lists a HCI system's servers. This is a list of servers with their associated virtualization persona attributes aggregated to be displayed on UI.
        return self.doGet(self.url+'/hci/v1/systems/'+str(systemId)+'/servers')  

    def getSystemArrays(self, systemId):
        # Lists storage arrays of HCI system's storage system in HCI system details page view.
        return self.doGet(self.url+'/hci/v1/systems/'+str(systemId)+'/storage-arrays')

    def getSystemStoragePools(self, systemId):
        # Lists storage pools of HCI system's storage system in HCI system details page view.
        return self.doGet(self.url+'/hci/v1/systems/'+str(systemId)+'/storage-pools')   

    def getSystemStorageReplicationPartners(self, systemId):
        # Lists replication partners of HCI system's storage system in HCI system details page view.
        return self.doGet(self.url+'/hci/v1/systems/'+str(systemId)+'/storage-replication-partners')                  

    def getSystemHealth(self, systemId):
        # Show Counts of HCI system's high level components in HCI system details page view.
        return self.doGet(self.url+'/hci/v1/systems/'+str(systemId)+'/system-health')   

    def getServers(self, clusterId):
        # List of servers in the HCI system are returned provided the user has permissions to view these servers. 
        # The response can be paged by using the limit and offset query parameters and filtered, sorted and ordered by using 
        # the filter and sort query parameters. Specific attributes be obtained using the select parameter. Will be changed to /hci-systems/{systemId}/servers.
        return self.doGet(self.url+'/hci-clusters/'+str(clusterId)+'/servers')
    
    def getServerDetails(self, clusterId, serverId):
        # Details of the specified server in the HCI system are returned provided the user has permissions to view this server. 
        # Will be changed to /hci-systems/{systemId}/servers/{serverId}
        return self.doGet(self.url+'/hci-clusters/'+str(clusterId)+'/servers/'+str(serverId))

    def getToRSwitches(self, clusterId):
        # List of switches used by the HCI system are returned provided the user has permissions to view these switches. 
        # The response can be paged by using the limit and offset query parameters and filtered, sorted and ordered by using the filter, and sort query parameters. 
        # Specific attributes be obtained using the select parameter. Will be changed to /hci-systems/{systemId}/switches.    
        return self.doGet(self.url+'/hci-clusters/'+str(clusterId)+'/switches')
    
    def getToRSwitchDetails(self, clusterId, switchId):
        # Details of the specified switch in the cluster are returned provided the user has permissions to view this switch. 
        # Will be changed to /hci-systems/{systemId}/switches/{switchId}.
        return self.doGet(self.url+'/hci-clusters/'+str(clusterId)+'/switches/'+str(switchId))

    def getClusterConfigurationAnalysis(self, clusterId):
        # Returns config analysis rules execution reports for HCI System referenced by 'clusterId' parameter.
        return self.doGet(self.url+'/api/v1/hci-clusters/'+str(clusterId)+'/configuration-analysis-report')

    def initateClusterConfigurationAnalysis(self, clusterId):
        # Initiates execution of config analysis rules execution for the HCI System specified by 'clusterId' parameter
        return self.doPost(self.url+'/api/v1/hci-clusters/'+str(clusterId)+'/configuration-analysis-report') 

    def getConfigAnalysisList(self):
        # Returns latest config analysis rules execution report for all HCI Systems
        return self.doGet(self.url+'/api/v1/hci-clusters/configuration-analysis-reports') 

    def getConfigAnalysisReport(self, clusterId, reportId ):
        #  Returns latest config analysis rules execution report identified by 'reportId' parameter for HCI System referenced by 'clusterId' parameter.
        return self.doGet(self.url+'/api/v1/hci-clusters/'+str(clusterId)+'/configuration-analysis-reports/'+str(reportId))

    def getClusters(self):
        # Returns a list of HCI systems that the user has permissions to view. The response can be paged by using the limit and offset query parameters and filtered, sorted 
        # and ordered by using the filter and sort query parameters. Specific attributes be obtained using the select parameter. Will be changed to /hci-systems.
        return self.doGet(self.url+'/hci-clusters')

    def getClusterDetails(self, clusterId):
        # Details of the specified HCI system are returned provided the user has permissions to view this system. Will be changed to /hci-systems/{systemId}.
        return self.doGet(self.url+'/hci-clusters/'+str(clusterId))

    def addCluster(self, hciSystemId, clustername, datacenter, configureVds):
        # Initiates addition of the specified hypervisor cluster to HCI system, provided the user has permissions to update this HCI system 
        # i.e. data-services.hci-cluster.update. Returns a task identifier to be used by clients to track progress of the hypervisor cluster 
        # addition. Notes: URI will be changed to POST /hci-systems/{hciSystemId}/hypervisor-clusters. 
        # Permission data-services.hci-cluster.update will be renamed as data-services.hci-system.update.
        # Parameter:
        #     hciSystemId  - string
        #     clustername  - string
        #     datacenter   - string
        #     configureVds - boolean
        dict={
            "configureVds": configureVds,
            "hypervisorClustername": clustername,
            "vsphereDatacenterName": datacenter
        }
        body = json.dumps(dict, indent=4)
        return self.doPost(self.url+'/hci-clusters/'+str(hciSystemId)+'/hypervisor-clsuters', body)

class BRaaS(DSCC):

    def getProtectionJobsReport(self):
        # Fetches summary and detailed report for protection jobs of different assets e.g., details about a collection of protection job executions 
        # for VMware, AWS or for an Asset Type etc. Note: When 'Accept' header is 'text/csv', a CSV formatted content in form of file is returned 
        # back to the client. Currently, maximum limit on the number of records in the CSV file is kept at 5000.
        return self.doGet(self.url+'/api/v1/backup-recovery-reports/protection-jobs')
    
    def getProtectionStatus(self):
        # Fetches summary report for protection status of different assets e.g., details about AWS Machine instances , VMware Virtual Machines etc.
        return self.doGet(self.url+'/api/v1/backup-recovery-reports/protection-status')

class ApplicationDashboard(DSCC):
    
    def getInventorySummary(self):
        # Fetches summary for aggregated counts of assets for different hypervisor managers or application types e.g., number of Virtual Machines, Data Stores, VCenters etc .
        return self.doGet(self.url+'/app-data-management/v1/dashboard/inventory-summary')
        
    def getJobExecutionSummary(self):
        # Fetch aggregated completed or failed status counts bucketized for different date time intervals.
        return self.doGet(self.url+'/app-data-management/v1/dashboard/job-execution-status-summary')
    
    def getProtectedResources(self):
        # Fetches summary for number of resources protected for different hypervisor managers or application types e.g., number of Virtual Machines protected for different vcenter servers.
        return self.doGet(self.url+'/app-data-management/v1/dashboard/protections-summary')

    def getSubscriptionUsage(self):
        # Fetch details of the subscription like subscription-type, start-date, end-date, etc and usage information like protected VMs, EBS, EC2, etc.
        return self.doGet(self.url+'/app-data-management/v1/dashboard/subscription-and-usage-summary')

    def getBackupCapacityUsage(self):
        # Fetch capacity usage summary for backups on OPE/local and cloud storage.
        return self.doGet(self.url+'/app-data-management/v1/dashboard/backup-usage-usage-summary')    

class User(DSCC):

    def getUserPermissions(self):
        # Return a list of user permissions scoped by groups. The returned list of permissions/groups is based upon the supplied filter.
        return self.doGet(self.url+'/api/v1/group-access')

    def getResourceTypes(self):
        # Return resource types on which the user has a read permission. The returned list will be based upon the supplied filter. 
        # If no filter was provided, all resource types for which the user has a read permission on will be returned
        return self.doGet(self.url+'/api/v1/resource-types')    

    def getDevice(self):
        """
        Returns a list of devices associated with the customer that have yet to be or have just been initialized. This includes devices that are:
           onboarded
           uninitialized
           initializing
           initialized (Note that such devices will only be shown for a short period of time)
           initialization_failed 
        """
        return self.doGet(self.url+'/api/v1/devices')

    def getDeviceDetails(self, id):
        # Get a specific device
        return self.doGet(self.url+'/api/v1/devices/'+str(id))
    
    def getSetupProgress(self, id):
        # Get the specific setup progress for a device
        return self.doGet(self.url+'/api/v1/devices/setup-progress/'+str(id))

    def getGroups(self):
        # returns all groups for a customer
        return self.doGet(self.url+'/api/v1/groups')
    
    def getGroupDetails(self, id):
        # returns group for a customer
        return self.doGet(self.url+'/api/v1/groups/'+str(id))

    def getGroupAssociatedResources(self, id):
        # returns list of resources associated with a specific group.
        return self.doGet(self.url+'/api/v1/groups/'+str(id)+'/associated-resources')
    
    def createGroup(self, description, name):
        # Create a new group
        dict = {
            "description": description,
            "name": name
        }
        body=json.dumps(dict, indent=4)
        return self.doPost(self.url+'/api/v1/groups/', body)          

    def deleteGroup(self, id):
        # Delete a Specific Group.
        return self.doDelete(self.url+'/api/v1/groups/'+str(id))
    
    def getSettings(self):
        """
        Gets all the setting values for the current account.
        """
        return self.doGet(self.url+'/api/v1/settings')
    
class DualAuthorization(DSCC):

    def getDualAuthOperations(self):
        # Gets all operations for Dual Auth, which satisfy the following conditions: belong to current account. belong to the resource 
        # types (Application Resource) for which the user has read permission User should have permission to read pending operations
        return self.doGet(self.url+'/api/v1/dual-auth-operations')

    def getDualAuthOperationDetail(self, id):
        # Returns Dual-Auth operation belonging to current account only. Belonging to the resource type (Application Resource) for 
        # which the user has read permission User should have permission to read pending operations
        return self.doGet(self.url+'/api/v1/dual-auth-operations/'+str(id))

    def patchDualAuthOperation(self, id, checkedStatus):
        # Approve/Deny the pending operation by changing its state in DB.
        # checkedStatus: enum Allowed:   APPROVED, CANCELLED, DELETED
        #   dict = {
        #       "checkedStatus": checkedStatus
        #   }
        return self.doPatch(self.url+'/api/v1/dual-auth-operations/'+str(id), checkedStatus)  

class FileServer(DSCC):
    pass  