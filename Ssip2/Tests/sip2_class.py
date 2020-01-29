import pprint
from sip2.sip2 import Gossip

pp = pprint.PrettyPrinter(indent=4)


""" TESTS 
#mySip.withCrc = False
#print (mySip._check_crc("09N20160419    12200820160419    122008APReading Room 1|AO830|AB830$28170815|AC|AY2AZEB80"))

#print (mySip.sip_block_patron_request('My Message'))
#print (mySip.sip_checkin_request('083$1234'))
#print (mySip.sip_checkout_request('083$1234'))
#print (mySip.sip_end_patron_session_request())
#print (mySip.sip_fee_paid_request(1, 0, 1.0))
#print (mySip.sip_hold_request('+', 1))
#print (mySip.sip_item_information_request('830$1234'))
#print (mySip.sip_item_status_update_request('830$1234'))
#print (mySip.sip_login_request('user', 'pw'))
#print (mySip.sip_patron_enable_request())
#print (mySip.sip_patron_information_request('hold'))
#print (mySip.sip_patron_information_request('overdue'))
#print (mySip.sip_patron_information_request('unavail'))
#print (mySip.sip_patron_status_request())
#print (mySip.sip_renew_request('830$421'))
#print (mySip.sip_renew_all_request())
#print (mySip.sip_sc_resend_request())
#print (mySip.sip_sc_status_request())

#x = mySip.sip_checkin_response('101YUN20160427    130429AOTUHH|AB830$28328201|AQLS1|AJDigital ävionics handbook;          2: Development 2. ed CRC Pres 2007|AA08300005811|AY5AZD8E7')
#x = mySip.sip_checkout_response('121NUY20160511    112658AOTUB HH|AA08300287914|AB830$26482330|AJStatik                              / Gross, Dietm 12.,  Springer 2013|AH08.06.2016|AY4AZDC6F')
#x = mySip.sip_end_patron_session_response('36Y20080228    145537AOWOHLERS|AAX00000000|AY9AZF474')
#x = mySip.sip_fee_paid_response('38Y20160429    212935AOTUHH|AA00180530690|BK00180530690-20160429-212934-954-257|BV2.00|CG81766|FA1.00|FB830$24602811|FC08.12.2014|FDStudentisches Wohnen in Baden-Wuerttemberg: Bestandsaufnahm|FE8|FFLeihfristberschreitung|FG1.00|CG521111|FA1.00|FB830$34278992|FC08.12.2014|FDLe Corbusier - Pavillon Suisse: the biography o/Zaknic, Ivan|FE8|FFLeihfristberschreitung|FG1.00|AY3AZ8EA3')
#x = mySip.sip_hold_response('???')
#x = mySip.sip_item_information_response('1803000120160511    071022CF0|AB830$23487118|AJ17.2004: Marine structures|AQMAG|AY6AZE9B7')
#x = mySip.sip_item_status_update_response('???')
#x = mySip.sip_login_response('941AY1AZFDFC')
#x = mySip.sip_patron_enable_response('???')
#x = mySip.sip_patron_information_response('64              00320160511    084442000000000000        0000AOTUB HH|AA08300076190|AEMalte Baesler|BLY|CQY|BHEUR|BV0.00|BEmalte.baesler@tuhh.de|AY6AZD946')
#x = mySip.sip_patron_status_response('???')
#x = mySip.sip_renew_response('300NUU20080228    222232AOWOHLERS|AAX00000241|ABM02400028262|AJFolksongs of Britain and Ireland|AH5/23/2008,23:59|CH|AFOverride required to exceed renewal limit.|AY1AZCDA5')
#x = mySip.sip_renew_all_response('???')
#x = mySip.sip_sc_status_response('98YYYYNN90099920160511    0605582.00AOTUB HH|AMTUHH                                    |BXYYYNYYYYYYYNNNYY|SVGossip gossip-1.1.2; scala-Version: 2.11.8; sbt-Version: 0.13.11; built: Mon Apr 18 23:18:00 CEST 2016|AY2AZC870')
#pp.pprint(x)
"""
