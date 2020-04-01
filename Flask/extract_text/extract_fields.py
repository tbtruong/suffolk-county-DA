import re
import os
import extract_text


# criminal complaint
def find_docket_number(document):
    docket = re.search("[0-9]{4}[A-Z]{2}[0-9]{6}", document)
    if (docket != None):
        return docket.group()
    return "Docket number not found"


def find_full_name(document):
    name = re.search("[A-Z][a-z]*\s[A-Z]\s[A-Z][a-z]*", document)
    if (name != None):
        return name.group()
    return "Name not found"


def find_dates(document):
    dates = re.findall("[0-9]{2}/[0-9]{2}/[0-9]{4}", document)
    if (dates != None):
        return dates
    return "No dates found"


def find_obtn(document):
    obtn = re.search("[A-Z]{4}[0-9]{9}", document)
    if (obtn != None):
        return obtn.group()
    return "obtn not found"


def find_indicent_report(document):
    irn = re.search("[0-9]{3}\s[0-9]{3}\s[0-9]{3}", document)
    if (irn != None):
        return irn.group()
    return "Police Incident report number not found"


def find_addresses(document):
    street = re.findall('[0-9][0-9]*\s[A-Z][a-z]*\s[A-Z][a-z]+', document)
    city_state = re.findall('[A-Z][a-z]+[,]\s[A-Z]{2}\s[0-9]{5}', document)
    if len(street) == 2 and len(city_state) == 2:
        return {'court': street[1] + ' ' + city_state[1], 'defendant': street[0] + ' ' + city_state[0]}
    return {'court': 'Not found', 'defendant': 'Not found'}


def find_codes(document):
    codes = re.findall('[1-9][0-9]+(/[0-9][0-9][A-Z]*)?(/[A-Z]+)?', document)
    codes = re.findall('[1-9][0-9]*/[0-9]+[A-Z]*(/[0-9]*[A-Z]*)?',document)
    return codes


# data extracted from arrest booking form by finding the key words for the fields and adding the corresponding key, value pair to dictionary
def arrest_booking_form(raw_document):
    #print("We are in Extract_Fields")
    header = ['Boston Police Department', 'Arrest Booking Form']
    document = raw_document
    for phrase in header:
        document = document.replace(phrase, '')
    #weird bug? Why is this changing to PPAddress
    document = document.replace("Address", "Personal Address")
    #print(document)
    # list of keywords
    #First address is simply "Address" on form, changed for ease of use/code
    block_list = ["Report Date", "Booking Status", "Printed By", "District", "UCR Code", "OBTN", "Court of Appearance",
                  "Master Name", "Age", "Location of Arrest",
                  "Booking Name", "Alias", "Personal Address", "Charges", "Booking #", "Incident #", "CR Number", "Booking Date",
                  "Arrest Date", "RA Number", "Sex", "Height", "Occupation",
                  "Race", "Weight", "Employer/School", "Date of Birth", "Build", "Emp/School Addr", "Place of Birth",
                  "Eyes Color", "Social Sec. Number", "Marital Status",
                  "Hair Color", "Operators License", "Mother's Name", "Complexion", "State", "Father's Name",
                  "Phone Used", "Scars/Marks/Tattoos", "Examined at Hospital",
                  "Clothing Desc", "Breathalyzer Used", "Examined by EMS", "Arresting Officer", "Cell Number",
                  "Booking Officer", "Partner's #", "Informed of Rights", "Unit #",
                  "Placed in Cell By", "Trans Unit #", "Searched By", "Cautions", "Booking Comments", "Visible Injuries",
                  "Person Notified", "Relationship", "Phone", "Address",
                  "Juv. Prob. Officer", "Notified By", "Notified Date/Time", "Bail Set By", "I Selected the Bail Comm.",
                  "Bailed By", "Amount", "BOP Check",
                  "Suicide Check", "BOP Warrant", "BOP Court"]

    #block_list = ["Report Date", "Booking Status"]
    #Unit # before Trans Unit #, problematic
    #Need special case for line Cautions: Booking Comments: Visible Injuries:
    #BOP Court picking up Signature when it shouldn't
    fields = {}
    for counter in range(len(block_list)):
        field = block_list[counter]
        find = field + ': '
        value = ''
        if find in document:
            temp_doc = document[document.index(find) + len(find):]
            if counter < len(block_list)-1:
                # temporarily erase keywords and use the index of : to know when to end the string
                #for word in block_list:
                word = block_list[counter+1]
                #temp_doc = temp_doc.replace(word, '', 1)
                value = temp_doc[:temp_doc.index(word)].replace('\n', '').strip()
            else:
                # if no : in the remaining document, end current field with next space or newline
                value = temp_doc[:re.search('\s|\n', temp_doc).start()]
        fields[field] = value
    return fields


# application for criminal complaint
def find_name_ACC(document):
    name = re.search("[a-z]*\s[A-Z][a-z]*[,]\s[A-Z][a-z]*", document)
    return name

def application_for_criminal_complaint(raw_document):
    #Remove Headers
    header = ['Application Details', 'Accused Details', 'Complainant Details']
    document = raw_document
    for phrase in header:
        document = document.replace(phrase, '')
    block_list = ["Summons", "Hearing Requested", "Court", "Arrest Status of Accused", "Arrest Date", "In Custody", "Officer ID No.",
                  "Agency", "Type", "Name", "Birth Surname", "Address", "Date of Birth", "Place of Birth", "Social Security No.",
                  "PCF No.", "SID", "Marital Status", "Driver's License No.", "Driver's License State", "Driver's License Exp. Year",
                  "Gender", "Race", "Height", "Weight", "Eyes", "Hair", "Ethnicity", "Primary Language", "Complexion",
                  "Scars/Marks/Tattoos", "Employer Name", "School Name", "Day Phone", "Mother Name", "Mother Maiden Name",
                  "Father Name", "Complainant Type", "Police Dept."]
    #Name getting replaced with empty string before other fields, problematic
    fields = {}
    for counter in range(len(block_list)):
        field = block_list[counter]
        find = field + ': '
        value = ''
        if find in document:
            temp_doc = document[document.index(find) + len(find):]
            if ':' in temp_doc:
                #Must have space after colon in order to work properly
                # temporarily erase keywords and use the index of : to know when to end the string
                word = block_list[counter + 1]
                # temp_doc = temp_doc.replace(word, '', 1)
                value = temp_doc[:temp_doc.index(word)].replace('\n', '').strip()
            else:
                # if no : in the remaining document, end current field with next space or newline
                value = temp_doc[:re.search('\n', temp_doc).start()]
        fields[field] = value
    return fields