import datetime
import re
import time
import socket, ssl
from _socket import SHUT_RDWR
import sys

import logging
from logging.handlers import TimedRotatingFileHandler
import os.path

class Sip2:
    """ SIP2 Class
    This class provides a method of communicating with an Integrated Library
    System using 3M's SIP2 (Standard Interchange Protocol) standard. It is a 
    low level implementation and method, parameter and variable names are chosen
    in accordance with the protocol definition document 
    ("sip_COMMAND-MESSAGE_request/response"). Some sip fields are configured as
    class properties (@see __init__() - "Public SIP variables (saved for various 
    requests)", because they are used for nearly every request.

    @note:
    - The protocol definition by 3m can be downloaded here:
      http://mws9.3m.com/mws/mediawebserver.dyn?6666660Zjcf6lVs6EVs66S0LeCOrrrrQ-
    - Methods in this class follow the convention 
    
    @note: Connection errors
    The class has two places, where a ConnectionError might be raised. It might
    happen on the initial connection attempt: connect(). The second possibility
    a connection was established but got lost later on. Then the same error will
    be raised in get_response(). Assuming the connection data is correct, then
    a reconnect trial loop probably would be the best option to handle this 
    exception in the implementing class.    

    @Example:
        from sip2 import Gossip (or Sip2)

        #mySip = Sip2()
        mySip = Gossip()
        mySip.hostName = 'mysip.server.net'
        mySip.hostPort = 1294

        # connect to server
        mySip.connect()

        # Now login you SC device
        msg      = mySip.sip_login_request('user', 'pass')
        response = mySip.sip_login_response(mySip.get_response(msg))

        #display response (string or parsed)
        print (mySip.last_response)
        print (mySip.last_response_parsed) #same as variable response
        loginStatus = 'Login ok' if (mySip.last_response_parsed['fixed']['Ok'] == '1') else 'Login failed'
        print (loginStatus)

        # The first thing should/might be a status check. This tells you what
        # requests the ACS accepts and denies
        msg      = mySip.sip_sc_status_request()
        response = mySip.sip_sc_status_response(mySip.get_response(msg))
        onlineStatus = 'Is online' if (mySip.last_response_parsed['fixed']['OnlineStatus'] == 'Y') else 'Not online'
        print (onlineStatus)

        # Identify a patron
        mySip.patron    = '101010101'
        mySip.patronpwd = '010101'

        # Generate charged items request message
        msg      = mySip.sip_patron_information_request('charged')
        response = mySip.sip_patron_information_response(mySip.get_response(msg))

        ...

        # Disconnect
        mySip.disconnect()
        
        # You might check the sip2.log in you path/working dir        

    @package
    @license    MIT License
    @author     Tobias Zeumer <tzeumer@verweisungsform.de>
    @copyright  2016 Tobias Zeumer <tzeumer@verweisungsform.de>
    @link       Python: ???
    @version    $Id: sip2.class.php 28 2010-10-08 21:06:51Z cap60552 $
    @requires:  Python 3.4 (I guess)
    """

    def __init__(self):
        self._version        = 'Sip2'
        # @var string      Used protocol version (or extension) - Sip2 or Gossip

        """Public connection variables"""
        self.hostName       = ''
        # @var string      Instance hostname
        self.hostPort       = 1294
        # @var int         Port number
        self.maxretry       = 0
        # @var integer     Maximum number of resends allowed before we give up. Note: this is pretty much a relict from pre tcp times
        self.socketTimeout  = 3;
        # @var integer     Socket: value until connection times out (no server response)
        self.tlsEnable      = True
        # @var boolean     Use encrypted connection (or try to). Server has to support it.
        self.tlsAcceptSelfsigned = True
        # @var boolean     Allow self signed certificates (adds server cert to ca)
        self.hostEncoding   = 'utf-8'
        # @var string      Encoding returned by ACS

        """Private connection variables"""
        self._socket        = None
        # @var object      A socket connection
        self._retryCount    = 0
        # @var integer     Internal retry counter


        """Public SIP variables (...which you will probably never change)"""
        self.last_request    = ''
        # @var string      Last message sent to ACS
        self.last_response   = ''
        # @var string      Last response from ACS
        self.last_response_parsed = {}
        # @var array       Last parsed response from ACS

        self.fldTerminator  = '|'
        # @var string      Field terminator
        self.msgTerminator  = "\r"
        # @var string      Message terminator

        self.withCrc        = True
        # @var boolean     Toggle crc checking and appending. Note: this is pretty much a relict from pre tcp times
        self.withSeq        = True
        # @var boolean     Toggle the use of sequence numbers

        self.UIDalgorithm   = 0
        # @var integer     Login encryption algorithm type (0 = plain text)
        self.PWDalgorithm   = 0
        # @var integer     Password encryption algorithm type (undocumented)

        """Public SIP variables (saved for various requests) """
        self.language       = '000'
        # @var string      Language code (000 = default, 001 == english)
        self.institutionId  = 'My Test Institute'
        # @var string      Value for the AO field
        self.terminalPassword     = ''
        # @var string      Terminal password (AC)
        self.scLocation     = 'My Test SC Location'
        # @var string l    Location code (AP "location code" / CP "current location")
        self.patron         = ''
        # @var string      Patron identifier (AA)
        self.patronpwd      = ''
        # @var string      Patron password (AD)

        """Private SIP variables"""
        self._noFixed       = ''
        # @var boolean     Internal message build toggle
        self._rqstBuild     = ''
        # @var string      Internal message build buffer
        self._seq           = -1
        # @var integer     Internal sequence number

        """Public logging variables """
        self.log            = None
        # @var object      Logger object. Log of communication actions
        self.logfile_path   = ''
        # @var string      Path where to write to the logfile. Exampele: 'c:\\temp'
        self.loglevel       = 'DEBUG'
        # @var string      Loglevel (DEBUG, INFO, WARNING, ERROR, CRITICAL)


    def __del__(self):
        """ Make sure sockets are always closed """
        try:
            self.disconnect()
        finally:
            print ('Sip2 object unset')
            
    def __exit__(self):
        """ Make sure sockets are always closed """
        try:
            self.disconnect()
        finally:
            print ('Sip2 object unset')


    def _request_new(self, code):
        """ Reset the internal message buffers and start a new message
        @param int code        The message code to start the string
        """
        # resets the rqstBuild variable to the value of code, and clears the flag for fixed messages
        self._noFixed   = False;
        self._rqstBuild = code;


    def _request_addOpt_fixed(self, value, length):
        """ Add a fixed length option field to a request message
        @param string value    The option value
        @param int    len      The length of the option field
        @return bool
        """
        # adds a fixed length option to the rqstBuild IF no variable options have been added.
        if (self._noFixed):
            return False;
        else:
            self._rqstBuild += '{:<{width}}'.format(str(value)[0:length], width=length)
            return True


    def _request_addOpt_var(self, field, value, optional = False):
        """ Add a variable length option field to a request message
        @param string  field       field code for this message
        @param string  value       the option value
        @param bool    optional    optional field designation (default False)
        @return bool
        """
        # adds a variable length option to the message, and also prevents adding additional fixed fields
        if (optional == True and value == ''):
            # skipped
            self.log.info("--- SKIPPING OPTIONAL FIELD --- '%s'" % field)
        else:
            self._noFixed   = True; # no more fixed for this message
            self._rqstBuild += field + str(value)[0:255] + self.fldTerminator;

        return True;


    def _request_seq_set(self):
        """ Manage the internal sequence number and return the next in the list
        @return int            internal sequence number
        """
        # Get a sequence number for the AY field. Valid numbers range 0-9.
        self._seq += 1;
        if (self._seq > 9): self._seq = 0
        return (self._seq);


    def _request_return(self, withSeq = None, withCrc = None):
        """ Return the contents of the internal rqstBuild variable after appending
        sequence and crc fields if requested and appending terminators
        @param  bool withSeq   optional value to enforce addition of sequence numbers
        @param  bool withCrc   optional value to enforce addition of CRC checks
        @return string         formatted sip2 message text complete with termination
        """
        # use object defaults if not passed
        #withSeq = empty($withSeq) ? self.withSeq : $withSeq;
        withSeq = self.withSeq if withSeq is None else withSeq
        withCrc = self.withCrc if withCrc is None else withCrc

        # Finalizes the message and returns it.  Message will remain in rqstBuild until newMessage is called
        if (withSeq):
            self._rqstBuild += 'AY' + str(self._request_seq_set())

        if (withCrc):
            self._rqstBuild += 'AZ'
            self._rqstBuild += self._crc_calc(self._rqstBuild)

        self._rqstBuild += self.msgTerminator

        return self._rqstBuild;


    def _response_parse_varData(self, response, start):
        """ Parse variable length fields from SIP2 responses
        @param  string response    [description]
        @param  int    start       [description]
        @return array              an array containing the parsed variable length data fields
        """
        #import unicodedata
        #def remove_control_characters(s):
        #    return "".join(ch for ch in s if unicodedata.category(ch)[0] != "C")

        parsed = {}
        response = response.strip()

        if (self.withCrc):
            parsed['Raw'] =  response[start:len(response)-6].split(self.fldTerminator)
        else:
            #$result['Raw'] = explode("|", substr($response, $start));
            parsed['Raw'] =  response[start:].split(self.fldTerminator)
        for item in parsed['Raw']:
            field = item[0:2]
            value = item[2:2+len(item)]
            # Could not find any problem. Yet, if a server returns "weird"
            # characters you can uncomment remove_control_characters and use
            # this
            ## clean = remove_control_characters(value)
            ##if (clean != ''):
            ##    result[field] = clean
            if (field not in parsed): parsed[field] = []
            parsed[field].append(value)

        if (self.withCrc):
            parsed['AZ'] = [response[len(response)-4:len(response)]]
        else:
            parsed['AZ'] = ['']
            
        return parsed


    def _crc_calc(self, msg):
        """ Generate and format checksums for SIP2 messages
        The checksum is four ASCII character digits representing the binary sum
        of the characters including the first character of the transmission and
        up to and including the checksum field identifier characters.
        To calculate the checksum add each character as an unsigned binary
        number, take the lower 16 bits of the total and perform a 2's
        complement. The checksum field is the result represented by four hex
        digits.
        To verify the correct checksum on received data, simply add all the hex
        values including the checksum. It should equal zero.
        @param  string string  the string to checksum
        @return string         properly formatted checksum of given string
        """
        #msg = "09N20160419    12200820160419    122008APReading Room 1|AO830|AB830$28170815|AC|AY2AZ" #crc should be EB80
        #msg = "09N20160419    12171320160419    121713APReading Room 1|AO830|AB830$28170815|AC|AY2AZ" #crc should be EB7C
        # Calculate CRC
        ordSum = 0
        for n in range(0, len(msg)):
            ordSum = ordSum + ord(msg[n:n+1])
        crc = format((-ordSum & 0xFFFF), 'X')
        return crc


    def _crc_verify(self, msg):
        """ Verify the integrity of SIP2 messages containing checksums
        @param  string msg     The messsage to check
        @return bool
        """
        # check for enabled crc
        if (self.withCrc != True): return True;

        # test the received message's CRC by generating our own CRC from the message
        test = re.split('(.{4})$', msg.strip());

        # check validity
        if (len(test) > 1 and (self._crc_calc(test[0]) > test[1] and self._crc_calc(test[0]) < test[1]) == 0):
            return True;

        # default return
        return False;


    def _datestamp(self, timestamp = ''):
        """ Generate a SIP2 computable datestamp
        From the spec: YYYYMMDDZZZZHHMMSS.
        All dates and times are expressed according to the ANSI standard X3.30
        for date and X3.43 for time. The ZZZZ field should contain blanks
        (code $20) to represent local time. To represent universal time, a Z
        character(code $5A) should be put in the last (right hand) position of
        the ZZZZ field. To represent other time zones the appropriate character
        should be used; a Q character (code $51) should be put in the last
        (right hand) position of the ZZZZ field to represent Atlantic Standard
        Time. When possible local time is the preferred format.
        @param  timestamp      Unix timestamp to format (default use current time)
        @return string         A SIP2 compatible date/time stamp
        """
        # Current Date/Time if none given
        if (timestamp == ''): timestamp = int(time.time())

        # Generate a proper date time from the date provided
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y%m%d    %H%M%S')


    def _init_logger(self):
        """ Handle the printing of debug messages
        @param  string message     The message text
        """
        #logentry = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()) + ' ' + message
        message = 'Started logging with loglevel ' + self.loglevel
        
        # Configure logger
        filename = 'sip2.log'
        if os.path.exists(self.logfile_path):
            logfile  = os.path.join(self.logfile_path, filename)
        else:
            message += ' Custom log file path not set or does not exist. Using default: ' + os.getcwd()
            logfile  = os.path.join(os.getcwd(), filename)

        # Set configuration
        self.log = logging.getLogger(self._version)
 
        # set level       
        # https://stackoverflow.com/a/15368084
        level = logging.getLevelName(self.loglevel)
        self.log.setLevel(level)
        
        # Formatting
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        #, datefmt='%Y-%m-%d %H:%M:%'

        # Rotating 
        handler = TimedRotatingFileHandler(logfile, when="midnight", interval=1, backupCount=31)
        handler.setFormatter(formatter)
        self.log.addHandler(handler)

        # Log to file (for now always debug
        self.log.warning(message)              


    def connect(self):
        """ Open a socket connection to a backend SIP2 system, enable TLS via property
        @see https://docs.python.org/3/library/exceptions.html#os-exceptionss
        @todo Improvements
            - Save and reuse self signed certificates and/or give means to provide ca file
            - PHP 5.6+ has context option "allow_self_signed" - check if Python adds it too later on
        @return bool               The socket connection status
        """
        # Initialize logger on first connect
        if self.log == None:
            self._init_logger()
        
        # Check that basic parameters are right
        if self.hostName == '':
            raise ValueError("Cannot autoconnect. No host set (parameter: hostName): '%s'" % self.hostName)
        if isinstance(self.hostPort, int) == False or int(self.hostPort < 1):
            raise ValueError("Cannot autoconnect. No port set (parameter: hostPort) or not a valid integer: '%s'" % self.hostPort)

        self.log.info("--- BEGIN SIP communication ---")
        mode = False

        """ Check if host is reachable at all """
        plain = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        plain.settimeout(self.socketTimeout)
        try:
            plain.connect((self.hostName, self.hostPort))
            self.log.info("--- SOCKET EXISTS ---")
            mode = 'plain'
        except socket.timeout as e:
            self.log.critical("--- CONNECTION ERROR: Host not reachable. ---")
            raise ConnectionError('Connection error: TCP') from e
        except socket.error as e:
            """Socket exceptions suck, because they may vary by OS?
            Anyway, all errors 'might' be just caused by a temporarily downtime 
            of the server. The best action for any implementation on a 
            ConnectionError 'should' be a reconnect attempt.
            """
            #print (str(e.errno) + ' ' + e.strerror)
            if (e.errno == 10061 or e.strerror.find('refused') > 0):
                self.log.critical("--- CONNECTION ERROR: Possibly wrong port. %s ---" % e)
                # Ask user to correct name/port
            elif (e.errno == 11001 or e.strerror.find('getaddrinfo') > 0):
                self.log.critical("--- CONNECTION ERROR: Possibly wrong host name. %s ---" % e)
                # Ask user to correct name/port
            elif (e.errno == 10060 or e.strerror.find('period of time') > 0):
                self.log.critical("--- CONNECTION ERROR: Host not reachable. %s ---" % e)
            else:
                self.log.critical("--- CONNECTION ERROR: I got no clue. %s ---" % e)
            raise ConnectionError('Connection error: TCP') from e
            #sys.exit(1)

        # return socket if TLS is explicitly disabled
        if (self.tlsEnable == False):
            self.log.warning("--- CONNECTION ESTABLISHED: Unencrypted ---")
            self._socket = plain
            return True

        # Otherwise go for TLS
        """ Configure ssl context
        ssl.PROTOCOL_SSLv23: Selects the highest protocol version that both the client and server support. Despite the name, this option can select “TLS” protocols as well as “SSL”.
        ssl.PROTOCOL_TLSv1: Selects TLS version 1.0 as the channel encryption protocol.
        ssl.PROTOCOL_TLSv1_1: Selects TLS version 1.1 as the channel encryption protocol. Available only with openssl version 1.0.1+.
        ssl.PROTOCOL_TLSv1_2: New in version 3.4. Selects TLS version 1.2 as the channel encryption protocol. This is the most modern version, and probably the best choice for maximum protection, if both sides can speak it. Available only with openssl version 1.0.1+.
        """
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        #context.verify_mode = ssl.CERT_NONE
        context.verify_mode     = ssl.CERT_REQUIRED
        context.check_hostname  = True
        context.options        |= ssl.OP_NO_COMPRESSION
        context.set_ciphers('HIGH:!aNULL:!SSLv2:!RC4:!3DES:!MD5')
        # new, by default it loads certs trusted for Purpose.SERVER_AUTH
        # uses OS stroe but may change later - Python documentation...
        context.load_default_certs()

        """ Test if TLS is available, wrap ssl around plain """
        try:
            # if this works without exception, then we have a host with tls support, valid cert and known CA
            sslSock = context.wrap_socket(plain, server_hostname = self.hostName)
            mode = 'tls'
        except ssl.SSLError as e:
            #print (str(e.errno) + ' --- ' + e.strerror)
            if  (e.strerror.find('unknown protocol') > 0):
                self.log.warning("--- CONNECTION INFO: SSL is not supported by host (using plain connection). %s ---" % e)
            elif  (e.strerror.find('wrong version') > 0):
                # seems always to be the case if no ssl _and_ higher than PROTOCOL_SSLv23 selected
                self.log.warning("--- CONNECTION INFO: SSL seems not to be supported (using plain connection). Slight chance that is only a misconfiguration in Sip2 module.  %s ---" % e)
            elif  (e.strerror.find('verify failed') > 0):
                # seems always to be the case if no ssl _and_ higher than PROTOCOL_SSLv23 selected
                self.log.warning("--- CONNECTION INFO: SSL - Server probably uses self signed certificate (or invalid!).") # %s ---\n" % e)
                mode = 'tls_untrusted'
            else:
                self.log.critical("--- CONNECTION INFO: Some unkown error testing for SSL. %s ---" % e)

        """ If we want to allow self signed certificates, get the server cert and use it as trusted ca """
        if (mode == 'tls_untrusted' and self.tlsAcceptSelfsigned == True):
            pem = ssl.get_server_certificate((self.hostName, self.hostPort))
            if not pem:
                self.log.warning("--- CONNECTION ERROR: SSL server certificate unavailable though assumed it must exist. %s ---" % e)
            else:
                # Seems like we have to start over again with new context
                plain = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                plain.connect((self.hostName, self.hostPort))

                # Add the server cert as ca - (self signed = ca + cert in one)
                # Other options are set above already (and stick)
                #context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
                #context.verify_mode     = ssl.CERT_REQUIRED
                #context.check_hostname  = True
                #context.options        |= ssl.OP_NO_COMPRESSION
                #context.set_ciphers('HIGH:!aNULL:!SSLv2:!RC4:!3DES:!MD5')
                #context.load_default_certs()
                context.load_verify_locations(cafile=None, capath=None, cadata=pem)


                sslSock = context.wrap_socket(plain, server_hostname = self.hostName)
                # we really should check if "Issuer" == "Subject" in pem - but how to decode pem?
                # Only way to get plaintext of certificate without 3rd party modules like M2Crypto or OpenSSL
                cert_plain = sslSock.getpeercert()
                if (cert_plain['issuer'] == cert_plain['subject']):
                    self.log.warning("--- CONNECTION INFO: SSL - Certificate issuer and subject are identical. It is self signed.")
                # even more checking (we already know subject = issuer, so it doesn't matter wich we check
                # it's a manual version of context.check_hostname  = True
                for field in cert_plain['subject']:
                    if field[0][0] == 'commonName':
                        certhost = field[0][1]
                        if certhost != self.hostName:
                            raise ssl.SSLError("Host name '%s' doesn't match certificate host '%s'" % (self.hostName, certhost))
                        else:
                            self.log.warning("--- CONNECTION INFO: SSL - Certificate issuer[commonName] and subject[commonName] are identical. It is self signed.")
                #print (pem)
        elif (mode == 'tls_untrusted' and self.tlsAcceptSelfsigned == False):
                self.log.critical("--- CONNECTION ERROR: SSL server seems to use self signed certificate that cannot be accepted (set tlsAcceptSelfsigned = True to change) ---")
                mode = False

        """ Finish connection """
        if (mode == 'plain'):
            self.log.warning("--- CONNECTION ESTABLISHED: Unencrypted ---")
            # the plain connection may have been closed when attempting TLS. Reconnect if this happens.
            if plain.fileno() == -1:
                plain = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                plain.connect((self.hostName, self.hostPort))
                plain.settimeout(self.socketTimeout)

            self._socket = plain
            return True
        elif (mode == 'tls'):
            self.log.info("--- CONNECTION ESTABLISHED: Encrypted (Valid host, valid known CA, valid certificate) ---")
            self._socket = sslSock
            return True
        elif (mode == 'tls_untrusted'):
            self.log.warning("--- CONNECTION ESTABLISHED: Encrypted (Self Signed - Valid host = valid CA => valid certificate) ---")
            self._socket = sslSock
            return True
        else:
            self.log.critical("--- CONNECTION FAILED ---")
            raise ConnectionError('Connection error: TLS')
            return False


    def disconnect(self):
        """ Disconnect from the backend SIP2 system (close socket)
        """
        #if (gettype($this->socket) !=  'resource') {
        #    $context = ($this->socket_protocol == 'tcp') ? stream_context_create() : stream_context_create( ['ssl' => $this->socket_tls_options] );
        if (self._socket != None):
            self._socket.shutdown(SHUT_RDWR)
            self._socket.close()
            self.log.info("--- CONNECTION CLOSED ---")
            self._socket = None

        return True


    def get_response (self, request):
        """ Send a message to the backend SIP2 system and read response
        @todo Should this class offer any options to handle disconnects? I think
              it's better to keep this class "dumb" and let it handle the actual
              user if either a ConnectionResetError or a ConnectionError happens.
        @param  string request     The request text to send to the backend system
        @return string|false       Raw string response returned from the backend system (response)
        """
        # Set user defined socket timeout
        try:
            self._socket.settimeout(self.socketTimeout)
        # If _connect is not initialized then no (sucessful) connection was ever initiated
        except AttributeError as e:
            raise ConnectionError('Connection error: You must make a sucessful connection attempt before sending commands!') from e

        self.log.info("--- SENDING REQUEST --- \n%s" % request)
        try:
            #Send complete string at once
            self._socket.sendall(bytes(request, self.hostEncoding))
            self.log.info("--- REQUEST SENT, WAITING FOR RESPONSE ---")
        except socket.error as e:
            self.log.warning("--- SENDING REQUEST FAILED --- \n%s" % e)
            raise ConnectionResetError('Connection reset: Most likely connection was lost. %s' % e) from e
            # HERE > NEW TRY > CONNECT AGAIN!?! (
            # if self_socket != None:
            #     connect mit https://julien.danjou.info/blog/2017/python-tenacity
            # else:
            #     raise runtime-or-so("Please connect before sending requests")
            #sys.exit()

        # \x0A is the escaped hexadecimal Line Feed. The equivalent of \n.
        # \x0D is the escaped hexadecimal Carriage Return. The equivalent of \r.
        #$result = stream_get_line((stream_socket_client($this->socket_protocol.'://'.$this->hostname.':'.$this->port, $this->socket_error_id, $this->socket_error_msg, $this->socketTimeout, STREAM_CLIENT_CONNECT|STREAM_CLIENT_PERSISTENT, $context)), 100000, "\x0D");
        response = self._socket.recv(4096).decode(encoding = self.hostEncoding)

        self.log.info("--- RESPONSE RECEIVED  --- \n%s" % response)

        # test request for CRC validity
        if (self._crc_verify(response) == True):
            # reset the retry counter on successful send
            self._retryCount = 0
            self.log.info("--- Message from ACS passed CRC check ---")
        else:
            # CRC check failed, request a resend
            self._retryCount += 1;
            if (self._retryCount < self.maxretry):
                # try again
                self.log.warning("--- Message failed CRC check, retrying --- (%s)" % self._retryCount)
                self.get_response(request)
            else:
                # give up
                self.log.critical("--- Failed to get valid CRC --- after (%s) retries." % self._retryCount)
                # This might be a bit tricky should a CRC really ever fail.
                # Most likely it's best to indicate that a reconnect probably is
                # the best choice bei raising a ConnectionError.
                raise ConnectionError('Connection error: Failed to get valid CRC for response') from e
                #return False

        # Keep last message and response as property
        self.last_request  = request
        self.last_response = response

        return response


    def sip_block_patron_request(self, blockedCardMsg, cardRetained = 'N'):
        """ Generate Block Patron (code 01) request messages in sip2 format
        @param  string blockedCardMsg  AJ field: message value for the required variable length AL field
        @param  string cardRetained    value for the retained portion of the fixed length field (default N)
        @return string                 SIP2 request message

        @note SIP2 Protocol definition document:        
        This message requests that the patron card be blocked by the ACS. This
        is, for example, sent when the patron is detected tampering with the SC
        or when a patron forgets to take their card. The ACS should invalidate
        the patron’s card and respond with a Patron Status Response message. The
        ACS could also  notify the library staff that the card has been blocked.
            01<card retained><transaction date><institution id><blocked card msg><patronidentifier><terminal password>
        """
        # Blocks a patron, and responds with a patron status response  (01) - untested
        self._request_new('01')
        self._request_addOpt_fixed(cardRetained, 1); #  Y if card has been retained
        self._request_addOpt_fixed(self._datestamp(), 18)
        self._request_addOpt_var('AO', self.institutionId);
        self._request_addOpt_var('AL', blockedCardMsg);
        self._request_addOpt_var('AA', self.patron);
        self._request_addOpt_var('AC', self.terminalPassword);

        return self._request_return()


    def sip_checkin_request(self, itemIdentifier, returnDate = None, currentLocation = '', itemProperties = '', noBlock = 'N', cancel = ''):
        """ Generate Checkin (code 09) request messages in sip2 format
        @param  string itemIdentifier  value for the variable length required AB field
        @param  string returnDate      value for the return date portion of the fixed length field
        @param  string currentLocation value for the variable length required AP field (default '')
        @param  string itemProperties  value for the variable length optional CH field (default '')
        @param  string noBlock         value for the blocking portion of the fixed length field (default N)
        @param  string cancel          value for the variable length optional BI field (default N)
        @return string                 SIP2 request message

        @note SIP2 Protocol definition document:        
        This message is used by the SC to request to check in an item, and also 
        to cancel a Checkout request that did not successfully complete. The ACS 
        must respond to this command with a Checkin Response message.
            09<no block><transaction date><return date><current location><institution id><item identifier><terminal password><item properties><cancel>
        """
        # If no location is specified, assume the default location of the SC, behavior suggested by spec
        if (currentLocation == ''):
            currentLocation = self.scLocation

        # Assume time of method call as return date if none is given
        returnDate = self._datestamp() if returnDate is None else self._datestamp(returnDate)

        self._request_new('09')
        self._request_addOpt_fixed(noBlock, 1)
        self._request_addOpt_fixed(self._datestamp(), 18)
        self._request_addOpt_fixed(returnDate, 18)
        self._request_addOpt_var('AP', currentLocation)
        self._request_addOpt_var('AO', self.institutionId)
        self._request_addOpt_var('AB', itemIdentifier)
        self._request_addOpt_var('AC', self.terminalPassword)
        self._request_addOpt_var('CH', itemProperties, True)
        self._request_addOpt_var('BI', cancel, True); # Y or N

        return self._request_return()


    def sip_checkin_response(self, response):
        """ Parse the response returned from Checkin request messages (code 10)
        @param  string response    response string from the SIP2 backend
        @return array              parsed SIP2 response message
        
        @note SIP2 Protocol definition document:        
        This message must be sent by the ACS in response to a SC Checkin message.
            10<ok><resensitize><magnetic media><alert><transaction date><institution id><itemidentifier><permanent location><title identifier><sort bin><patron identifier><media type><item properties><screen message><print line>
        """
        result = {'fixed': {
                            'Ok':              response[2:3],
                            'Resensitize':     response[3:4],
                            'MagneticMedia':   response[4:5],
                            'Alert':           response[5:6],
                            'TransactionDate': response[6:6+18]
                            },
                  'variable': self._response_parse_varData(response, 24)
                }

        self.last_response_parsed = result;
        return result;


    def sip_checkout_request(self, itemIdentifier, nbDueDate = '', scRenewalPolicy = 'N', itemProperties ='', feeAcknowledged='N', noBlock='N', cancel='N'):
        """
        Generate Checkout (code 11) request messages in sip2 format
        @param  string itemIdentifier  value for the variable length required AB field
        @param  string nbDueDate       optional override for default due date (default '')
        @param  string scRenewalPolicy value for the renewal portion of the fixed length field (default N)
        @param  string itemProperties  value for the variable length optional CH field (default '')
        @param  string feeAcknowledged value for the variable length optional BO field (default N)
        @param  string noBlock         value for the blocking portion of the fixed length field (default N)
        @param  string cancel          value for the variable length optional BI field (default N)
        @return string                 SIP2 request message

        @note SIP2 Protocol definition document:        
        This message is used by the SC to request to check out an item, and also 
        to cancel a Checkin request that did not successfully complete. The ACS 
        must respond to this command with a Checkout Response message.
            11<SC renewal policy><no block><transaction date><nb due date><institution id><patron identifier><item identifier><terminal password><patron password><item properties><fee acknowledged><cancel>
        """
        self._request_new('11')
        self._request_addOpt_fixed(scRenewalPolicy, 1)
        self._request_addOpt_fixed(noBlock, 1)
        self._request_addOpt_fixed(self._datestamp(), 18)
        if (nbDueDate != ''):
            # override default date due
            self._request_addOpt_fixed(self._datestamp(nbDueDate), 18)
        else:
            # send a blank date due to allow ACS to use default date due computed for item
            self._request_addOpt_fixed('', 18)

        self._request_addOpt_var('AO', self.institutionId)
        self._request_addOpt_var('AA', self.patron)
        self._request_addOpt_var('AB', itemIdentifier)
        self._request_addOpt_var('AC', self.terminalPassword)
        self._request_addOpt_var('CH', itemProperties, True)
        self._request_addOpt_var('AD', self.patronpwd, True)
        self._request_addOpt_var('BO', feeAcknowledged, True) # Y or N
        self._request_addOpt_var('BI', cancel, True) # Y or N

        return self._request_return()


    def sip_checkout_response(self, response):
        """ Parse the response returned from Checkout request messages (code 12)
        @param  string response    response string from the SIP2 backend
        @return array              parsed SIP2 response message
        
        @note SIP2 Protocol definition document:        
        This message must be sent by the ACS in response to a Checkout message from the SC.
            12<ok><renewal ok><magnetic media><desensitize><transaction date><institution id><patron identifier><item identifier><title identifier><due date><fee type><security inhibit><currency type><fee amount><media type><item properties><transaction id><screen message><print line>
        """
        result = {'fixed': {
                            'Ok':              response[2:3],
                            'RenewalOk':       response[3:4],
                            'MagneticMedia':   response[4:5],
                            'Desensitize':     response[5:6],
                            'TransactionDate': response[6:6+18]
                            },
                  'variable': self._response_parse_varData(response, 24)
                }

        self.last_response_parsed = result
        return result;


    def sip_end_patron_session_request(self):
        """ Generate End Patron Session (code 35) request messages in sip2 format
        @return string         SIP2 request message

        @note SIP2 Protocol definition document:        
        This message will be sent when a patron has completed all of their 
        transactions. The ACS may, upon receipt of this command, close any open 
        files or deallocate data structures pertaining to that patron. The ACS 
        should respond with an End Session Response message.
            35<transaction date><institution id><patron identifier><terminal password><patron password>
        """
        # End Patron Session, should be sent before switching to a new patron. (35)
        self._request_new('35')
        self._request_addOpt_fixed(self._datestamp(), 18)
        self._request_addOpt_var('AO', self.institutionId)
        self._request_addOpt_var('AA', self.patron)
        self._request_addOpt_var('AC', self.terminalPassword, True)
        self._request_addOpt_var('AD', self.patronpwd, True)

        return self._request_return()


    def sip_end_patron_session_response(self, response):
        """ Parse the response returned from End Session request messages (code 36)
        @example    36Y20080228    145537AOWOHLERS|AAX00000000|AY9AZF474
        @param  string response    response string from the SIP2 backend
        @return array              parsed SIP2 response message

        @note SIP2 Protocol definition document:        
        The ACS must send this message in response to the End Patron Session 
        message.
            36<end session><transaction date><institution id><patron identifier><screen message><print line>
        """
        result = {'fixed': {
                            'EndSession':      response[2:3],
                            'TransactionDate': response[3:3+18]
                            },
                  'variable': self._response_parse_varData(response, 21)
                }

        self.last_response_parsed = result
        return result


    def sip_fee_paid_request (self, feeType, paymentType, feeAmount, feeIdentifier = '', transactionId = '', currencyType = 'EUR'):
        """ Generate Fee Paid (code 37) request messages in sip2 format
        @param  int    feeType         value for the fee type portion of the fixed length field
        @param  int    paymentType     value for payment type portion of the fixed length field
        @param  string feeAmount       value for the payment amount variable length required BV field
        @param  string feeIdentifier   value for the fee id variable length optional CG field
        @param  string transactionId   value for the transaction id variable length optional BK field
        @param  string currencyType    value for the currency type portion of the fixed field
        @return string|false           SIP2 request message or false on error

        Fee Types:
        01 other/unknown      02 administrative            03 damage
        04 overdue            05 processing                06 rental
        07 replacement        08 computer access charge    09 hold fee

        Value Payment Type
        00   cash            01   VISA                     02   credit card

        @note SIP2 Protocol definition document:        
        This message can be used to notify the ACS that a fee has been collected 
        from the patron. The ACS should record this information in their 
        database and respond with a Fee Paid Response message.
            37<transaction date><fee type><payment type><currency type><fee amount><institution id><patron identifier><terminal password><patron password><fee identifier><transaction id>
        """
        if (feeType > 99 or feeType < 1):
            # not a valid fee type - exit
            error = "(sip_fee_paid_request) Invalid fee type: %s" % feeType
            self.log.error(error)
            raise ValueError(error)

        if (paymentType > 99 or paymentType < 0):
            # not a valid payment type - exit
            error = "(sip_fee_paid_request) Invalid payment type: %s" % feeType
            self.log.error(error)
            raise ValueError(error)

        self._request_new('37');
        self._request_addOpt_fixed(self._datestamp(), 18);
        self._request_addOpt_fixed(str(feeType).zfill(2) , 2);
        self._request_addOpt_fixed(str(paymentType).zfill(2), 2);
        self._request_addOpt_fixed(currencyType, 3);
        self._request_addOpt_var('BV', feeAmount); # due to currancy format localization, it is up to the programmer to properly format their payment amount
        self._request_addOpt_var('AO', self.institutionId);
        self._request_addOpt_var('AA', self.patron);
        self._request_addOpt_var('AC', self.terminalPassword, True);
        self._request_addOpt_var('AD', self.patronpwd, True);
        self._request_addOpt_var('CG', feeIdentifier, True);
        self._request_addOpt_var('BK', transactionId, True);

        return self._request_return()


    def sip_fee_paid_response(self, response):
        """ Parse the response returned from Fee Paid request messages (code 38)
        @param  string response    response string from the SIP2 backend
        @return array              parsed SIP2 response message
        
        @note SIP2 Protocol definition document:        
        The ACS must send this message in response to the Fee Paid message.
            38<payment accepted><transaction date><institution id><patron identifier><transaction id><screen message><print line>
        """
        result = {'fixed': {
                            'PaymentAccepted': response[2:3],
                            'TransactionDate': response[3:3+18]
                            },
                  'variable': self._response_parse_varData(response, 21)
                }

        self.last_response_parsed = result
        return result


    def sip_hold_request(self, holdMode, expirationDate = '', holdType = '', itemIdentifier = '', titleIdentifier = '', feeAcknowledged='N', pickupLocation = ''):
        """ Generate Hold (code 15) request messages in sip2 format
        @param  string holdMode          value for the mode portion of the fixed length field
        @param  string expirationDate    value for the optional variable length BW field
        @param  string holdType          value for the optional variable length BY field
        @param  string itemIdentifier    value for the optional variable length AB field
        @param  string titleIdentifier   value for the optional variable length AJ field
        @param  string feeAcknowledged   value for the optional variable length BO field
        @param  string pickupLocation    value for the optional variable length BS field
        @return string|false             SIP2 request message or false on error

        mode validity check:
        - remove hold        + place hold        * modify hold
        
        @note SIP2 Protocol definition document:        
        This message is used to create, modify, or delete a hold. The ACS should 
        respond with a Hold Response message. Either or both of the “item 
        identifier” and “title identifier” fields must be present for the 
        message to be useful.
            15<hold mode><transaction date><expiration date><pickup location><hold type><institution id><patron identifier><patron password><item identifier><title identifier><terminal password><fee acknowledged>        
        """
        if (holdMode == '' or (holdMode in '-+*') == False):
            # not a valid mode - exit
            error = self._version + ": Invalid hold mode: %s" % holdMode
            self.log.error(error)
            raise ValueError(error)

        """ Valid hold types range from 1 - 9
        1   other        2   any copy of title        3   specific copy
        4   any copy at a single branch or location
        """
        if (holdType != '' and (holdType < 1 or holdType > 9)):
            error = self._version + ": Invalid hold type code: %s" % holdType
            self.log.error(error)
            raise ValueError(error)

        self._request_new('15')
        self._request_addOpt_fixed(holdMode, 1)
        self._request_addOpt_fixed(self._datestamp(), 18)
        if (expirationDate != ''):
            # hold expiration date,  due to the use of the datestamp function,
            # we have to check here for empty value. when datestamp is passed an
            # empty value it will generate a current datestamp
            self._request_addOpt_var('BW', self._datestamp(expirationDate), True)  # spec says this is fixed field, but it behaves like a var field and is optional...
        self._request_addOpt_var('BS', pickupLocation, True)
        self._request_addOpt_var('BY', holdType, True)
        self._request_addOpt_var('AO', self.institutionId)
        self._request_addOpt_var('AA', self.patron)
        self._request_addOpt_var('AD', self.patronpwd, True)
        self._request_addOpt_var('AB', itemIdentifier, True)
        self._request_addOpt_var('AJ', titleIdentifier, True)
        self._request_addOpt_var('AC', self.terminalPassword, True)
        self._request_addOpt_var('BO', feeAcknowledged, True) # Y when user has agreed to a fee notice

        return self._request_return()


    def sip_hold_response(self, response):
        """ Parse the response returned from Hold request messages (code 16)
        @param  string response      response string from the SIP2 backend
        @return array                parsed SIP2 response message
        
        @note SIP2 Protocol definition document:        
        The ACS should send this message in response to the Hold message from 
        the SC.
            16<ok><available><transaction date><expiration date><queue position><pickup location><institution id><patron identifier><item identifier><title identifier><screen message><print line>
        """
        result = {'fixed': {
                            'Ok':               response[2:3],
                            'Available':        response[3:4],
                            'TransactionDate':  response[4:4+18],
                            'ExpirationDate':   response[22:22+18]
                            },
                  'variable': self._response_parse_varData(response, 40)
                }

        self.last_response_parsed = result
        return result


    def sip_item_information_request(self, itemIdentifier):
        """ Generate Item Information (code 17) request messages in sip2 format
        @param  string itemIdentifier    value for the variable length required AB field
        @return string                   SIP2 request message
        
        @note SIP2 Protocol definition document:        
        This message may be used to request item information. The ACS should 
        respond with the Item Information Response message.
            17<transaction date><institution id><item identifier><terminal password>
        """
        self._request_new('17');
        self._request_addOpt_fixed(self._datestamp(), 18);
        self._request_addOpt_var('AO', self.institutionId);
        self._request_addOpt_var('AB', itemIdentifier);
        self._request_addOpt_var('AC', self.terminalPassword, True);
        return self._request_return();


    def sip_item_information_response(self, response):
        """ Parse the response returned from Item Info request messages (code 18)
        @param  string response    response string from the SIP2 backend
        @return array              parsed SIP2 response message
        
        CirculationStatuses
        1 other       2 on order        3 available
        4 charged     5 charged; not to be recalled until earliest recall date
        6 in process  7 recalled        8 waiting on hold shelf
        9 waiting to be re-shelved      10 in transit between library locations
        11 claimed returned             12 lost
        13 missing

        @note SIP2 Protocol definition document:        
        The ACS must send this message in response to the Item Information 
        message.
            18<circulation status><hold queue length><security marker><fee type><transaction date><due date><recall date><hold pickup date><item identifier><title identifier><owner><currency type><fee amount><media type><permanent location><current location><item properties><screen message><print line>         
        """
        result = {'fixed': {
                            'CirculationStatus':response[2:4],
                            'SecurityMarker':   response[4:6],
                            'FeeType':          response[6:8],
                            'TransactionDate':  response[8:8+18]
                            },
                  'variable': self._response_parse_varData(response, 26)
                }

        self.last_response_parsed = result
        return result


    def sip_item_status_update_request (self, itemIdentifier, itemProperties = ''):
        """ Generate Item Status (code 19) request messages in sip2 format
        @param  string itemIdentifier  value for the variable length required AB field
        @param  string itemProperties  value for the variable length required CH field
        @return string                 SIP2 request message
        
        @note SIP2 Protocol definition document:        
        This message can be used to send item information to the ACS, without 
        having to do a Checkout or Checkin operation. The item properties could 
        be stored on the ACS’s database. The ACS should respond with an Item 
        Status Update Response message.
            19<transaction date><institution id><item identifier><terminal password><item properties>
        """
        self._request_new('19')
        self._request_addOpt_fixed(self._datestamp(), 18)
        self._request_addOpt_var('AO', self.institutionId)
        self._request_addOpt_var('AB', itemIdentifier)
        self._request_addOpt_var('AC', self.terminalPassword, True)
        self._request_addOpt_var('CH', itemProperties)
        return self._request_return()


    def sip_item_status_update_response(self, response):
        """ Parse the response returned from Item Status Update request messages (code 20)
        @param  string response    response string from the SIP2 backend
        @return array              parsed SIP2 response message
        
        @note SIP2 Protocol definition document:        
        The ACS must send this message in response to the Item Status Update 
        message.
        20<item properties ok><transaction date><item identifier><title identifier><item properties><screen message><print line>
        """
        result = {'fixed': {
                            'ItemPropertiesOk': response[2:3],
                            'TransactionDate':  response[3:3+18]
                            },
                  'variable': self._response_parse_varData(response, 21)
                }

        self.last_response_parsed = result
        return result


    def sip_login_request(self, loginUserId, loginPassword):
        """ Generate login (code 93) request messages in sip2 format
        @param  string loginUserId     login value for the CN field
        @param  string loginPassword   password value for the CO field
        @return string                 SIP2 request message
        
        @note SIP2 Protocol definition document:        
        This message can be used to login to an ACS server program. The ACS 
        should respond with the Login Response message. Whether to use this 
        message or to use some other mechanism to login to the ACS is 
        configurable on the SC. When this message is used, it will be the first 
        message sent to the ACS.
            93<UID algorithm><PWD algorithm><login user id><login password><location code>
        """
        self._request_new('93')
        self._request_addOpt_fixed(self.UIDalgorithm, 1)
        self._request_addOpt_fixed(self.PWDalgorithm, 1)
        self._request_addOpt_var('CN', loginUserId)
        self._request_addOpt_var('CO', loginPassword)
        self._request_addOpt_var('CP', self.scLocation, True)
        return self._request_return()


    def sip_login_response(self, response):
        """ Parse the response returned from login request messages (code 94)
        @param  string response    response string from the SIP2 backend
        @return array              parsed SIP2 response message
        
        @note SIP2 Protocol definition document:        
        The ACS should send this message in response to the Login message. When 
        this message is used, it will be the first message sent to the SC.
            94<ok>
        """
        result = {'fixed': {
                            'Ok':              response[2:3]
                            },
                  'variable': self._response_parse_varData(response, 3)
                }

        self.last_response_parsed = result
        return result


    def sip_patron_enable_request(self):
        """ Generate Patron Enable (code 25) request messages in sip2 format
        This message can be used by the SC to re-enable canceled patrons. It
        should only be used for system testing and validation.
        @return string         SIP2 request message
        
        @note SIP2 Protocol definition document:        
        This message can be used by the SC to re-enable canceled patrons. It 
        should only be used for system testing and validation. The ACS should 
        respond with a Patron Enable Response message.
            25<transaction date><institution id><patron identifier><terminal password><patron password>
        """
        self._request_new('25');
        self._request_addOpt_fixed(self._datestamp(), 18);
        self._request_addOpt_var('AO', self.institutionId);
        self._request_addOpt_var('AA', self.patron);
        self._request_addOpt_var('AC', self.terminalPassword, True);
        self._request_addOpt_var('AD', self.patronpwd, True);
        return self._request_return();


    def sip_patron_enable_response(self, response):
        """ Parse the response returned from Patron Enable request messages (code 26)
        @param  string response    response string from the SIP2 backend
        @return array              parsed SIP2 response message
        
        @note SIP2 Protocol definition document:        
        The ACS should send this message in response to the Patron Enable 
        message from the SC. 
            26<patron status><language><transaction date><institution id><patron identifier><personal name><valid patron><valid patron password><screen message><print line>
        """
        result = {'fixed': {
                            'PatronStatus':     response[2:16],
                            'Language':         response[16:19],
                            'TransactionDate':  response[19:19+18]
                            },
                  'variable': self._response_parse_varData(response, 37)
                }

        self.last_response_parsed = result
        return result


    def sip_patron_information_request(self, infoType, startItem = '1', endItem = '5'):
        """ Generate Patron Information (code 63) request messages in sip2 format
        According to the specification:
        Only one category of items should be  requested at a time, i.e. it would
        take 6 of these messages, each with a different position set to Y, to
        get all the detailed information about a patron's items.
        @param  string infoType    type of information request (none, hold, overdue, charged, fine, recall, unavail)
        @param  string startItem   value for BP field (default from 1 item)
        @param  string endItem     value for BQ field (default 5 items total)
        @return string             SIP2 request message
        
        @note SIP2 Protocol definition document:        
        This message is a superset of the Patron Status Request message. It 
        should be used to request patron information. The ACS should respond 
        with the Patron Information Response message.
            63<language><transaction date><summary><institution id><patron identifier><terminal password><patron password><start item><end item>
        """
        summary = {
        'none':    '      ',
        'hold':    'Y     ',
        'overdue': ' Y    ',
        'charged': '  Y   ',
        'fine':    '   Y  ',
        'recall':  '    Y ',
        'unavail': '     Y'
        }

        # Request patron information
        self._request_new('63')
        self._request_addOpt_fixed(self.language, 3)
        self._request_addOpt_fixed(self._datestamp(), 18)
        #self._request_addOpt_fixed(sprintf("%-10s", summary[type]), 10);
        self._request_addOpt_fixed(summary[infoType], 10)
        self._request_addOpt_var('AO', self.institutionId)
        self._request_addOpt_var('AA', self.patron)
        self._request_addOpt_var('AC', self.terminalPassword, True)
        self._request_addOpt_var('AD', self.patronpwd, True)
        self._request_addOpt_var('BP', startItem, True)  # old function version used padded 5 digits, not sure why
        self._request_addOpt_var('BQ', endItem, True)    # old function version used padded 5 digits, not sure why
        return self._request_return()


    def sip_patron_information_response(self, response):
        """ Parse the response returned from Patron Information request messages (code 64)
        @param  string response    response string from the SIP2 backend
        @return array              parsed SIP2 response message
        
        @note SIP2 Protocol definition document:        
        The ACS must send this message in response to the Patron Information message.
            64<patron status><language><transaction date><hold items count><overdue items count><charged items count><fine items count><recall items count><unavailable holds count><institution id><patron identifier><personal name><hold items limit><overdue items limit><charged items limit><valid patron><valid patron password><currency type><fee amount><fee limit><items><home address><e-mail address><home phone number><screen message><print line>

        item: zero or more instances of one of the following, based on “summary” field of the Patron Information message:
        hold items AS variable-length optional field (this field should be sent for each hold item).
        overdue items AT variable-length optional field (this field should be sent for each overdue item).
        charged items AU variable-length optional field (this field should be sent for each charged item).
        fine items AV variable-length optional field (this field should be sent for each fine item).
        recall items BU variable-length optional field (this field should be sent for each recall item).
        unavailable hold items CD variable-length optional field (this field should be sent for each unavailable hold item).
        home address BD variable-length optional field
        e-mail address BE variable-length optional field
        home phone number BF variable-length optional field
        screen message AF variable-length optional field
        print line AG variable-length optional field
        """
        result = {'fixed': {
                            'PatronStatus':             response[2:16],
                            'Language':                 response[16:19],
                            'TransactionDate':          response[19:19+18],
                            'HoldItemsCount':           response[37:41],
                            'OverdueItemsCount':        response[41:45],
                            'ChargedItemsCount':        response[45:49],
                            'FineItemsCount':           response[49:53],
                            'RecallItemsCount':         response[53:57],
                            'UnavailableHoldsCount':    response[57:61]
                            },
                  'variable': self._response_parse_varData(response, 61)
                }

        self.last_response_parsed = result
        return result


    def sip_patron_status_request(self):
        """ Generate Patron Status (code 23) request messages in sip2 format
        @return string         SIP2 request message
        
        @note This message requires a patron password. If possible (not Sip1) 
        use the advanced version sip_patron_information_request() (63) 
        @note SIP2 Protocol definition document:        
        This message is used by the SC to request patron information from the 
        ACS. The ACS must respond to this command with a Patron Status Response 
        message.
            23<language><transaction date><institution id><patron identifier><terminal password><patron password>
        """
        # Server Response: Patron Status Response message.
        self._request_new('23');
        self._request_addOpt_fixed(self.language, 3);
        self._request_addOpt_fixed(self._datestamp(), 18);
        self._request_addOpt_var('AO', self.institutionId);
        self._request_addOpt_var('AA', self.patron);
        self._request_addOpt_var('AC', self.terminalPassword);
        self._request_addOpt_var('AD', self.patronpwd);
        return self._request_return();


    def sip_patron_status_response(self, response):
        """ Parse the response returned from Patron Status request messages (code 24)
        @param  string response    response string from the SIP2 backend
        @return array              parsed SIP2 response message
        
        @note This message requires a patron password. If possible (not Sip1) 
        use the advanced version sip_patron_information_response() (64) 
        @note SIP2 Protocol definition document:        
        The ACS must send this message in response to a Patron Status Request 
        message as well as in response to a Block Patron message.
            24<patron status><language><transaction date><institution id><patron identifier><personal name><valid patron><valid patron password><currency type><fee amount><screen message><print line>
        """
        result = {'fixed': {
                            'PatronStatus':     response[2:16],
                            'Language':         response[16:19],
                            'TransactionDate':  response[19:19+18]
                            },
                  'variable': self._response_parse_varData(response, 37)
                }

        self.last_response_parsed = result
        return result


    def sip_renew_request(self, itemIdentifier = '', titleIdentifier = '', nbDuDate = '', itemProperties = '', feeAcknowledged= 'N', noBlock = 'N', thirdPartyAllowed = 'N'):
        """ Generate Renew (code 29) request messages in sip2 format
        @param  string itemIdentifier      value for the variable length optional AB field
        @param  string titleIdentifier     value for the variable length optional AJ field
        @param  string nbDuDate            value for the due date portion of the fixed length field
        @param  string itemProperties      value for the variable length optional CH field
        @param  string feeAcknowledged     value for the variable length optional BO field
        @param  string noBlock             value for the blocking portion of the fixed length field
        @param  string thirdPartyAllowed   value for the party section of the fixed length field
        @return string                     SIP2 request message
        
        @note SIP2 Protocol definition document:        
        This message is used to renew an item. The ACS should respond with a 
        Renew Response message. Either or both of the “item identifier” and 
        “title identifier” fields must be present for the message to be useful.
            29<third party allowed><no block><transaction date><nb due date><institution id><patron identifier><patron password><item identifier><title identifier><terminal password><item properties><fee acknowledged>
        """
        self._request_new('29')
        self._request_addOpt_fixed(thirdPartyAllowed, 1)
        self._request_addOpt_fixed(noBlock, 1)
        self._request_addOpt_fixed(self._datestamp(), 18)
        if (nbDuDate != ''):
            # override default date due
            self._request_addOpt_fixed(self._datestamp(nbDuDate), 18)
        else:
            # send a blank date due to allow ACS to use default date due computed for item
            self._request_addOpt_fixed('', 18)
        self._request_addOpt_var('AO', self.institutionId)
        self._request_addOpt_var('AA', self.patron)
        self._request_addOpt_var('AD', self.patronpwd, True)
        self._request_addOpt_var('AB', itemIdentifier, True)
        self._request_addOpt_var('AJ', titleIdentifier, True)
        self._request_addOpt_var('AC', self.terminalPassword, True)
        self._request_addOpt_var('CH', itemProperties, True)
        self._request_addOpt_var('BO', feeAcknowledged, True) # Y or N

        return self._request_return()


    def sip_renew_response(self, response):
        """ Parse the response returned from Renew request messages (code 30)
        @param  string response    response string from the SIP2 backend
        @return array              parsed SIP2 response message
        
        @note SIP2 Protocol definition document:        
        This message must be sent by the ACS in response to a Renew message by 
        the SC.
            30<ok><renewal ok><magnetic media><desensitize><transaction date><institution id><patron identifier><item identifier><title identifier><due date><fee type><security inhibit><currency type><fee amount><media type><item properties><transaction id><screen message><print line>
        """
        result = {'fixed': {
                            'Ok':              response[2:3],
                            'RenewalOk':       response[3:4],
                            'MagneticMedia':   response[4:5],
                            'Desensitize':     response[5:6],
                            'TransactionDate': response[6:6+18]
                            },
                  'variable': self._response_parse_varData(response, 24)
                }

        self.last_response_parsed = result
        return result;


    def sip_renew_all_request(self, feeAcknowledged = 'N'):
        """ Generate Renew All (code 65) request messages in sip2 format
        @param  string feeAcknowledged     value for the optional variable length BO field
        @return string                     SIP2 request message
        
        @note SIP2 Protocol definition document:        
        This message is used to renew all items that the patron has checked out. 
        The ACS should respond with a Renew All Response message.
            65<transaction date><institution id><patron identifier><patron password><terminal password><fee acknowledged>
        """
        self._request_new('65')
        self._request_addOpt_var('AO', self.institutionId)
        self._request_addOpt_var('AA', self.patron)
        self._request_addOpt_var('AD', self.patronpwd, True)
        self._request_addOpt_var('AC', self.terminalPassword, True)
        self._request_addOpt_var('BO', feeAcknowledged, True) # Y or N
        return self._request_return()


    def sip_renew_all_response(self, response):
        """ Parse the response returned from Renew All request messages (cod 66)
        @param  string response    string from the SIP2 backend
        @return array              parsed SIP2 response message
        
        @note SIP2 Protocol definition document:        
        The ACS should send this message in response to a Renew All message from 
        the SC.
            66<ok ><renewed count><unrenewed count><transaction date><institution id><renewed items><unrenewed items><screen message><print line>
        """
        result = {'fixed': {
                            'Ok':              response[2:3],
                            'RenewedItems':    response[3:7],
                            'UnrenewedItems':  response[7:11],
                            'TransactionDate': response[11:11+18]
                            },
                  'variable': self._response_parse_varData(response, 29)
                }

        self.last_response_parsed = result
        return result;


    def sip_sc_resend_request(self):
        """ Generate ACS Resend (code 97) request messages in sip2 format
        Used to request a resend due to CRC mismatch - No sequence number is used
        @return string         SIP2 request message
        
        @note SIP2 Protocol definition document:        
        This message requests the SC to re-transmit its last message. It is sent 
        by the ACS to the SC when the checksum in a received message does not 
        match the value calculated by the ACS. The SC should respond by 
        re-transmitting its last message, This message should never include a 
        “sequence number” field, even when error detection is enabled, (see 
        “Checksums and Sequence Numbers” below) but would include a “checksum” 
        field since checksums are in use.
            96
        """
        self._request_new('97')
        return self._request_return(False)


    def sip_sc_status_request(self, statusCode = 0, maxPrintWidth = '080', protocolVersion = 2):
        """ Generate SC Status (code 99) request messages in sip2 format
        Selfcheck status message, this should be sent immediatly after login.
        @param  int statusCode         status code
        @param  int maxPrintWidth      message width (default 80)
        @param  int protocolVersion    protocol version (default 2)
        @return string|false           SIP2 request message or false on error
        
        status codes, from the spec
        0 SC unit is OK    1 SC printer is out of paper    2 SC is about to shut down
        
        @note SIP2 Protocol definition document:        
        The SC status message sends SC status to the ACS. It requires an ACS 
        Status Response message reply from the ACS. This message will be the 
        first message sent by the SC to the ACS once a connection has been 
        established (exception: the Login Message may be sent first to login to 
        an ACS server program). The ACS will respond with a message that 
        establishes some of the rules to be followed by the SC and establishes 
        some parameters needed for further communication.
            99<status code><max print width><protocol version>
        """
        if (statusCode < 0 or statusCode > 2):
            error = "Invalid status code passed to sip_sc_status_request"
            self.log.error(error)
            raise ValueError(error)

        self._request_new('99')
        self._request_addOpt_fixed(statusCode, 1)
        self._request_addOpt_fixed(maxPrintWidth, 3)
        #self._request_addOpt_fixed(sprintf("%03.2f",$version), 4)
        self._request_addOpt_fixed("{0:.2f}".format(protocolVersion), 4)
        return self._request_return()


    def sip_sc_status_response(self, response):
        """ Parse the response returned from SC Status request messages (code 98)
        @param  string response    response string from the SIP2 backend
        @return array              parsed SIP2 response message
        
        @note SIP2 Protocol definition document:        
        The ACS must send this message in response to a SC Status message. This 
        message will be the first message sent by the ACS to the SC, since it 
        establishes some of the rules to be followed by the SC and establishes 
        some parameters needed for further communication (exception: the Login 
        Response Message may be sent first to complete login of the SC).
            98<on-line status><checkin ok><checkout ok><ACS renewal policy><status update ok><off-line ok><timeout period><retries allowed><date / time sync><protocol version><institution id><library name><supported messages ><terminal location><screen message><print line>
        """
        result = {'fixed': {
                            'OnlineStatus':    response[2:3],
                            'CheckinOk':       response[3:4], # is Checkin by the SC allowed?
                            'CheckoutOk':      response[4:5], # is Checkout by the SC allowed?
                            'AcsRenewalPolicy':response[5:6], # is Renewal allowed?
                            'StatusUpdateOk':  response[6:7], # is patron status updating by the SC allowed ? (status update ok)
                            'OfflineOk':       response[7:8], # 
                            'TimeoutPeriod':   response[8:11],
                            'RetriesAllowed':  response[11:14],
                            'TransactionDate': response[14:14+18],
                            'ProtocolVersion': response[32:36]
                            },
                  'variable': self._response_parse_varData(response, 36)
                }

        self.last_response_parsed = result
        return result;


class Gossip(Sip2):
    """ Gossip Class
    Gossip is an SIP2 server implementation (Java) with an extension for enhanced
    payment options. It's possible to pay
     - a single outstanding position; "subtotal-payment"
     - an amount being below so total fees (but that sums up to complete
       positions being paid); "subtotal-payment"
     - an amount being below so total fees (but that might only pays one or more
       positions partially); "subtotal-payment + partial-fee-payment"

    SIP2 already provides everything for the payment part with positions. Example
     $transid = time();
     ammount    = '0.10';    // this is what you get doing a
                             // sip_patron_information_request(feeItems) - FA
     feeId      = '1059648'; // this is what you get doing a
                             // sip_patron_information_request(feeItems) - FB
     msg = gossip.sip_fee_paid_request('01', '00', ammount, 'EUR', feeId, transid);
     print(gossip.sip_fee_paid_response(gossip.get_response(msg) ));

    Fee positions can be fetched using a Y a position 7 in a Patron Information
    request (code 63)
    It returns these additional fields:
    FIELD    USED IN (Responses) Description
    FA       64, 38    Ammount of for fee position (alway dot as decimal seperator)
    FB       64, 38    ItemId of media for fee position
    FC       64, 38    Date when fee was generated (alway "dd.MM.yyyy")
    FD       64, 38    Description/title of fee position
    FE       64, 38    Cost type of fee position
    FF       64, 38    Description of cost type of fee position
    FG       38        Paid ammount for fee position

    Note: Sadly no official documentation for Gossip is available online. You
    can only contact the developer (J. Hofmann) via
    https://www.gbv.de/Verbundzentrale/serviceangebote/gossip-service-der-vzg

    @package
    @license    http://opensource.org/licenses/gpl-3.0.html
    @author     Tobias Zeumer <tzeumer@verweisungsform.de>
    @copyright  2016 Tobias Zeumer <tzeumer@verweisungsform.de>
    @link       PHP: https://github.com/tzeumer/Sip2Wrapper
    @link       Python: ???
    @version    $Id: sip2.class.php 28 2010-10-08 21:06:51Z cap60552 $
    @requires:  Python 3.4 (I think)
    """

    def __init__(self):
        Sip2.__init__(self)

        """Public variables """
        # @var string    Used protocol version (or extension)
        self._version        = 'Gossip'


    def sip_patron_information_request(self, infoType, start = '1', end = '5'):
        """ Generate Patron Information (code 63) request messages in sip2 format
        According to the specification:
        Only one category of items should be  requested at a time, i.e. it would
        take 6 of these messages, each with a different position set to Y, to
        get all the detailed information about a patron's items.
        @param  string infoType    type of information request (none, hold, overdue, charged, fine, recall, unavail, feeItems)
        @param  string start       value for BP field (default from 1 item)
        @param  string end         value for BQ field (default 5 items total)
        @return string             SIP2 request message
        """
        summary = {
        'none':     '       ',
        'hold':     'Y      ',
        'overdue':  ' Y     ',
        'charged':  '  Y    ',
        'fine':     '   Y   ',
        'recall':   '    Y  ',
        'unavail':  '     Y ',
        'feeItems': '      Y'
        }

        # Request patron information
        self._request_new('63')
        self._request_addOpt_fixed(self.language, 3)
        self._request_addOpt_fixed(self._datestamp(), 18)
        #self._request_addOpt_fixed(sprintf("%-10s", summary[type]), 10);
        self._request_addOpt_fixed(summary[infoType], 10)
        self._request_addOpt_var('AO', self.institutionId)
        self._request_addOpt_var('AA', self.patron)
        self._request_addOpt_var('AC', self.terminalPassword, True)
        self._request_addOpt_var('AD', self.patronpwd, True)
        self._request_addOpt_var('BP', start, True)  # old function version used padded 5 digits, not sure why
        self._request_addOpt_var('BQ', end, True)    # old function version used padded 5 digits, not sure why
        return self._request_return()
