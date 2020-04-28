import sys
sys.path.append('/Users/eloisanitorreda/suffolk-county-DA/Flask/')
import os #allows interaction with operating system and pathing files
import json #allows python dictionaries to be formatted into JSON and vice versa JSON to string
from bson import ObjectId #allows MongoDB to format data
from werkzeug.utils import secure_filename #secure file name given file name
from PIL import Image #package that allows you to give functionality to images
from SCDA import config
from .extract_text.extract_fields import *
from .extract_text.extract_text import *
from SCDA import app, models, db
from flask import request, flash, redirect, render_template
from .extract_routes.database_code import *
from datetime import datetime





#allowed_file adapted from http://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'json'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


#http://www.programmersought.com/article/68322218798/
class JSONEncoder(json.JSONEncoder):
    def default(self, o):                # pylint: disable=E0202 
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"
@app.route('/upload', methods=['POST'])
def upload_forms():
    if request.method == 'POST':
        print(request.data)
        form_data = request.get_json()
        if 'acc' not in form_data:
            return "Please upload all required document(s): missing ACC"
        else:
            acc_file = form_data['acc']
            acc_filename = acc_file.split('/')
            acc_filename = acc_filename[-1]
            # Replace with better security
            if allowed_file(acc_filename):
                form_upload_date = datetime.now()
                filename = secure_filename(acc_filename)
                file = Image.open(acc_file)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image = ImageReader(image_path)
                text = ExtractText(image.image)
                #does not work well with provided test image
                #doc = text.extract_text()
                doc = open(os.path.expanduser("~/suffolk-county-DA/Flask/SCDA/extract_text/extraction_tests/test_textdumps/Application for Criminal Complaint .txt")).read()
                acc_info = application_for_criminal_complaint(doc)
                #print(acc_info)
                if acc_info["Name"] == '' or acc_info["Date of Birth"] == '' or acc_info["Social Security No."] == '':
                    return "Application for criminal complaint could not be read. Please upload a clearer image."
                else:
                    uuid = getUser(acc_info["Name"], acc_info["Social Security No."][-4:], acc_info["Date of Birth"])
                    #print(uuid)
                    
                    # store path or actual image?
                    acc_insert = models.ACC(uuid, form_upload_date, image_path, acc_info["Summons"], acc_info["Hearing Requested"], acc_info["Court"], acc_info["Arrest Status of Accused"], acc_info["Arrest Date"], acc_info["In Custody"],acc_info["Officer ID No."],acc_info["Agency"],acc_info["Type"],acc_info["Name"],acc_info["Birth Surname"],acc_info["Address"],acc_info["Date of Birth"], acc_info["Place of Birth"], acc_info["Social Security No."], acc_info["PCF No."],acc_info["SID"],acc_info["Marital Status"],acc_info["Driver's License No."],acc_info["Driver's License State"],acc_info["Driver's License Exp. Year"],acc_info["Gender"],acc_info["Race"],acc_info["Height"],acc_info["Weight"],acc_info["Eyes"],acc_info["Hair"],acc_info["Ethnicity"],acc_info["Primary Language"],acc_info["Complexion"],acc_info["Scars/Marks/Tattoos"],acc_info["Employer Name"],acc_info["School Name"],acc_info["Day Phone"],acc_info["Mother Name"],acc_info["Mother Maiden Name"],acc_info["Father Name"],acc_info["Complainant Type"],acc_info["Police Dept."])
                    db.session.add(acc_insert)
                    #REMINDER: MUST HAVE FORMS TABLE BEFORE COMMITTING
                    #db.session.commit()
            else:
                return redirect('failure')
            return "All good!"
    #recieve the json object and possibily convert it


    #the upload should be in json format by this point, see format in database code.py 
    #also at this point, the json should hold a key called forms which contains a list of objects where each object is keyed by their form title
    #extract forms such that there is a variable call it forms that is equal to the list of objects
    #Go through the list and find ACC which is required.
        #If ACC is in the list
                #Constiutents table
                    #User = add_acc(RAW_ACC_Document), at this point we get the UUID
                    #GetUser(Name,DOB,SSN), this getUser should return the unique id number
                        #If GetUser returns no user found, else call AddUser which also returns the newly made uuid number
                    #Set a variable User = GetUser() 
                #At this point, we have a user we want to add our forms to.
                #At this point we are finished with the constituents table
    #At this point, Constituents table is properly filled out
                #Forms Table
                    #Given their UUID
                    #Get the FormUploadDate = getDate()
                    #Call addFormRow(UUID,FormUploadDate, List Variable Forms)
                        #this should add a new row with consitutuent UUID, Form upload date, all the forms in list set to upload date. 
                        #this function should return a reference to the new row in the forms table so that we can add the actual forms later
                    #Set variable formRow = addFormRow()
    #At this point, Forms Table is properly filled out.
    #Six if in conditions, but if ACC pass, example https://stackoverflow.com/questions/9371114/check-if-list-of-objects-contain-an-object-with-a-certain-attribute-value. 
                #Individual Document Tables 
                    #Example: Do this for all 6 forms,
                    #Route ACC Table
                        #Call addACCForm(ACC Image)
                            #The ultimate goal of this function is to add a row to their respective tables in the Postgres database. 
                            #This should return success or failure depending if the form was successfully extracted and tested

                

        #If ACC is not in list, send error "Please upload all required document(s): missing ACC"
    pass


#route for criminal complaints
@app.route('/CC', methods=['POST'])
def Criminal_Complaint_Post():
    print("RECIEVING REQUEST 1")
    if request.method == 'POST':
        #print(request)
        #print(request.form)
        #print(request.headers)
        print(request.files)
        print(request.data)
        if 'file' not in request.files:
            flash('No file part')
            print('file not in request.files')
            print('REDIRECT LINK')
            return redirect('/failure')
        file = request.files['file']
        #print(file)
        if file.filename == '':
            flash('/failure')
            print('no file name')
            print('HIT REDIRECT LINK 2')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            print("RECIEVING IMAGE")
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))     
            test_image = ImageReader(os.path.join(app.config['UPLOAD_FOLDER'], filename)) #this allows you to see image
            
            #images come in oriented wrong, so the following code rotates it the correct way
            image = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image = image.transpose(Image.ROTATE_270)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'],'file_rotated.png'))
            final_image = ImageReader(os.path.join(app.config['UPLOAD_FOLDER'],'file_rotated.png'))

            text = ExtractText(final_image.image)
            doc = text.extract_text()
            #print(doc)
            docket_num = find_docket_number(doc)
            subject_name = find_full_name(doc)
            dates = find_dates(doc)
            #the following date variables assume all dates were recorded properly by the scan -- need to fix that assumption
            if(0<len(dates)):
                date_of_birth = dates[0]
            else:
                date_of_birth = 'Not found'
            #date of issued complaint
            if(1<len(dates)):
                complaint_issued = dates[1]
            else:
                complaint_issued = 'Not found'
            #date of offense
            if(2<len(dates)):
                doo = dates[2]
            else:
                doo = 'Not found'
            if(3<len(dates)):
                arrest_date = dates[3]
            else:
                arrest_date = 'Not found'
            if(4<len(dates)):
                next_event_date = dates[4]
            else:
                next_event_date = 'Not found'
            #obtn number
            obtn = find_obtn(doc)
            #address
            address = find_addresses(doc)
            offense_codes = find_codes(doc)
            #incident report number
            irn = str(find_indicent_report(doc))
            print("docket:", docket_num)
            print("name:", subject_name)
            print("obtn:", obtn)
            print("dob:", date_of_birth)
            print("doc:", complaint_issued)
            print("doo:",doo)
            print("doa:", arrest_date)
            print("irn:", irn)
            print("court address:", address['court'])
            print('defendant address:', address['defendant'])
            print('offense codes:', str(offense_codes))
            fields = {'_id': docket_num,'docket': docket_num, 'name': subject_name, 'dob': date_of_birth,'doc':complaint_issued,'doo':doo, 'doa':arrest_date, 'obtn': obtn, 'text': doc, 'irn': irn,
            'court_address':address['court'], 'defendant_address':address['defendant'], 'offense_codes':offense_codes}
            #save the image
            img_filename = os.path.join(app.config['UPLOAD_FINAL'], 'CC', fields['docket']+'_CC.jpg')
            image = image.transpose(Image.ROTATE_90)
            image.save(img_filename)
            fields['img'] = img_filename
            fields_package = json.dumps(fields)
            #print(fields_package)            
            #Input into database
            #Check if there is an existing record, if so just update. 
            #If no such records exist, create an entry.
            #set unique case incident report number, and obtn to the scanned values and embed all scanned fields into new document under the case with this docket #
        
            #create a new db document if one does not already exist
            return fields_package
        else:
            print('File not valid')
            print('HIT REDIRECT 3')
            return redirect('failure')
    return 'Please send a post request with your document picture'

#route for criminal complaint confirmation
@app.route('/confirm_CC', methods=['POST'])
def confirm_CC():
    if request.method == 'POST':
        data = request.form['data']
        print(data)
        img = request.files['image']
        json_name = 'data'
        img_name = secure_filename(img.filename)
        data.save(os.path.join(app.config['UPLOAD_JSON'],json_name))
        with open(os.path.join(app.config['UPLOAD_JSON'], json_name)) as f:
            fields = json.loads(f.read())
            img_filename = os.path.join(app.config['UPLOAD_FINAL'], 'CC', fields['docket']+'_CC.jpg')
            #set unique case incident report number, and obtn to the scanned values and embed all scanned fields into new document under the case with this docket #
            fields['image'] = img_filename
            img.save(img_filename)
            cases.update_one({'docket':fields['docket']},{'$set':{'irn':fields['irn'],'obtn':fields['obtn'],'CC':fields}}, upsert=True)
        os.remove(os.path.join(app.config['UPLOAD_JSON'],json_name))
        #fields = json.loads(data)
        #img_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'CC', fields['docket']+'_CC.jpg')
        #set unique case incident report number, and obtn to the scanned values and embed all scanned fields into new document under the case with this docket #
        #fields['image'] = img_filename
        #img.save(img_filename)
        #cases.update_one({'docket':fields['docket']},{'$set':{'irn':fields['irn'],'obtn':fields['obtn'],'CC':fields}}, upsert=True)
        return json.dumps({'status':'success'})



@app.route('/ABF', methods=['POST'])
def abf():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            print('file not in request.files')
            return redirect('/failure')
        file = request.files['file']
        if file.filename == '':
            flash('/failure')
            print('no file name')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            test_image = ImageReader(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #images come in oriented wrong, so the following code rotates it the correct way
            image = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image = image.transpose(Image.ROTATE_270)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'],'file_rotated.png'))
            final_image = ImageReader(os.path.join(app.config['UPLOAD_FOLDER'],'file_rotated.png'))
            text = ExtractText(final_image.image)
            doc = text.extract_text()
            data = arrest_booking_form(doc)
            print(data)
            cases.update_one({'obtn':data['OBTN']}, { "$set": {'abf':data}}, upsert=True)
            return json.dumps(data)
        else:
            print('File not valid')
            return redirect('failure')
    return 'Please send a post request with your document picture'
#route for application for criminal complaints
@app.route('/ACC', methods=['POST'])
def acc():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            print('file not in request.files')
            return redirect('/failure')
        file = request.files['file']
        #print(file)        
        if file.filename == '':
            flash('/failure')
            print('no file name')
            return redirect(request.url)        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            test_image = ImageReader(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            text = ExtractText(test_image.image)
            doc = text.extract_text()
            #docket number sent in the posted form since it is not on the document itself
            docket_num = request.form.get('docket')
            subject_name = find_name_ACC(doc)
            print(subject_name)
            dates = find_dates(doc)
            #the following date variables assume all dates were recorded properly by the scan -- need to fix that assumption
            #date_of_birth = dates[0]
            print("docket:", docket_num)
            print("name:", subject_name)
            #print("dob:", date_of_birth)
            fields = {'_id': docket_num,'docket': docket_num, 'name': subject_name, 'text': doc}
            fields_package = json.dumps(fields)
            #check if there is an already existing record, and simply update with the new info
            cases.update_one({'docket':docket_num}, { "$set": {'name': subject_name, 'text':doc}}, upsert=True)
            #create a new db document if one does not already exist
            return fields_package
        else:
            print('File not valid')
            return redirect('failure')
    return 'Please send a post request with your document picture'

@app.route('/dockets', methods=['GET'])
def dockets():
    case_list = cases.find({})
    dockets = []
    for case in case_list:
        print(case)
        dockets.append(case['docket'])
    return json.dumps({'dockets': dockets})

#returns a 'master json' which contains all cases keyed by docket number and within each case has all documents
@app.route('/master')
def get_master():
    master_list = list(cases.find({}))
    case_list = {}
    for case in master_list:
        case_list[case['docket']] = case
    return JSONEncoder().encode(case_list)

#web page to display all documents
@app.route('/all_cases')
def case_page():
    master_list = list(cases.find({}))
    case_list = {}
    for case in master_list:
        case_list[case['docket']] = case
    return render_template('case_page.html',case_list=case_list)

#web page to display documents for a specific case
@app.route('/<docket_number>')
def display_doc(docket_number):
    docket = docket_number 
    document = dict(cases.find_one({'docket':docket}))
    return render_template('display_doc.html',document=document,docket=docket)
    


@app.route('/success')
def uploaded():
    return 'File successfully uploaded'

@app.route('/failure')
def fail():
    return 'File not uploaded successfully'

if __name__ == '__main__':
    #app.run(host='0.0.0.0', ssl_context=('/home/eric/cert.pem', '/home/eric/key.pem'))
    app.run(host='0.0.0.0')