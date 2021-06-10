SIP2 Python Client: Simple Interchange Protocol Client for Python

# About
A Python SIP2 client. It also supports Gossip.

# Purpose
This was (nearly) my first go with Python. I thought the source might have a better time on Github (well, after a two month break I forgot what I already figured out about publishing a real Python package) than on my drive.
Ideas: Could be used to build some selfcheck device application for libraries. Or use it for some kind of automation...  

# Usage
There are just three files. File sip2.py is a low level implemntation of SIP2/Gossip while wrapper.py makes the handling a little bit more comfortable. Check comments of both files.
File message_lookup.py could be used for advanced programming purposes. Maybe...

# Changelog
* 2021-06-10 Release v1.1.0 
	* Fixed typo (wrong case) and merged an exception handling for TSL. Thank @yefuwang and @MarkTr
* 2018-06-11 Release v1.0.0

# More about SIP2
Standard Interchange Protocol 2, Standard: http://mws9.3m.com/mws/mediawebserver.dyn?6666660Zjcf6lVs6EVs66S0LeCOrrrrQ-

Gossip is short for "Good Old Server for Standard Interchange Protocol". Gossip is an SIP2 server implementation (Java) with an extension for enhanced payment options. It's possible to pay
* a single outstanding position; "subtotal-payment"
* an amount being below the total fees (but that sums up to complete positions being paid); "subtotal-payment"
* an amount being below the total fees (but that might only pay one or more positions partially); "subtotal-payment + partial-fee-payment"

Note: Sadly no official documentation for Gossip is available online. You can only contact the developer via https://www.gbv.de/Verbundzentrale/serviceangebote/gossip-service-der-vzg

# Source
The primary source is at https://github.com/tzeumer/SIP2-Client-for-Python. There is also a package at pypi.org: https://packaging.python.org/tutorials/packaging-projects/. It's the only one I ever released, so I have to figure out the process every time - an might forget it completely ;)