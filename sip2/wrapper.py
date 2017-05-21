
class Sip2Wrapper:
    """ A wrapper for the Sip2 class that makes sip requests more convenient.

    Concept:
    - All request/response pairs from the Sip2 class are wrapped into one 
      method. The wrapped pairs are prefixed with sip_ followed by Sip2 class 
      (and protocol definition manual) name. 
    - return, get ...

    @package
    @license    MIT License
    @author     Tobias Zeumer <tzeumer@verweisungsform.de>
    @copyright  2016 Tobias Zeumer <tzeumer@verweisungsform.de>
    @link       Python: ???
    @version    $Id: sip2.class.php 28 2010-10-08 21:06:51Z cap60552 $
    @requires:  Python 3.4 (I guess)
    
    @example 1: First configure some basic setting. Example with all settings:
    sip2Params = {
        'hostName'       : 'my-asc.ils.net',
        'hostPort'       : 1294,
        'maxretry'       : 0,
        'socket_timeout' : 3,
        'tlsEnable'      : True,
        'tlsAcceptSelfsigned' : True,
        'hostEncoding'   : 'utf-8', 
        'fldTerminator'  : '|',
        'msgTerminator'  : "\r",
        'withCrc'        : True,
        'withSeq'        : True,
        'UIDalgorithm'   : 0,
        'PWDalgorithm'   : 0,
        'language'       : '000',
        'institutionId'  : 'My Test Institute',
        'terminalPassword': '',
        'scLocation'     : 'My Test SC Location',
        'patron'         : '12345',
        'patronpwd'      : 'secret',
        'logfile_path'   : '',
        'loglevel'       : 'WARNING',
        
    }
    
    @example 2: And now a complete initialization example (with reduced config 
    options - you probably won't change most of the defaults anyway).
    
    from sip2.wrapper import Sip2Wrapper
    sip2Params = {
        'hostName'       : 'my-asc.ils.net',
        'hostPort'       : 1294,
        'tlsEnable'      : True,
        'tlsAcceptSelfsigned' : True,
        'hostEncoding'   : 'utf-8', 
        'language'       : '000',
        'institutionId'  : 'My Test Institute',
        'scLocation'     : 'My Test SC Location',
    }
    # Create instance and automatically connect
    wrapper = Sip2Wrapper(sip2Params, True, 'Gossip')

    # Login with device and automatically do a self check
    wrapper.login_device('user', 'pass', True)

    # Return item - no patron login required
    wrapper.sip_item_checkin('itemBarcode') 

    # Probably check a scanned item
    wrapper.sip_item_information('itemBarcode')

    #  Ask patron to log in
    wrapper.login_patron('patronName', 'patronPass')
    
    # Ask patron Checkout something
    wrapper.sip_item_checkout('itemBarcode')
   
    # Before shutting down device, logout
    wrapper.disconnect()

    """

    def __init__(self, sip2Params = {}, autoConnect = True, version = 'Sip2'):
        """ Constructor
        @param array sip2Params    Array of key value pairs that will set the 
                   corresponding member variables in the underlying sip2 class
        @param boolean autoConnect Defaults to True and automatically connects
        @param string version      Currently either Sip2 (default) or Gossip
        """
        
        #set private     Class properties
        self._sip2              = None
        # @var object sip2 object
        self._connected         = False
        # @var boolean   Connected state toggle

        self._inPatronSession   = False
        # @var boolean   Patron session state toggle
        self._patronInfo        = None
        # @var array     Patron information
        self._patronStatus      = None
        # @var array     Patron status
        self._scStatus          = None
        # @var array Acs status

        
        """ Begin initialization """
        if version == 'Sip2':
            from sip2.sip2 import Sip2
            sip2 = Sip2()
        elif version == 'Gossip':
            from sip2.sip2 import Gossip
            sip2 = Gossip()        
        else:
            raise RuntimeError('Version can only be Sip2 or Gossip')

        # Set properties, warn if property does not exist        
        for key,value in sip2Params.items():
            attrExists = getattr(sip2, key, 'NoneProperty')
            if attrExists == 'NoneProperty':
                print ("'%s' with value '%s' is not a valid property." % (key, value))
            else:
                setattr(sip2, key, value) 
        
        self._sip2 = sip2
        
        if autoConnect:
            self.connect()


    def __del__(self):
        """ Reset everything, make sure client is disconnected """
        try:
            self.disconnect()
        finally:
            print ('Sip2Wrapper object unset')       


    def connect(self):
        """ Connect to the server
        @throws Exception if connection fails
        @return boolean returns true if connection succeeds
        """
        self._connected = self._sip2.connect()

        # You might check via debug output or the log file what went wrong
        return self._connected


    def disconnect(self):
        """ Disconnect from the server
        @return Sip2Wrapper returns void
        """        
        self._sip2.disconnect()
        self._connected         = False
        self._inPatronSession   = False
        self._patronInfo        = None
        self._scStatus          = None
        return self


    def login_device(self, loginUserId, loginPassword, autoSelfCheck = True):
        """ Login SC device and do selfcheck as suggested by protocol definition
        @param string loginUserId      The admin user
        @param string loginPassword    The admin password
        @param boolean autoSelfCheck   Whether to call SCStatus after login. 
            Defaults to True. You should always do it.
        @throws Exception if login failed
        @return Sip2Wrapper - returns $this if login successful
        """ 
        # login device
        self.sip_login(loginUserId, loginPassword)
        
        # Perform self check
        if (autoSelfCheck == True):
            # check status
            self.sip_sc_status()
            # Check status
            if (self._scStatus['fixed']['OnlineStatus'] != 'Y'):
                raise RuntimeError('ACS Offline')
            else:                
                return True


    def login_patron(self, patronId, patronPass = ''):
        """ This method is required before any get/fetch methods that have Patron 
        in the name.  Upon successful login, it sets the inPatronSession property to 
        True, otherwise False.
        @param string $patronId Patron login ID
        @param string $patronPass Patron password; may be empty. If you don't 
                                  want to accept logins without password then make
                                  sure that patronPass is never empty!
        @return boolean returns true on successful login, false otherwise
        """
        # Always reset data from failed logins where no session was created
        self._patronStatus      = None
        self._patronInfo        = None
        
        # Always end previous sessions (from successful login)
        if (self._inPatronSession):
            self.sip_patron_session_end()
            
        self._sip2.patron    = patronId
        self._sip2.patronpwd = patronPass

        # Set to true before call to getPatronIsValid since it will throw an exception otherwise
        self._inPatronSession = True
        self._inPatronSession = self.get_patron_isValid()
        return self._inPatronSession


    def get_patron_status(self):
        """
        @throws Exception if patron session hasn't began
        @return array the patron status
        """
        if (self._inPatronSession != True):
            raise RuntimeError('Must start patron session before calling getPatronStatus')

        if (self._patronStatus == None):
            self.sip_patron_status()

        return self._patronStatus


    def get_patron_isValid(self):
        """ Parses patron status to determine if login was successful.
        @note 2017-05-18: If the patron password is empty then CQ (valid password)
        always must be false ('N'). Your must take care that your app/implemen-
        tation does not accept empty passwords if you don't want them.  
        @return boolean returns true if valid, false otherwise
        """
        self.get_patron_status()
        if (self._patronStatus['variable']['BL'][0] != 'Y' or (self._sip2.patronpwd != '' and self._patronStatus['variable']['CQ'][0] != 'Y')):
            return False

        return True

    def get_patron_chargedItems(self):
        """ Get the charged items field
        @return array charged items
        """
        info = self.sip_patron_information('charged')
        if 'AU' in info['variable']:
            return info['variable']['AU']
        
        return {}

    def get_patron_feeItems(self):
        """ Gossip only: return patron fees by type
        @return array fees by type
        """
        if (self._sip2._version != 'Gossip'): return False

        info = self.sip_patron_information('feeItems')
        if 'FA' in info['variable']:
            #https://stackoverflow.com/a/5352630
            return {k: info['variable'][k] for k in info['variable'].keys() & {'CG', 'FA', 'FB', 'FC', 'FD', 'FE', 'FF'}}

        return {}

    def get_patron_fineItems(self):
        """ Return patron fine detail from patron info
        @return array fines
        """
        info = self.sip_patron_information('fine')
        if 'AV' in info['variable']:
            return info['variable']['AV'][0]

        return {}

    def get_patron_finesTotal(self):
        """ Returns the total fines from patron status call
        @return number the float value of the fines
        """ 
        info = self.sip_patron_information()
        if 'BV' in info['variable']:
            return float(info['variable']['BV'][0])
            
        return 0.00

    def get_patron_holdItems(self):
        """ Gets the patron info hold items field
        @return array Hold Items
        """
        info = self.sip_patron_information('hold')
        if 'AS' in info['variable']:
            return info['variable']['AS'][0]

        return {}

    def get_patron_overdueItems(self):
        """ Get the patron info overdue items field
        @return array overdue items
        """
        info = self.sip_patron_information('overdue')
        if 'AT' in info['variable']:
            return info['variable']['AT'][0]

        return {}

    def get_patron_recallItems(self):
        """ Return patron recall items from patron info
        @return array patron items
        """
        info = self.sip_patron_information('recall')
        if 'BU' in info['variable']:
            return info['variable']['BU'][0]

        return {}

    def get_patron_unavailableItems(self):
        """ Return patron unavailable items from patron info
        @return array unavailable items
        """
        info = self.sip_patron_information('unavail')
        if 'CD' in info['variable']:
            return info['variable']['CD'][0]

        return {}

    def get_patron_screenMessages(self):
        """ Returns the Screen Messages field of the patron status, which can include
        for example blocked or barred
        @return array the screen messages
        """
        info = self.get_patron_status();
        if 'AF' in info['variable']:
            return info['variable']['AF'][0]

        return {}

   
    def return_last_request(self):
        """ getter for Sip2 class last_request """ 
        return self._sip2.last_request

    def return_last_response(self):
        """ getter for Sip2 class last_response """ 
        return self._sip2.last_response

    def return_last_response_parsed(self):
        """ getter for Sip2 class last_response_parsed """ 
        return self._sip2.last_response_parsed

    def return_sc_status(self):
        """ Getter for scStatus
        @return Ambigous <NULL, multitype:string multitype:multitype:  >
        """
        return self._scStatus

    def return_sip2(self):
        """ Getter function for self._sip2
        @return sip2
        """
        return self._sip2


    def _command_available(self, sm_id):
        """ Check if a) sc supports command and b) patron is allowed to use command
        @note    
        This can't be checked without calling sip_sc_status() before. So if 
        login_device() is called without selfcheck parameter being True, we'll 
        have to return True on good faith for everything here.
        
        @todo: 
        - improve check by patron status
        - check by item status
        
        @param int sm_id           Position in BX "supported messages" (0-15)
        @return boolean    True or False (always True if self._scStatus is not set)
        """
        if (self._scStatus == None): return True
        
        supported_messages = (
        'Patron Status Request',
        'Checkout',            'Checkin',                  'Block Patron',
        'SC/ACS Status',       'Request SC/ACS Resend',    'Login',
        'Patron Information',  'End Patron Session',       'Fee Paid',
        'Item Information',    'Item Status Update',       'Patron Enable',
        'Hold',                'Renew',                    'Renew All'
        )
        
        patron_status = (
        'charge privileges denied',
        'renewal privileges denied',    'recall privileges denied',
        'hold privileges denied',       'card reported lost',
        'too many items charged',       'too many items overdue',
        'too many renewals',            'too many claims of items returned',
        'too many items lost',          'excessive outstanding fines',
        'excessive outstanding fees',   'recall overdue',
        'too many items billed'                         
        )
        
        if self._scStatus['variable']['BX'][0][sm_id:sm_id + 1] != 'Y':
            self._sip2.log.warning("Wrapper: Server does not support command %s (no message sent)" % supported_messages[sm_id])
            return False
        elif isinstance(self._patronStatus, dict) == True:
            if sm_id == 1 and self._patronStatus['fixed']['PatronStatus'][0:0 + 1] != 'Y':   
                # patron may not charge items
                self._sip2.log.warning("Wrapper: Patron restriction: %s (no message sent)" % patron_status[0])
                return False
            elif sm_id == 13 and self._patronStatus['fixed']['PatronStatus'][3:3 + 1] != 'Y':
                # patron may not hold items   
                self._sip2.log.warning("Wrapper: Patron restriction: %s (no message sent)" % patron_status[3])
                return False
            elif sm_id in (14,15) and self._patronStatus['fixed']['PatronStatus'][1:1 + 1] != 'Y':
                # patron may not renew items
                self._sip2.log.warning("Wrapper: Patron restriction: %s (no message sent)" % patron_status[1])
                return False
        else:
            return True
        
    
    def sip_patron_block(self, blockedCardMsg, cardRetained = 'N'):
        """ Generate Block Patron (code 01) request messages in sip2 format
        Note: Even the protocol definition suggests, that this is pretty useless...
        @param  string blockedCardMsg  message value for the required variable length AL field
        @param  string cardRetained    value for the retained portion of the fixed length field (default N)
        @return string                 SIP2 request message
        """
        if (self._command_available(3) == False): return False
        
        if (self._inPatronSession == False):
            raise RuntimeError('Must start patron session before calling sip_patron_block')

        msg  = self._sip2.sip_block_patron_request(blockedCardMsg, cardRetained)
        info = self._sip2.sip_patron_status_response(self._sip2.get_response(msg))
        return info    
    

    def sip_item_checkin(self, itemIdentifier, returnDate = None, currentLocation = '', itemProperties = '', noBlock = 'N', cancel = ''):
        """ Checking item (code 09/10)
        @param  string itemIdentifier  value for the variable length required AB field
        @param  string returnDate      value for the return date portion of the fixed length field
        @param  string currentLocation value for the variable length required AP field (default '')
        @param  string itemProperties  value for the variable length optional CH field (default '')
        @param  string noBlock         value for the blocking portion of the fixed length field (default N)
        @param  string cancel          value for the variable length optional BI field (default N)
        @return array                  SIP2 checkin response
        """
        if (self._command_available(2) == False): return False
        msg  = self._sip2.sip_checkin_request(itemIdentifier, returnDate, currentLocation, itemProperties, noBlock, cancel)
        info = self._sip2.sip_checkin_response(self._sip2.get_response(msg))
        return info
    

    def sip_item_checkout(self, itemIdentifier, itemProperties ='', feeAcknowledged='N', noBlock='N', nbDueDate = '', scRenewalPolicy = 'N', cancel='N'):
        """ Checkout item (code 11/12). Changed order of parameters slightly
        @param  string itemIdentifier  value for the variable length required AB field
        @param  string nbDueDate       optional override for default due date (default '')
        @param  string scRenewalPolicy value for the renewal portion of the fixed length field (default N)
        @param  string itemProperties  value for the variable length optional CH field (default '')
        @param  string feeAcknowledged value for the variable length optional BO field (default N)
        @param  string noBlock         value for the blocking portion of the fixed length field (default N)
        @param  string cancel          value for the variable length optional BI field (default N)
        @return array                  SIP2 checkout response
        """
        if (self._command_available(1) == False): return False
        msg  = self._sip2.sip_checkout_request(itemIdentifier, nbDueDate, scRenewalPolicy, itemProperties, feeAcknowledged, noBlock, cancel)
        info = self._sip2.sip_checkout_response(self._sip2.get_response(msg))
        return info


    def sip_patron_session_end(self):
        """ Method to send a patron session to the server (code 35/36)
        @throws Exception if patron session is not properly ended
        @return Sip2Wrapper returns $this
        """
        msg  = self._sip2.sip_end_patron_session_request()
        info = self._sip2.sip_end_patron_session_response(self._sip2.get_response(msg))
        if ((info['fixed']['EndSession'] > 'Y') - (info['fixed']['EndSession'] < 'Y')) != 0:
            raise RuntimeError('Error ending patron session')
        self._inPatronSession   = False
        # @todo: Might be a bit redundant because it is reset on each login. 
        #        Cleaner on the other hand, isn't it? 
        self._patronStatus      = None
        self._patronInfo        = None
        return self


    def sip_fee_paid(self, feeType, paymentType, feeAmount, feeIdentifier = '', transactionId = '', currencyType = 'EUR'):
        """ Pay fees (code 37/38)
        @param  int    feeType         value for the fee type portion of the fixed length field
        @param  int    paymentType     value for payment type portion of the fixed length field
        @param  string feeAmount       value for the payment amount variable length required BV field
        @param  string feeIdentifier   value for the fee id variable length optional CG field
        @param  string transactionId   value for the transaction id variable length optional BK field
        @param  string currencyType    value for the currency type portion of the fixed field
        @return array                  SIP2 payment response
        """
        if (self._command_available(9) == False): return False
        msg  = self._sip2.sip_fee_paid_request(feeType, paymentType, feeAmount, feeIdentifier, transactionId, currencyType)
        info = self._sip2.sip_fee_paid_response(self._sip2.get_response(msg))
        return info


    def sip_item_hold(self, holdMode, expirationDate = '', holdType = '', itemIdentifier = '', titleIdentifier = '', feeAcknowledged='N', pickupLocation = ''):
        """ Create, modify, or delete a hold (code 15/16)
        @param  string holdMode          value for the mode portion of the fixed length field
        @param  string expirationDate    value for the optional variable length BW field
        @param  string holdType          value for the optional variable length BY field
        @param  string itemIdentifier    value for the optional variable length AB field
        @param  string titleIdentifier   value for the optional variable length AJ field
        @param  string feeAcknowledged   value for the optional variable length BO field
        @param  string pickupLocation    value for the optional variable length BS field
        @return array                    SIP2 hold response
        """
        if (self._command_available(13) == False): return False
        msg  = self._sip2.sip_hold_request(holdMode, expirationDate, holdType, itemIdentifier, titleIdentifier, feeAcknowledged, pickupLocation)
        info = self._sip2.sip_hold_response(self._sip2.get_response(msg))
        return info


    def sip_item_information(self, itemIdentifier):
        """ Method to get Item Information (17/18)
        @param  string itemIdentifier    value for the variable length required AB field
        @return array                  SIP2 item information response
        """
        if (self._command_available(10) == False): return False
        msg  = self._sip2.sip_item_information_request(itemIdentifier)
        info = self._sip2.sip_item_information_response(self._sip2.get_response(msg))
        return info


    def sip_item_status_update(self,  itemIdentifier, itemProperties = ''):
        """ Item Status Update (code 19/20)
        Generate Item Status (code 19) request messages in sip2 format
        @param  string itemIdentifier  value for the variable length required AB field
        @param  string itemProperties  value for the variable length required CH field
        @return array                  SIP2 checkin response
        """
        if (self._command_available(11) == False): return False
        msg  = self._sip2.sip_item_status_update_request(itemIdentifier, itemProperties)
        info = self._sip2.sip_item_status_update_response(self._sip2.get_response(msg))
        return info


    def sip_login(self, loginUserId, loginPassword):
        """ Authenticate with admin credentials to the backend server (code 93/94)
        @param string loginUserId    The admin user
        @param string loginPassword  The admin password
        @throws Exception if login failed
        @return Sip2Wrapper - returns $this if login successful
        """
        msg  = self._sip2.sip_login_request(loginUserId, loginPassword)
        info = self._sip2.sip_login_response(self._sip2.get_response(msg))
        if (info['fixed']['Ok'] != '1'):
            raise RuntimeError('Login failed')

        return info
    
    
    def sip_patron_enable(self):
        """ Generate Patron Enable (code 25/26) request messages in sip2 format
        Note: Even the protocol definition suggests, that this is pretty useless...
        @return string         SIP2 request message
        @return array          SIP2 enable response
        """
        if (self._command_available(12) == False): return False
        msg  = self._sip2.sip_patron_enable_request()
        info = self._sip2.sip_patron_enable_response(self._sip2.get_response(msg))
        return info


    def sip_patron_information(self, infoType = 'none'):
        """ Worker function to call out to sip2 server and grab patron information (code 64/65)
        @param string infoType     One of 'none', 'hold', 'overdue', 'charged', 'fine', 'recall', or 'unavail'
        @throws Exception if startPatronSession has not been called with success prior to calling this
        @return array              The parsed response from the server
        """
        if (self._command_available(7) == False): return False
        
        if (self._inPatronSession == False):
            raise RuntimeError('Must start patron session before calling fetchPatronInfo')
        
        if (isinstance(self._patronInfo, dict) and infoType in self._patronInfo):
            return self._patronInfo[infoType]

        msg  = self._sip2.sip_patron_information_request(infoType)
        info = self._sip2.sip_patron_information_response(self._sip2.get_response(msg))
        if (self._patronInfo == None):
            self._patronInfo = {}
        self._patronInfo[infoType] = info
        return info


    def sip_patron_status(self):
        """ Method to grab the patron status from the server and store it in _patronStatus 
        (code 63/64). Automatic fallback to Sip1 (code 23/24) 
        @todo 2017-05-18: Any good reason to add an option to force 23/24 and 
        not use the better option?
        @return Sip2Wrapper returns $this
        """
        if (self._command_available(0) == False): return False
        
        # Prefer Sip2 above Sip1 and use the improved variant 63/64 if supported
        info = self.sip_patron_information()
        if info != False:
            self._patronStatus = info
            return info
        # Otherwise use Sip1 variant
        else: 
            msg  = self._sip2.sip_patron_status_request()
            info = self._sip2.sip_patron_status_response(self._sip2.get_response(msg))
            self._patronStatus = info
            return info


    def sip_item_renew(self, itemIdentifier = '', titleIdentifier = '', itemProperties = '', feeAcknowledged= 'N', noBlock = 'N', nbDuDate = '', thirdPartyAllowed = 'N'):
        """ Renew single item (code 29/30). Changed order of parameters slightly
        Generate Renew (code 29) request messages in sip2 format
        @param  string item        value for the variable length optional AB field
        @param  string title       value for the variable length optional AJ field
        @param  string nbDateDue   value for the due date portion of the fixed length field
        @param  string itmProp     value for the variable length optional CH field
        @param  string fee         value for the variable length optional BO field
        @param  string noBlock     value for the blocking portion of the fixed length field
        @param  string thirdParty  value for the party section of the fixed length field
        @return array              SIP2 checkin response
        """
        if (self._command_available(14) == False): return False
        msg  = self._sip2.sip_renew_request(itemIdentifier, titleIdentifier, nbDuDate, itemProperties, feeAcknowledged, noBlock, thirdPartyAllowed)
        info = self._sip2.sip_renew_all_response(self._sip2.get_response(msg))
        return info


    def sip_item_renew_all(self, feeAcknowledged = 'N'):
        """ Renew all loaned items (code 65/66)
        @param  string feeAcknowledged     value for the optional variable length BO field
        @return string                     SIP2 request message
        @return array                      SIP2 checkin response
        """
        if (self._command_available(15) == False): return False
        msg  = self._sip2.sip_renew_all_request(feeAcknowledged)
        info = self._sip2.sip_renew_all_response(self._sip2.get_response(msg))
        return info


    def sip_sc_status(self, statusCode = 0, maxPrintWidth = '080', protocolVersion = 2):
        """ Checks the SC Status to ensure that the SC is online
        @throws Exception if ACS is not online
        @return Sip2Wrapper returns $this if successful
        """
        # execute self test
        msg  = self._sip2.sip_sc_status_request(statusCode, maxPrintWidth, protocolVersion)
        info = self._sip2.sip_sc_status_response(self._sip2.get_response(msg))
        self._scStatus = info

        return info
        