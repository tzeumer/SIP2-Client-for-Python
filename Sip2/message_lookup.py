""" Structured version of field definitions as described in the 3M Sip2 protocol definition document

Could probably be used to explain requests and responses? Or to check (and configure) valid values?

Schema:
    'id_as_in_protocol_definition_or_CamelCased_name_if_no_id': {
            'fieldName':        'name_as_in_protocol_definition',
            'fieldID':          'id_as_in_protocol_definition',
            'fieldDescription': "description_as_in_protocol_definition",
            'fixedLength':      False or int (char count),
            'values': False (vairable data) / Dict (known entries) / List (multiple values defined by position)
    },

'values': Might can be either False, a Dictionary or a List. 
    False means, that there are no predefined and fixed values by the protocol definition.
    A dictionary explains a single returned value (like 'Y': 'Means true'). Note that some list might be extended by a ASC/SIP-Server
    A list is used if a long string with multiple information that is identified by string positions is returned (used for for PatronStatus, Summary, BX)
"""  
fieldDefinitions = {
    'AcsRenewalPolicy': {
            'fieldName':        'ACS renewal policy',
            'fieldID':          '',
            'fieldDescription': '1-char, fixed-length field: Y or N. A Y indicates that the SC is allowed by the ACS to process renewal requests as a policy. This field was called “renewal ok” in Version 1.00 of the protocol.',
            'fixedLength':      1,
            'values': {
                'Y': 'SC is allowed by the ACS to process renewal requests as a policy',
                'N': 'SC is denied by the ACS to process renewal requests as a policy'
            }
            #'minVersion': 1
            #'requiredBy': ('sip_sc_status_response')
            #'optionalWith': ()                     
    },
    'Alert': {
            'fieldName':        'alert',
            'fieldID':          '',
            'fieldDescription': "1-char, fixed-length field: Y or N. A Y in the alert field will generate an audible sound at the SC. The alert will indicate conditions like articles on hold, articles belonging to another library branch, or other alert conditions as determined by the ACS. The alert signal will alert the library staff to special article handling conditions during discharging operations.",
            'fixedLength':      1,
            'values': {
                'Y': 'Play sound',
                'N': 'Don\'t play sound'
            }
            #'minVersion': 1
            #'requiredBy': ('sip_checkin_response')
            #'optionalWith': ()
    },
    'Available': {
            'fieldName':        'available',
            'fieldID':          '',
            'fieldDescription': "1-char, fixed-length field: Y or N. A Y indicates that the item is available; it is not checked out or on hold.",
            'fixedLength':      1,
            'values': {
                'Y': 'Item available',
                'N': 'Item unavailable'
            }
    },
    'AL': {
            'fieldName':        'blocked card msg',
            'fieldID':          'AL',
            'fieldDescription': "variable-length field. This field indicates the reason the patron card was blocked",
            'fixedLength':      False,
            'values': False
            #'minVersion': 1
            #'requiredBy': ('sip_block_patron_request')
            #'optionalWith': ()
    },
    'BI': {
            'fieldName':        'cancel',
            'fieldID':          'BI',
            'fieldDescription': "1-char field: Y or N. This field should be set to Y for a Checkout command being used to cancel a failed Checkin command, or for a Checkin command being used to cancel a failed Checkout command. It should be set to N for all other Checkout or Checkin commands.",
            'fixedLength':      1,
            'values': {
                'Y': 'Cancel checkout/checkin',
                'N': 'default'
            }
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_checkin_request', 'sip_checkout_request')

    },
    'CardRetained': {
            'fieldName':        'card retained',
            'fieldID':          '',
            'fieldDescription': "1-char, fixed-length field: Y or N. This field notifies the ACS that the patron’s library card has been retained by the SC. The ACS may ignore this field or notify the library staff that the patron's card has been retained by the SC.",
            'fixedLength':      1,
            'values': {
                'Y': 'Card retained by SC',
                'N': 'Card valid'
            }
            #'minVersion': 1
            #'requiredBy': ('sip_block_patron_request')
            #'optionalWith': ()
    },
    'AU': {
            'fieldName':        'charged items',
            'fieldID':          'AU',
            'fieldDescription': "variable-length field. This field should be sent for each charged item.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_checkout_request', 'sip_patron_information_response', 'sip_renew_request')
    },
    'ChargedItemsCount': {
            'fieldName':        'charged items count',
            'fieldID':          '',
            'fieldDescription': "4-char, fixed-length field. This field should contain the number of charged items for this patron, from 0000 to 9999. If this information is not available or unsupported this field should contain four blanks (code $20).",
            'fixedLength':      4,
            'values': False
            #'minVersion': 2
            #'requiredBy': ('sip_patron_information_response')
            #'optionalWith': ()
    },
    'CB': {
            'fieldName':        'charged items limit',
            'fieldID':          'CB',
            'fieldDescription': "4-char, fixed-length field. This field should contain the limit number of charged items for this patron from 0000 to 9999.",
            'fixedLength':      4,
            'values': False
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_patron_information_response')
    },
    'CheckinOk': {
            'fieldName':        'checkin ok',
            'fieldID':          '',
            'fieldDescription': "1-char, fixed-length field: Y or N. A Y indicates that the SC is allowed to check in items.",
            'fixedLength':      1,
            'values': {
                'Y': 'SC is allowed to check in items',
                'N': 'SC is not allowed to check in items'
            }
            #'minVersion': 1
            #'requiredBy': ('sip_sc_status_response')
            #'optionalWith': ()                     
    },
    'CheckoutOk': {
            'fieldName':        'checkout ok',
            'fieldID':          '',
            'fieldDescription': "1-char, fixed-length field: Y or N. A Y indicates that the SC is allowed to check out items.",
            'fixedLength':      1,
            'values': {
                'Y': 'SC is allowed to check out items',
                'N': 'SC is not allowed to check out items'
            }
            #'minVersion': 1
            #'requiredBy': ('sip_sc_status_response')
            #'optionalWith': ()                     
    },
    'AZ': {
            'fieldName':        'checksum',
            'fieldID':          'AZ',
            'fieldDescription': "4-char, fixed-length message checksum, used for checksumming messages when error detection is enabled.",
            'fixedLength':      4,
            'values': False
    },
    'CirculationStatus': {
            'fieldName':        'circulation status',
            'fieldID':          '',
            'fieldDescription': "2-char, fixed-length field (00 thru 99). The circulation status of an item. The following statuses are defined:\nVal Status\n01  other\n02  on order\n03  available\n04  charged\n05  charged; not to be recalled until earliest recall date\n06  in process\n07  recalled\n08  waiting on hold shelf\n09  waiting to be re-shelved\n10  in transit between library locations\n11  claimed returned\n12  lost\n13  missing",
            'fixedLength':      2,
            'values': {
                '01': 'other',
                '02': 'on order',
                '03': 'available',
                '04': 'charged',
                '05': 'charged; not to be recalled until earliest recall date',
                '06': 'in process',
                '07': 'recalled',
                '08': 'waiting on hold shelf',
                '09': 'waiting to be re-shelved',
                '10': 'in transit between library locations',
                '11': 'claimed returned',
                '12': 'lost',
                '13': 'missing',
            }
            #'minVersion': 2
            #'requiredBy': ('sip_item_information_response')
            #'optionalWith': ()
    },                                        
    'BH': {
            'fieldName':        'currency type',
            'fieldID':          'BH',
            'fieldDescription': "3-char, fixed-length field. The value for currency type follows ISO Standard 4217:1995, using the 3-character alphabetic code part of the standard. A portion of the standard is provided here as examples:\nVal Definition\nUSD US Dollar\nCAD Canadian Dollar\nGBP Pound Sterling\nFRF French Franc\nDEM Deutsche Mark\nITL Italian Lira\nESP Spanish Peseta\nJPY Yen",
            'fixedLength':      3,
            'values': {
                'USD': 'Dollar (US)',
                'EUR': 'Euro'
            }
            #'minVersion': 2
            #'requiredBy': ('sip_fee_paid_request')
            #'optionalWith': ('sip_checkout_response', 'sip_item_information_response', 'sip_patron_information_response', 'sip_patron_status_response', 'sip_renew_response')
    },
    'AP': {
            'fieldName':        'current location',
            'fieldID':          'AP',
            'fieldDescription': "variable-length field; the current location of the item. 3M SelfCheck system software could set this field to the value of the 3M SelfCheck system terminal location on a Checkin message.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 1
            #'requiredBy': ('sip_checkin_request')
            #'optionalWith': ('sip_item_information_response VERSION 2')
    },
    'DateTimeSync': {
            'fieldName':        'date / time sync',
            'fieldID':          '',
            'fieldDescription': "18-char, fixed-length field: YYYYMMDDZZZZHHMMSS. May be used to synchronize clocks. The date and time should be expressed according to the ANSI standard X3.30 for date and X3.43 for time. 000000000000000000 indicates a unsupported function. When possible local time is the preferred format.",
            'fixedLength':      18,
            'values': False
            #'minVersion': 1
            #'requiredBy': ('sip_sc_status_response')
            #'optionalWith': ()                     
    },
    'Desensitize': {
            'fieldName':        'desensitize',
            'fieldID':          '',
            'fieldDescription': "1-char, fixed-length field: Y or N or (obsolete)U. A Y in this field indicates that the SC unit should desensitize the article. An N in this field indicates that the article will not be desensitized, i.e. some non-circulation books are allowed to be checked out, but not removed from the library. A U indicates that the ACS does not know if the item should or should not be desensitized, and will be treated by the SC the same as an N.",
            'fixedLength':      1,
            'values': {
                'Y': 'Desensitize item',
                'N': 'Don\'t desensitize item'
            }
            #'minVersion': 1
            #'requiredBy': ('sip_checkout_response', 'sip_renew_response')
            #'optionalWith': ()
    },
    'AH': {
            'fieldName':        'due date',
            'fieldID':          'AH',
            'fieldDescription': "variable-length field. This date field is not necessarily formatted with the ANSI standard X3.30 for date and X3.43 for time. Since it is a variable-length field the ACS can send this date field in any format it wishes.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 1
            #'requiredBy': ('sip_checkout_response', 'sip_renew_response')
            #'optionalWith': ('sip_item_information_response')
    },      
    'BE': {
            'fieldName':        'e-mail address',
            'fieldID':          'BE',
            'fieldDescription': "variable-length field. The patron’s e-mail address.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_patron_information_response')
    },                                  
    'BQ': {
            'fieldName':        'end item',
            'fieldID':          'BQ',
            'fieldDescription': "variable-length field. The number of the last item to be returned. The Patron Information message allows the SC to request the ACS to send a list of items that a patron has checked out, or that are overdue, etc. This field specifies the number in that list of the last item to be sent to the SC. For instance, if the SC had requested - via the summary, start item, and end item fields of the Patron Information message - to have the seventh through twelfth items in the list of the patron’s overdue items sent in the Patron Information response, this field would have the value “12”. A numbering system that starts with 1 is assumed. This allows the requester to have control over how much data is returned at a time, and also to get the whole list in sequential or some other order using successive messages/responses.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_patron_information_request')
    },
    'EndSession': {
            'fieldName':        'end session',
            'fieldID':          '',
            'fieldDescription': "1-char, fixed-length field: Y or N. Y indicates that the ACS has ended the patron’s session in response to the End Patron Session message. N would be an error condition.",
            'fixedLength':      1,
            'values': {
                'Y': 'Patron session closed',
                'N': 'Error on closing patron session'
            }
            #'minVersion': 1
            #'requiredBy': ('sip_end_patron_session_response')
            #'optionalWith': ()
    },
    'BW': {
            'fieldName':        'expiration date',
            'fieldID':          'BW',
            'fieldDescription': "18-char, fixed-length field: YYYYMMDDZZZZHHMMSS; the date, if any, that the hold will expire.",
            'fixedLength':      18,
            'values': False
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_hold_request')
    },
    'BO': {
            'fieldName':        'fee acknowledged',
            'fieldID':          'BO',
            'fieldDescription': "1-char field: Y or N.\nIf this field is N in a Checkout message and there is a fee associated with checking out the item, the ACS should tell the SC in the Checkout Response that there is a fee, and refuse to check out the item. If the SC and the patron then interact and the patron agrees to pay the fee, this field will be set to Y on a second Checkout message, indicating to the ACS that the patron has acknowledged the fee and checkout of the item should not be refused just because there is a fee associated with the item.\nOne could say that use of the fee acknowledged field should not be necessary for renewals - the patron should already know that there is a fee associated with the item, having agreed to it when the item was initially checked out - but the field is provided as an optional field with the renewal messages for those systems that take the view that patrons should always acknowledge fees.\nPresumably, a Y value in the fee acknowledged field of a Renew All message would mean that the patron had agreed to all fees associated with all items being renewed.\nFee acknowledged exists as an optional field on the Hold command to acknowledge a charge to put a hold on an item. Some libraries, under some conditions, levy a charge to put a hold on an item; fee acknowledged could be used in these situations to allow the hold charge to be agreed to before the hold was actually put on the item.",
            'fixedLength':      1,
            'values': {
                'Y': 'Patron accepts fee',
                'N': 'Patron does not accept fee'
            }
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_checkout_request', 'sip_hold_request', 'sip_renew_request', 'sip_renew_all_request')
    },
    'BV': {
            'fieldName':        'fee amount',
            'fieldID':          'BV',
            'fieldDescription': "variable-length field. This contains a money amount in whatever currency type is specified by the currency type field of the same message. For example, \“115.57\” could specify $115.57 if the currency type was USD (US Dollars).",
            'fixedLength':      False,
            'values': False
            #'minVersion': 2
            #'requiredBy': ('sip_fee_paid_request')
            #'optionalWith': ('sip_checkout_response', 'sip_item_information_response', 'sip_patron_information_response', 'sip_patron_status_response', 'sip_renew_response')
    },
    'CG': {
            'fieldName':        'fee identifier',
            'fieldID':          'CG',
            'fieldDescription': "variable-length field. Identifies a specific fee, possibly in combination with fee type. This identifier would have to be user-selected from a list of fees.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_fee_paid_request')
    },
    'CC': {
            'fieldName':        'fee limit',
            'fieldID':          'CC',
            'fieldDescription': "variable-length field. This field indicates that the limiting value for fines and fees that the patron is allowed to accumulate in their account. It is a money amount in whatever currency type is specified by the currency type field of the same message. For example, \“50.00\” could specify $50.00 if the currency type was USD (US Dollars).",
            'fixedLength':      False,
            'values': False
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_patron_information_response')
    },
    'BT': {
            'fieldName':        'fee type',
            'fieldID':          'BT',
            'fieldDescription': "2-char, fixed-length field (01 thru 99). Enumerated type of fee, from the following table:\nVal Fee Type\n01  other/unknown\n02  administrative\n03  damage\n04  overdue\n05  processing\n06  rental\n07  replacement\n08  computer access charge\n09  hold fee",
            'fixedLength':      2,
            'values': {
                '01': 'other/unknown',
                '02': 'administrative',
                '03': 'damage',
                '04': 'overdue',
                '05': 'processing',
                '06': 'rental',
                '07': 'replacement',
                '08': 'computer access charge',
                '09': 'hold fee',
            }
            #'minVersion': 2
            #'requiredBy': ('sip_fee_paid_request', 'sip_item_information_response')
            #'optionalWith': ('sip_checkout_response', 'sip_renew_response')
    },
    'AV': {
            'fieldName':        'fine items',
            'fieldID':          'AV',
            'fieldDescription': "variable-length field. This field should be sent for each fine item.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_patron_information_response')
    },
    'FineItemsCount': {
            'fieldName':        'fine items count',
            'fieldID':          '',
            'fieldDescription': "4-char, fixed length field. This field should contain the number of fine items for this patron, from 0000 to 9999. If this information is not available or unsupported this field should contain four blanks (code $20).",
            'fixedLength':      4,
            'values': False
            #'minVersion': 2
            #'requiredBy': ('sip_patron_information_response')
            #'optionalWith': ()
    },
    'AS': {
            'fieldName':        'hold items',
            'fieldID':          'AS',
            'fieldDescription': "variable-length field. This field should be sent for each hold item.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_patron_information_response')
    },                    
    'HoldItemsCount': {
            'fieldName':        'hold items count',
            'fieldID':          '',
            'fieldDescription': "4-char, fixed length field. This field should contain the number of hold items for this patron, from 0000 to 9999. If this information is not available or unsupported this field should contain four blanks (code $20).",
            'fixedLength':      4,
            'values': False
            #'minVersion': 2
            #'requiredBy': ('sip_patron_information_response')
            #'optionalWith': ()
    },                    
    'BZ': {
            'fieldName':        'hold items limit',
            'fieldID':          'BZ',
            'fieldDescription': "4-char, fixed-length field. This field should contain the limit number of hold items for this patron, from 0000 to 9999.",
            'fixedLength':      4,
            'values': False
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_patron_information_response')
    },
    'HoldMode': {
            'fieldName':        'hold mode',
            'fieldID':          '',
            'fieldDescription': "1-char, fixed-length field. If mode is :\n+ add patron to the hold queue for the item\n- delete patron from the hold queue for the item\n* change the hold to match the message parameters",
            'fixedLength':      1,
            'values': {
                '+': 'Add patron to the hold queue for the item',
                '-': 'Delete patron from the hold queue for the item',
                '*': 'Change the hold to match the message parameters',
            }
            #'minVersion': 2
            #'requiredBy': ('sip_hold_request')
            #'optionalWith': ()
    },
    'CM': {
            'fieldName':        'hold pickup date',
            'fieldID':          'CM',
            'fieldDescription': "18-char, fixed-length field: YYYYMMDDZZZZHHMMSS. The date that the hold expires.",
            'fixedLength':      18,
            'values': False
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_item_information_response')
    },
    'CF': {
            'fieldName':        'hold queue length',
            'fieldID':          'CF',
            'fieldDescription': "variable-length field. Number of patrons requesting this item.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_item_information_response')
    },
    'BY': {
            'fieldName':        'hold type',
            'fieldID':          'BY',
            'fieldDescription': "1-char, fixed-length field (1 thru 9). The type of hold:\nVal  Hold Type\n1    other\n2    any copy of a title\n3    a specific copy of a title\n4    any copy at a single branch or sublocation",
            'fixedLength':      1,
            'values': {
                '1': 'other',
                '2': 'any copy of a title',
                '3': 'a specific copy of a title',
                '4': 'any copy at a single branch or sublocation',
            }
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_hold_request')
    },
    'BD': {
            'fieldName':        'home address',
            'fieldID':          'BD',
            'fieldDescription': "variable-length field; the home address of the patron.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_patron_information_response')
    },
    'BF': {
            'fieldName':        'home phone number',
            'fieldID':          'BF',
            'fieldDescription': "variable-length field; the patron’s home phone number.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_patron_information_response')
    },
    'AO': {
            'fieldName':        'institution id',
            'fieldID':          'AO',
            'fieldDescription': "variable-length field; the library’s institution ID.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 1
            #'requiredBy': ('sip_block_patron_request', 'sip_checkin_request', 'sip_checkin_response', 'sip_checkout_request', 'sip_checkout_response', 'sip_end_patron_session_request', 'sip_end_patron_session_response', 'sip_fee_paid_request', 'sip_fee_paid_response', 'sip_hold_request', 'sip_item_information_request', 'sip_item_status_update_request', 'sip_patron_enable_request', 'sip_patron_enable_response', 'sip_patron_information_request', 'sip_patron_information_response', 'sip_patron_status_request', 'sip_patron_status_response', 'sip_renew_request', 'sip_renew_response', 'sip_renew_all_request', 'sip_renew_all_response', 'sip_sc_status_response')
            #'optionalWith': ()
    },
    'AB': {
            'fieldName':        'item identifier',
            'fieldID':          'AB',
            'fieldDescription': "variable-length field; the article bar-code. This information is needed by the SC to verify that the article that was checked in matches the article bar-code at the SC.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 1
            #'requiredBy': ('sip_checkin_request', 'sip_checkin_response', 'sip_checkout_request', 'sip_checkout_response', 'sip_item_information_request', 'sip_item_information_response', 'sip_item_status_update_request', 'sip_item_status_update_response', 'sip_renew_response')
            #'optionalWith': ('sip_hold_request', 'sip_renew_request')
    },
    'CH': {
            'fieldName':        'item properties',
            'fieldID':          'CH',
            'fieldDescription': "variable-length field. This field may contain specific item information that can be used for identifying a item, such as item weight, size, security marker, etc. It may possibly used for security reasons. ACSs are encouraged to store this information in their database.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_checkin_request', 'sip_checkin_response', 'sip_checkout_response', 'sip_item_information_response', 'sip_item_status_update_request', 'sip_item_status_update_response', 'sip_renew_response')
    },
    'ItemPropertiesOk': {
            'fieldName':        'item properties ok',
            'fieldID':          '',
            'fieldDescription': "1-char field. A '1' in this field indicates that the item properties have been stored on the ACS database. Any other value indicates that item properties were not stored.",
            'fixedLength':      1,
            'values': {
                '0': 'Item properties not stored in ACS databse',
                '1': 'Item properties saved in ACS database'
            }
            #'minVersion': 2
            #'requiredBy': ('sip_item_status_update_response')
            #'optionalWith': ()                         
    },
    'Language': {
            'fieldName':        'language',
            'fieldID':          '',
            'fieldDescription': "3-char, fixed-length field. The ACS may use this field’s information to format screen and print messages in the language as requested by the Patron. Code 000 in this field means the language is not specified.\nCode  Language\n000   Unknown (default)\n001   English\n002   French\n003   German\n004   Italian\n005   Dutch\n006   Swedish\n007   Finnish\n008   Spanish\n009   Danish\n010   Portuguese\n011   Canadian-French\n012   Norwegian\n013   Hebrew\n014   Japanese\n015   Russian\n016   Arabic\n017   Polish\n018   Greek\n019   Chinese\n020   Korean\n021   North American Spanish\n022   Tamil\n023   Malay\n024   United Kingdom\n025   Icelandic\n026   Belgian\n027   Taiwanese",
            'fixedLength':      3,
            'values': {
                '000': 'Unknown (default)',
                '001': 'English',
                '002': 'French',
                '003': 'German',
                '004': 'Italian',
                '005': 'Dutch',
                '006': 'Swedish', 
                '007': 'Finnish',
                '008': 'Spanish',
                '009': 'Danish',
                '010': 'Portuguese',
                '011': 'Canadian-French',
                '012': 'Norwegian',
                '013': 'Hebrew',
                '014': 'Japanese',
                '015': 'Russian',
                '016': 'Arabic',
                '017': 'Polish',
                '018': 'Greek',
                '019': 'Chinese', 
                '020': 'Korean',
                '021': 'North American Spanish', 
                '022': 'Tamil', 
                '023': 'Malay', 
                '024': 'United Kingdom', 
                '025': 'Icelandic', 
                '026': 'Belgian', 
                '027': 'Taiwanese'
            }
            #'minVersion': 1
            #'requiredBy': ('sip_patron_enable_response', 'sip_patron_information_request', 'sip_patron_information_response', 'sip_patron_status_request', 'sip_patron_status_response')
            #'optionalWith': ()                    
    },
    'AM': {
            'fieldName':        'library name',
            'fieldID':          'AM',
            'fieldDescription': "variable-length field; the library’s name.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 1
            #'requiredBy': ()
            #'optionalWith': ('sip_sc_status_response')                     
    },
    'CP': {
            'fieldName':        'location code',
            'fieldID':          'CP',
            'fieldDescription': "variable-length field; the location code of the SC unit. This code will be configurable on the SC.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_login_request')                    
    },
    'CO': {
            'fieldName':        'login password',
            'fieldID':          'CO',
            'fieldDescription': "variable-length field; the password for the SC to use to login to the ACS. It is possible for this field to be encrypted; see the “PWD algorithm” field’s definition.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 2
            #'requiredBy': ('sip_login_request')
            #'optionalWith': ()                    
    },
    'CN': {
            'fieldName':        'login user id',
            'fieldID':          'CN',
            'fieldDescription': "variable-length field; the user id for the SC to use to login to the ACS. It is possible for this field to be encrypted; see the “UID algorithm” field’s definition.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 2
            #'requiredBy': ('sip_login_request')
            #'optionalWith': ()                    
    },
    'MagneticMedia': {
            'fieldName':        'magnetic media',
            'fieldID':          '',
            'fieldDescription': "1-char, fixed-length field: Y or N or U. A 'Y' in this field indicates that this article is magnetic media and the SC will then handle the security discharge accordingly. A 'N' in this field indicates that the article is not magnetic media. A 'U' indicates that the ACS does not identify magnetic media articles. ACS vendors are encouraged to store and provide article magnetic media identification.",
            'fixedLength':      1,
            'values': {
                'Y': 'Item is a magnetic secured media',
                'N': 'Item is not a magnetic secured media',
                'U': 'Unknown if item is a magnetic secured media',
            }
            #'minVersion': 1
            #'requiredBy': ('sip_checkin_response', 'sip_checkout_response', 'sip_renew_response')
            #'optionalWith': ()
            
    },
    'MaxPrintWidth': {
            'fieldName':        'max print width',
            'fieldID':          '',
            'fieldDescription': "3-char, fixed-length field. This is the maximum number of characters that the SC printer can print in one line. If the ACS wants to print longer messages it can send them in another print line field.",
            'fixedLength':      3,
            'values': False
            #'minVersion': 1
            #'requiredBy': ('sip_sc_status_request')
            #'optionalWith': ()
    },
    'CK': {
            'fieldName':        'media type',
            'fieldID':          'CK',
            'fieldDescription': "3-char, fixed-length field; enumerated media type, from the following table:\nVal Media Type\n000 other\n001 book\n002 magazine\n003 bound journal\n004 audio tape\n005 video tape\n006 CD/CDROM\n007 diskette\n008 book with diskette\n009 book with CD\n010 book with audio tape",
            'fixedLength':      3,
            'values': {
                '000': 'other',
                '001': 'book',
                '002': 'magazine',
                '003': 'bound journal',
                '004': 'audio tape',
                '005': 'video tape',
                '006': 'CD/CDROM',
                '007': 'diskette',
                '008': 'book with diskette',
                '009': 'book with CD',
                '010': 'book with audio tape',
            }
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_checkin_response', 'sip_checkout_response', 'sip_item_information_response', 'sip_renew_response')
    },
    'NbDueDate': {
            'fieldName':        'nb due date',
            'fieldID':          '',
            'fieldDescription': "18-char, fixed-length field: YYYYMMDDZZZZHHMMSS. This is the no block due date that articles were given during off-line (store and forward) operation.",
            'fixedLength':      18,
            'values': False
            #'minVersion': 1
            #'requiredBy': ('sip_checkout_request', 'sip_renew_request')
            #'optionalWith': ()
    },
    'NoBlock': {
            'fieldName':        'no block',
            'fieldID':          '',
            'fieldDescription': "1-char, fixed-length field: Y or N. This field notifies the ACS that the article was already checked in or out while the ACS was not on-line. When this field is Y, the ACS should not block this transaction because it has already been executed. The SC can perform transactions while the ACS is off-line. These transactions are stored and will be sent to the ACS when it comes back on-line.",
            'fixedLength':      1,
            'values': {
                'Y': 'ACS must not block item checkin/checkout because it was already executed offline',
                'N': 'ACS should allow or checkin/checkout according to its policies '
            }
            #'minVersion': 1
            #'requiredBy': ('sip_checkin_request', 'sip_checkout_request', 'sip_renew_request')
            #'optionalWith': ()
    },
    'OfflineOk': {
            'fieldName':        'off-line ok',
            'fieldID':          '',
            'fieldDescription': "1-char, fixed-length field: Y or N. This field should be Y if the ACS supports the off-line operation feature of the SC. The ACS must also support no block charge requests from the SC when it comes back on-line.",
            'fixedLength':      1,
            'values': {
                'Y': 'ACS supports offline operations',
                'N': 'ACS does not support offline operations'
            }
            #'minVersion': 1
            #'requiredBy': ('sip_sc_status_response')
            #'optionalWith': ()                     
    },
    'Ok': {
            'fieldName':        'ok',
            'fieldID':          '',
            'fieldDescription': "1-char, fixed-length field: 0 or 1. A '1' in this field indicates that the requested action was allowable and completed successfully. A ‘0’ indicates that the requested action was not allowable or did not complete successfully. This field is described in the preliminary NISO standard Z39.70-199x.",
            'fixedLength':      1,
            'values': {
                '0': 'Requested action failed',
                '1': 'Requested action was completed successfully'
            }
            #'minVersion': 1
            #'requiredBy': ('sip_checkin_response', 'sip_checkout_response', 'sip_login_response', 'sip_renew_response', 'sip_renew_all_response')
            #'optionalWith': ()
    },
    'OnlineStatus': {
            'fieldName':        'on-line status',
            'fieldID':          '',
            'fieldDescription': "1-char, fixed-length field: Y or N. This field is provided by the ACS to indicate whether the system is on or off-line. For example the ACS can use this field to notify the SC that it is going off-line for routine maintenance.",
            'fixedLength':      1,
            'values': {
                'Y': 'ACS is online',
                'N': 'ACS is offline'
            }
            #'minVersion': 1
            #'requiredBy': ('sip_sc_status_response')
            #'optionalWith': ()                     
    },
    'AT': {
            'fieldName':        'overdue items',
            'fieldID':          'AT',
            'fieldDescription': "variable-length field. This field should be sent for each overdue item.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_patron_information_response')
    },
    'OverdueItemsCount': {
            'fieldName':        'overdue items count',
            'fieldID':          '',
            'fieldDescription': "4-char, fixed-length field. This field should contain the number of overdue items for this patron, from 0000 to 9999. If this information is not available or unsupported this field should contain four blanks (code $20).",
            'fixedLength':      4,
            'values': False
            #'minVersion': 2
            #'requiredBy': ('sip_patron_information_response')
            #'optionalWith': ()
    },
    'CA': {
            'fieldName':        'overdue items limit',
            'fieldID':          'CA',
            'fieldDescription': "4-char, fixed-length field. This field should contain the limit number of overdue items for this patron, from 0000 to 9999.",
            'fixedLength':      4,
            'values': False
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_patron_information_response')
    },                    
    'BG': {
            'fieldName':        'owner',
            'fieldID':          'BG',
            'fieldDescription': "variable-length field. The field might contain the name of the institution or library that owns the item.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_item_information_response')
    },
    'AA': {
            'fieldName':        'patron identifier',
            'fieldID':          'AA',
            'fieldDescription': "variable-length field; an identifying value for the patron.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 1
            #'requiredBy': ('sip_block_patron_request', 'sip_checkout_request', 'sip_checkout_response', 'sip_end_patron_session_request', 'sip_end_patron_session_response', 'sip_fee_paid_request', 'sip_fee_paid_response', 'sip_hold_request', 'sip_patron_enable_request', 'sip_patron_enable_response', 'sip_patron_information_request', 'sip_patron_information_response', 'sip_patron_status_request', 'sip_patron_status_response', 'sip_renew_request', 'sip_renew_response', 'sip_renew_all_request')
            #'optionalWith': ('sip_checkin_response /VERSION 2')

    },
    'AD': {
            'fieldName':        'patron password',
            'fieldID':          'AD',
            'fieldDescription': "variable-length field. If the ACS stores the patron password in its database then the SC will prompt the patron for their password (PIN) and it will be sent to the ACS in this field. If this feature is not used by the ACS in the library then the field should be zero length if it is required in the command, and can be omitted entirely if the field is optional in the command.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_checkout_request', 'sip_end_patron_session_request', 'sip_fee_paid_request', 'sip_hold_request VERSION 1', 'sip_patron_enable_request VERSION 1', 'sip_patron_information_request VERSION 1', 'sip_patron_status_request', 'sip_renew_request', 'sip_renew_all_request')
    },
    'PatronStatus': {
            'fieldName':        'patron status',
            'fieldID':          '',
            'fieldDescription': "14-char, fixed-length field. This field is described in the preliminary NISO standard Z39.70-199x. A Y in any position indicates that the condition is true. A blank (code $20) in this position means that this condition is not true. For example, the first position of this field corresponds to \"charge privileges denied\" and must therefore contain a code $20 if this patron’s privileges are authorized.\nPos Definition\n0   charge privileges denied\n1   renewal privileges denied\n2   recall privileges denied\n3   hold privileges denied\n4   card reported lost\n5   too many items charged\n6   too many items overdue\n7   too many renewals\n8   too many claims of items returned\n9   too many items lost\n10  excessive outstanding fines\n11  excessive outstanding fees\n12  recall overdue\n13  too many items billed",
            'fixedLength':      14,
            'values': (
                'charge privileges denied',             #0
                'renewal privileges denied',            #1
                'recall privileges denied',             #2
                'hold privileges denied',               #3
                'card reported lost',                   #4
                'too many items charged',               #5
                'too many items overdue',               #6
                'too many renewals',                    #7
                'too many claims of items returned',    #8
                'too many items lost',                  #9
                'excessive outstanding fines',          #10
                'excessive outstanding fees',           #11
                'recall overdue',                       #12
                'too many items billed'                 #13
            )
            #'minVersion': 1
            #'requiredBy': ('sip_patron_information_response', 'sip_patron_status_response')
            #'optionalWith': ()
    },
    'PaymentAccepted': {
            'fieldName':        'payment accepted',
            'fieldID':          '',
            'fieldDescription': "1-char, fixed-length field: Y or N. A Y indicates that the ACS has accepted the payment from the patron and the patron’s account will be adjusted accordingly.",
            'fixedLength':      1,
            'values': { 
                'Y': 'ACS accepted payment',
                'N': 'ACS refused payment'
            }
            #'minVersion': 2
            #'requiredBy': ('sip_fee_paid_response', 'sip_patron_enable_response VERSION 1')
            #'optionalWith': ()                        
    },
    'PaymentType': {
            'fieldName':        'payment type',
            'fieldID':          '',
            'fieldDescription': "2-char, fixed-length field (00 thru 99). An enumerated value for the type of payment, from the following table:\nVal Payment Type\n00  cash\n01  VISA\n02  credit card",
            'fixedLength':      2,
            'values': { 
                '00': 'cash',
                '01': 'VISA',
                '02': 'credit card',
            }
            #'minVersion': 2
            #'requiredBy': ('sip_fee_paid_request')
            #'optionalWith': ()
    },
    'AQ': {
            'fieldName':        'permanent location',
            'fieldID':          'AQ',
            'fieldDescription': "variable-length field. The location where an item is normally stored after being checked in.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 1
            #'requiredBy': ('sip_checkin_response')
            #'optionalWith': ('sip_item_information_response VERSION 2')
    },
    'AE': {
            'fieldName':        'personal name',
            'fieldID':          'AE',
            'fieldDescription': "variable-length field; the patron’s name.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 1
            #'requiredBy': ('sip_patron_enable_response', 'sip_patron_information_response', 'sip_patron_status_response')
            #'optionalWith': ()
    },
    'BS': {
            'fieldName':        'pickup location',
            'fieldID':          'BS',
            'fieldDescription': "variable-length field; the location where an item will be picked up.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_hold_request')
    },
    'AG': {
            'fieldName':        'print line',
            'fieldID':          'AG',
            'fieldDescription': "variable-length field. Print line fields provide a way for the ACS to print messages on the SC printer. They are never required. When used, there can be one or more of these fields, which are then printed on consecutive lines of the printer. If they are too long, then the trailing portion of the field will be left out.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 1
            #'requiredBy': ()
            #'optionalWith': ('sip_checkin_response', 'sip_checkout_response', 'sip_end_patron_session_response', 'sip_fee_paid_response', 'sip_item_information_response', 'sip_item_status_update_response', 'sip_patron_enable_response', 'sip_patron_information_response', 'sip_patron_status_response', 'sip_renew_response', 'sip_renew_all_response', 'sip_sc_status_response')
    },
    'ProtocolVersion': {
            'fieldName':        'protocol version',
            'fieldID':          '',
            'fieldDescription': "4-char, fixed-length field: x.xx. The protocol version field contains the version number of the protocol that the software is currently using. The format of the version number should be expressed as a single numeral followed by a period then followed by two more numerals.",
            'fixedLength':      4,
            'values': False
            #'minVersion': 1
            #'requiredBy': ('sip_sc_status_request', 'sip_sc_status_response')
            #'optionalWith': ()
    },
    'PwdAlgorithm': {
            'fieldName':        'PWD algorithm',
            'fieldID':          '',
            'fieldDescription': "1-char, fixed-length field. Specifies the algorithm, if any, used to encrypt the login password field of the Login Message. ‘0’ means the login password is not encrypted. The SC and the ACS must agree on an algorithm to use and must agree on the value to be used in this field to represent that algorithm.",
            'fixedLength':      1,
            'values': { 
                '0': 'Unencrypted password',
                '1': 'Encrypted password'
            }
            #'minVersion': 2
            #'requiredBy': ('sip_login_request')
            #'optionalWith': ()                    
    },
    'BR': {
            'fieldName':        'queue position',
            'fieldID':          'BR',
            'fieldDescription': "variable-length field. This field contains a numeric value for the patron’s position in the hold queue for an item.",
            'fixedLength':      False,
            'values': False
    },
    'CJ': {
            'fieldName':        'recall date',
            'fieldID':          'CJ',
            'fieldDescription': "18-char, fixed-length field: YYYYMMDDZZZZHHMMSS. The date that the recall was issued.",
            'fixedLength':      18,
            'values': False
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_item_information_response')
    },
    'BU': {
            'fieldName':        'recall items',
            'fieldID':          'BU',
            'fieldDescription': "variable-length field. This field should be sent for each recalled item.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_patron_information_response')
    },
    'RecallItemsCount': {
            'fieldName':        'recall items count',
            'fieldID':          '',
            'fieldDescription': "4-char fixed-length field. This field should contain a count of the items that the patron still has checked out that have been recalled, from 0000 to 9999. If this information is not available or unsupported this field should contain four blanks (code $20).",
            'fixedLength':      False,
            'values': False
            #'minVersion': 2
            #'requiredBy': ('sip_patron_information_response')
            #'optionalWith': ()
    },
    'RenewalOk': {
            'fieldName':        'renewal ok',
            'fieldID':          '',
            'fieldDescription': "1-char, fixed-length field: Y or N. This field is needed to inform the SC that the material is already checked out. A ‘Y’ value means that the item was checked out to the same patron, so it is actually being renewed. An ‘N’ value means that the patron did not already have the item checked out.",
            'fixedLength':      1,
            'values': { 
                'Y': 'Item can be renewed by patron',
                'N': 'Item can not be renewed by patron'
            }
            #'minVersion': 1
            #'requiredBy': ('sip_checkout_response')
            #'optionalWith': ()
    },
    'RenewedCount': {
            'fieldName':        'renewed count',
            'fieldID':          '',
            'fieldDescription': "4-char fixed-length field. A count of the number of items that were renewed.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 2
            #'requiredBy': ('sip_renew_all_response')
            #'optionalWith': ()
    },
    'BM': {
            'fieldName':        'renewed items',
            'fieldID':          'BM',
            'fieldDescription': "variable-length field. This field should be sent for each renewed item.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_renew_all_response')
    },
    'Resensitize': {
            'fieldName':        'resensitize',
            'fieldID':          '',
            'fieldDescription': "1-char, fixed-length field: Y or N. If the ACS checked in the article and it is appropriate to resensitize it, then this field should contain a 'Y'. If the article should not be resensitized, then this field should contain a 'N'. In this case an appropriate message could be sent in the screen message field.",
            'fixedLength':      1,
            'values': { 
                'Y': 'Resensitize item',
                'N': 'Don\'t resensitize item' #(for example, a closed reserve book, or the checkin was refused).
            }
            #'minVersion': 1
            #'requiredBy': ('sip_checkin_response')
            #'optionalWith': ()
    },
    'RetriesAllowed': {
            'fieldName':        'retries allowed',
            'fieldID':          '',
            'fieldDescription': "3-char, fixed-length field. Indicates the number of retries that are allowed for a specific transaction. 999 indicates that the retry number is unknown.",
            'fixedLength':      3,
            'values': False
            #'minVersion': 1
            #'requiredBy': ('sip_sc_status_response')
            #'optionalWith': ()                     
    },
    'ReturnDate': {
            'fieldName':        'return date',
            'fieldID':          '',
            'fieldDescription': "18-char, fixed-length field: YYYYMMDDZZZZHHMMSS. The date that an item was returned to the library, which is not necessarily the same date that the item was checked back in.",
            'fixedLength':      18,
            'values': False
            #'minVersion': 1
            #'requiredBy': ('sip_checkin_request')
            #'optionalWith': ()
    },
    'ScRenewalPolicy': {
            'fieldName':        'SC renewal policy',
            'fieldID':          '',
            'fieldDescription': "1-char, fixed-length field: Y or N. If this field contains a 'Y ' then the SC has been configured by the library staff to do renewals. ‘N’ means the SC has been configured to not do renewals. This field was called “renewals allowed” in Version 1.00 of the protocol.",
            'fixedLength':      1,
            'values': { 
                'Y': 'SC item renewal allowed',
                'N': 'SC item renewal denied'
            }
            #'minVersion': 1
            #'requiredBy': ('sip_checkout_request')
            #'optionalWith': ()
    },
    'AF': {
            'fieldName':        'screen message',
            'fieldID':          'AF',
            'fieldDescription': "variable-length field. Screen message fields provide a way for the ACS to display messages on the SC screen. They are never required. When used, there can be one or more of these fields, which are then displayed on consecutive lines of the screen. If they are too long, then the trailing portion of the field will be left out. The message can contain holds, fines, disabled card, library branch, or other information as provided by the ACS.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 1
            #'requiredBy': ()
            #'optionalWith': ('sip_checkin_response', 'sip_checkout_response', 'sip_end_patron_session_response', 'sip_fee_paid_response', 'sip_item_information_response', 'sip_item_status_update_response', 'sip_patron_enable_response', 'sip_patron_information_response', 'sip_patron_status_response', 'sip_renew_response', 'sip_renew_all_response', 'sip_sc_status_response')
    },
    'CI': {
            'fieldName':        'security inhibit',
            'fieldID':          'CI',
            'fieldDescription': "1-char, fixed-length field: Y or N. A 'Y' in this field will notify the SC to ignore the security status of the item.",
            'fixedLength':      1,
            'values': { 
                'Y': 'Ignore security status of item',
                'N': 'Honor security status of item'
            }
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_checkout_response', 'sip_renew_response')
    },
    'SecurityMarker': {
            'fieldName':        'security marker',
            'fieldID':          '',
            'fieldDescription': "2-char, fixed-length field (00 thru 99). Enumerated security marker type.\nVal Security Marker Type\n00  other\n01  None\n02  3M Tattle-Tape Security Strip\n03  3M Whisper Tape",
            'fixedLength':      2,
            'values': { 
                '00': 'other',
                '01': 'None',
                '02': '3M Tattle-Tape Security Strip',
                '03': '3M Whisper Tape',
            }
            #'minVersion': 2
            #'requiredBy': ('sip_item_information_response')
            #'optionalWith': ()
    },
    'AY': {
            'fieldName':        'sequence number',
            'fieldID':          'AY',
            'fieldDescription': "1-char, fixed-length field; sequence number for the message, used for error detection and synchronization when error detection is enabled.",
            'fixedLength':      1,
            'values': (1,2,3,4,5,6,7,8,9)
    },
    'CL': {
            'fieldName':        'sort bin',
            'fieldID':          'CL',
            'fieldDescription': "variable-length field. This field should contain a bin number that indicates how the items should be sorted. The maximum practical number of sort bins for a patron using 3M SelfCheck system is probably only 3 or 4, but many digits are allowed to accommodate some sort of fantastic sorting device using a hierarchical bin numbering scheme.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_checkin_response')
    },
    'BP': {
            'fieldName':        'start item',
            'fieldID':          'BP',
            'fieldDescription': "variable-length field. The number of the first item to be returned. The Patron Information message allows the SC to request the ACS to send a list of items that a patron has checked out, or that are overdue, etc. This field specifies the number in that list of the first item to be sent to the SC. For instance, if the SC had requested - via the summary, start item, and end item fields of the Patron Information message - to have the fifth through tenth items in the list of the patron’s overdue items sent in the Patron Information response, this field would have the value “5”. A numbering system that starts with 1 is assumed. This allows the requester to have control over how much data is returned at a time, and also to get the whole list in sequential or some other order using successive messages/responses.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_patron_information_request')
    },
    'StatusCode': {
            'fieldName':        'status code',
            'fieldID':          '',
            'fieldDescription': "1-char, fixed-length field: 0 or 1 or 2; the status of the SC unit.\nVal Definition\n0   SC unit is OK\n1   SC printer is out of paper\n2   SC is about to shut down",
            'fixedLength':      1,
            'values': { 
                '0': 'SC unit is OK',
                '1': 'SC printer is out of paper',
                '2': 'SC is about to shut down",',
            }
            #'minVersion': 1
            #'requiredBy': ('sip_sc_status_request')
            #'optionalWith': ()
    },
    'StatusUpdateOk': {
            'fieldName':        'status update ok',
            'fieldID':          '',
            'fieldDescription': "1-char, fixed-length field: Y or N. ACS policy for the SC. A Y indicates that patron status updating by the SC is allowed, e.g., a patron’s card status can be changed to blocked.",
            'fixedLength':      1,
            'values': { 
                'Y': 'SC can update patron status',
                'N': 'SC can not update patron status'
            }
            #'minVersion': 1
            #'requiredBy': ('sip_sc_status_response')
            #'optionalWith': ()                     
    },
    'Summary': {
            'fieldName':        'summary',
            'fieldID':          '',
            'fieldDescription': "10-char, fixed-length field. This allows the SC to request partial information only. This field usage is similar to the NISO defined PATRON STATUS field. A Y in any position indicates that detailed as well as summary information about the corresponding category of items can be sent in the response. A blank (code $20) in this position means that only summary information should be sent about the corresponding category of items. Only one category of items should be requested at a time, i.e. it would take 6 of these messages, each with a different position set to Y, to get all the detailed information about a patron’s items. All of the 6 (7) responses, however, would contain the summary information. See Patron Information Response.\n Pos Definition\n0   hold items\n1   overdue items\n2   charged items\n3   fine items\n4   recall items\n5   unavailable holds",
            'fixedLength':      10,
            'values': (
                'hold items',          #0
                'overdue items',       #1
                'charged items',       #2
                'fine item',           #3
                'recall items',        #4
                'unavailable holds',   #5
                'feeItems',            #6 (Gossip)
                'undefined',           #7
                'undefined',           #8
                'undefined',           #9
            )                       
#            'values': {
#                'none':             '          ',
#                'hold items':       'Y         ',   #0
#                'overdue items':    ' Y        ',   #1
#                'charged items':    '  Y       ',   #2
#                'fine item':        '   Y      ',   #3
#                'recall items':     '    Y     ',   #4
#                'unavailable holds':'     Y    ',   #5
#                'feeItems':         '      Y   ',   #6 (Gossip)
#                'undefined':        '       Y  ',   #7
#                'undefined':        '        Y ',   #8
#                'undefined':        '         Y',   #9
#            }                       
            #'minVersion': 2
            #'requiredBy': ('sip_patron_information_request')
            #'optionalWith': ()
    },
    'BX': {
            'fieldName':        'supported messages',
            'fieldID':          'BX',
            'fieldDescription': "variable-length field. This field is used to notify the SC about which messages the ACS supports. A Y in a position means that the associated message/response is supported. An N means the message/response pair is not supported.\nPos Message Command/Response pair\n0   Patron Status Request\n1   Checkout\n2   Checkin\n3   Block Patron\n4   SC/ACS Status\n5   Request SC/ACS Resend\n6   Login\n7   Patron Information\n8   End Patron Session\n9   Fee Paid\n10  Item Information\n11  Item Status Update\n12  Patron Enable\n13  Hold\n14  Renew\n15  Renew All",
            'fixedLength':      False,
            'values': (
                'Patron Status Request',    #0
                'Checkout',                 #1
                'Checkin',                  #2
                'Block Patron',             #3
                'SC/ACS Status',            #4
                'Request SC/ACS Resend',    #5
                'Login',                    #6
                'Patron Information',       #7
                'End Patron Session',       #8
                'Fee Paid',                 #9
                'Item Information',         #10
                'Item Status Update',       #11
                'Patron Enable',            #12
                'Hold',                     #13   
                'Renew',                    #14
                'Renew All'                 #15
            )
            #'minVersion': 2
            #'requiredBy': ('sip_sc_status_response')
            #'optionalWith': ()                     
    },
    'AN': {
            'fieldName':        'terminal location',
            'fieldID':          'AN',
            'fieldDescription': "variable-length field. The ACS could put the SC’s location in this field.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 1
            #'requiredBy': ()
            #'optionalWith': ('sip_sc_status_response')                     
    },
    'AC': {
            'fieldName':        'terminal password',
            'fieldID':          'AC',
            'fieldDescription': "variable-length field. This is the password for the SC unit. If this feature is not used by the ACS in the library then the field should be zero length if it is required in the command, and can be omitted entirely if the field is optional in the command.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 1
            #'requiredBy': ('sip_block_patron_request', 'sip_checkin_request', 'sip_checkout_request')
            #'optionalWith': ('sip_end_patron_session_request', 'sip_fee_paid_request', 'sip_hold_request', 'sip_item_information_request', 'sip_item_status_update_request', 'sip_patron_enable_request', 'sip_patron_information_request', 'sip_patron_status_request', 'sip_renew_request', 'sip_renew_all_request')
    },                    
    'ThirdPartyAllowed': {
            'fieldName':        'third party allowed',
            'fieldID':          '',
            'fieldDescription': "1-char, fixed-length field: Y or N. If this field contains an 'N ' then the ACS should not allow third party renewals. This allows the library staff to prevent third party renewals from this terminal.",
            'fixedLength':      1,
            'values': { 
                'Y': 'Third party renewals allowed',
                'N': 'Third party renewals denied'
            }
            #'minVersion': 2
            #'requiredBy': ('sip_renew_request')
            #'optionalWith': ()                          
    },
    'TimeoutPeriod': {
            'fieldName':        'timeout period',
            'fieldID':          '',
            'fieldDescription': "3-char, fixed-length field. This timeout period until a transaction is aborted should be a number expressed in tenths of a second. 000 indicates that the ACS is not on-line. 999 indicates that the time-out is unknown.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 1
            #'requiredBy': ('sip_sc_status_response')
            #'optionalWith': ()                     
    },
    'AJ': {
            'fieldName':        'title identifier',
            'fieldID':          'AJ',
            'fieldDescription': "variable-length field. Identifies a title; could be a bibliographic number or a title string.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 1
            #'requiredBy': ('sip_checkout_response', 'sip_item_information_response', 'sip_renew_response')
            #'optionalWith': ('sip_checkin_response', 'sip_hold_request', 'sip_item_status_update_response', 'sip_renew_request')
    },
    'TransactionDate': {
            'fieldName':        'transaction date',
            'fieldID':          '',
            'fieldDescription': "18-char, fixed-length field: YYYYMMDDZZZZHHMMSS. All dates and times are expressed according to the ANSI standard X3.30 for date and X3.43 for time. The ZZZZ field should contain blanks (code $20) to represent local time. To represent universal time, a Z character (code $5A) should be put in the last (right hand) position of the ZZZZ field. To represent other time zones the appropriate character should be used; a Q character (code $51) should be put in the last (right hand) position of the ZZZZ field to represent Atlantic Standard Time. When possible local time is the preferred format.",
            'fixedLength':      18,
            'values': False
            #'minVersion': 1
            #'requiredBy': ('sip_block_patron_request', 'sip_checkin_request', 'sip_checkin_response', 'sip_checkout_request', 'sip_checkout_response', 'sip_end_patron_session_request', 'sip_end_patron_session_response', 'sip_fee_paid_request', 'sip_fee_paid_response', 'sip_hold_request', 'sip_item_information_request', 'sip_item_information_response', 'sip_item_status_update_request', 'sip_item_status_update_response', 'sip_patron_enable_request', 'sip_patron_enable_response', 'sip_patron_information_request', 'sip_patron_information_response', 'sip_patron_status_request', 'sip_patron_status_response', 'sip_renew_request', 'sip_renew_response', 'sip_renew_all_request', 'sip_renew_all_response')
            #'optionalWith': ()
    },
    'BK': {
            'fieldName':        'transaction id',
            'fieldID':          'BK',
            'fieldDescription': "variable-length field. This field should contain a transaction id that is assigned by the ACS or by a payment device, for auditing purposes to track cash flow.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_checkout_response', 'sip_fee_paid_request', 'sip_fee_paid_response', 'sip_renew_response')
    },
    'UidAlgorithm': {
            'fieldName':        'UID algorithm',
            'fieldID':          '',
            'fieldDescription': "1-char, fixed-length field. Specifies the algorithm, if any, used to encrypt the login user id field of the Login Message. ‘0’ means the login user id is not encrypted. The SC and the ACS must agree on an algorithm to use and must agree on the value to be used in this field to represent that algorithm. Few, if any, systems will want to encrypt the user id.",
            'fixedLength':      1,
            'values': { 
                '0': 'Unencrypted user id',
                '1': 'Encrypted user id'
            }
            #'minVersion': 2
            #'requiredBy': ('sip_login_request')
            #'optionalWith': ()                    
    },
    'UnavailableHoldsCount': {
            'fieldName':        'unavailable holds count',
            'fieldID':          '',
            'fieldDescription': "4-char fixed-length field. This field should contain the number of unavailable holds for this patron, from 0000 to 9999. If this information is not available or unsupported this field should contain four blanks (code $20).",
            'fixedLength':      4,
            'values': False
            #'minVersion': 2
            #'requiredBy': ('sip_patron_information_response')
            #'optionalWith': ()
    },
    'CD': {
            'fieldName':        'unavailable hold items',
            'fieldID':          'CD',
            'fieldDescription': "variable-length field. This field should be sent for each unavailable hold.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_patron_information_response')
    },
    'UnrenewedCount': {
            'fieldName':        'unrenewed count',
            'fieldID':          '',
            'fieldDescription': "4-char fixed-length field; a count of the number of items that were not renewed.",
            'fixedLength':      4,
            'values': False
            #'minVersion': 2
            #'requiredBy': ('sip_renew_all_response')
            #'optionalWith': ()
    },
    'BN': {
            'fieldName':        'unrenewed items',
            'fieldID':          'BN',
            'fieldDescription': "variable-length field. This field should be sent for each unrenewed item. It could include a reason that the item was not renewed.",
            'fixedLength':      False,
            'values': False
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_renew_all_response')
    },
    'BL': {
            'fieldName':        'valid patron',
            'fieldID':          'BL',
            'fieldDescription': "1-char field: Y or N. A Y in this field is used to indicate that the patron bar-code is valid, is on the database. An N indicates that the patron is not a valid patron.",
            'fixedLength':      1,
            'values': { 
                'Y': 'Patron id is valid',
                'N': 'Patron id is invalid',
            }
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_patron_enable_response', 'sip_patron_information_response', 'sip_patron_information_response', 'sip_patron_status_response')
    },
    'CQ': {
            'fieldName':        'valid patron password',
            'fieldID':          'CQ',
            'fieldDescription': "1-char field: Y or N. A Y in this field is used to indicate that the patron password is valid. An N indicates that the patron password is not valid.",
            'fixedLength':      1,
            'values': { 
                'Y': 'Patron password is valid',
                'N': 'Patron password is invalid',
            }
            #'minVersion': 2
            #'requiredBy': ()
            #'optionalWith': ('sip_patron_enable_response', 'sip_patron_information_response', 'sip_patron_status_response')
    },
}




"""
messageIdentifiers = {'fixed': {
                          'Ok':              response[2:3], 
                          'Resensitize':     response[3:4], 
                          'Magnetic':        response[4:5], 
                          'Alert':           response[5:6],
                          'TransactionDate': response[6:6+18]
                          },
                'variable': self._response_parse_varData(response, 24)
              }
"""
