import datetime
import qrcode
import urllib
import requests
import json
from bottle import Bottle, run, route, request, response, static_file, template, redirect
import util
from util import settings

app = Bottle()

@app.route('/')
def index():
    mbox = request.cookies.account
    name = request.cookies.name
    if mbox and name:
        return redirect('/home')
    return redirect('/register')

@app.route('/home')
def home():
    mbox = request.cookies.account
    name = request.cookies.name
    if not (mbox and name):
        return redirect('/register')
    return template('returning', mbox=mbox, name=name, pages=util.get_existing_pages())

@app.route('/home', method='POST')
def home():
    mbox = request.forms.get('mbox')
    name = request.forms.get('name')
    response.set_cookie('account', mbox)
    response.set_cookie('name', name)
    return template('returning', mbox=mbox, name=name, pages=util.get_existing_pages())    

@app.route('/register')
def register():
    mbox = request.cookies.account
    name = request.cookies.name
    if mbox and name:
        return redirect('/home')    
    return template('register')

@app.route('/signout')
def signout():
    acc_cookie = request.cookies.get('account', None)
    name_cookie = request.cookies.get('name', None)
    if acc_cookie:
        response.set_cookie('account', '', expires=datetime.datetime.now())
    if name_cookie:
        response.set_cookie('name', '', expires=datetime.datetime.now())
    redirect('/register') 

@app.route('/static/<filename>')
def server_static(filename):
    if not request.cookies.get('account') or not request.cookies.get('name'):
            redirect('/register')    
    return static_file(filename, root='./static')

@app.route('/info/<partname>')
def get_info(partname):
    if not request.cookies.get('account') or not request.cookies.get('name'):
            redirect('/register')

    actor = 'mailto:' + request.cookies.get('account')
    actor_name = request.cookies.get('name')
    display_name = urllib.unquote_plus(partname)

    data = {
            'actor': {'mbox': actor, 'name': actor_name},
            'verb': {'id': 'http://adlnet.gov/expapi/verbs/visited', 'display':{'en-US': 'visited'}},
            'object':{'id': settings.INFO_DOMAIN + '/info/' + partname,
                'definition':{'name':{'en-US':display_name + ' info page'}}}
            }
    post_resp = requests.post(settings.LRS_STATEMENT_ENDPOINT, data=json.dumps(data), headers=settings.HEADERS, verify=False)
    return template(partname + '_info')

@app.route('/instructions/<partname>')
def get_instructions(partname):
    if not request.cookies.get('account') or not request.cookies.get('name'):
            redirect('/register')

    actor = 'mailto:' + request.cookies.get('account')
    actor_name = request.cookies.get('name')        
    display_name = urllib.unquote_plus(partname)

    data = {
            'actor': {'mbox': actor, 'name': actor_name},
            'verb': {'id': 'http://adlnet.gov/expapi/verbs/visited', 'display':{'en-US': 'visited'}},
            'object':{'id': settings.INFO_DOMAIN + '/instructions/' + partname,
                'definition':{'name':{'en-US':display_name + ' instructions page'}}}
            }
    post_resp = requests.post(settings.LRS_STATEMENT_ENDPOINT, data=json.dumps(data), headers=settings.HEADERS, verify=False)
    return template(partname + '_instructions')

@app.route('/quiz/<partname>')
def get_quiz(partname):
    if not request.cookies.get('account') or not request.cookies.get('name'):
            redirect('/register')
    return template(partname + '_questions', partname=urllib.unquote_plus(partname))

@app.route('/quiz/<partname>', method='POST')
def get_quiz(partname):
    if not request.cookies.get('account') or not request.cookies.get('name'):
            redirect('/register')

    answer1 = request.forms.get('answer1')
    answer2 = request.forms.get('answer2')
    answer3 = request.forms.get('answer3')
    answer4 = request.forms.get('answer4')
    answer5 = request.forms.get('answer5')

    type1 = request.forms.get('type1')
    type2 = request.forms.get('type2')
    type3 = request.forms.get('type3')
    type4 = request.forms.get('type4')
    type5 = request.forms.get('type5')

    response1 = request.forms.get('question1')
    response2 = request.forms.get('question2')
    response3 = request.forms.get('question3')
    response4 = request.forms.get('question4')
    response5 = request.forms.get('question5')

    actor = 'mailto:' + request.cookies.get('account')
    actor_name = request.cookies.get('name')
    quiz_name = 'activity:qr_demo_%s_quiz' % partname
    display_name = urllib.unquote_plus(partname) + ' quiz'
    
    data = [
            {
                'actor': {'mbox': actor, 'name': actor_name},
                'verb': {'id': 'http://adlnet.gov/expapi/verbs/attempted', 'display':{'en-US': 'attempted'}},
                'object':{'id':quiz_name,
                    'definition':{'name':{'en-US':display_name}}}
            }
        ]

    resp1 = {
        'actor': {'mbox': actor, 'name': actor_name},
        'verb': {'id': 'http://adlnet.gov/expapi/verbs/answered', 'display':{'en-US': 'answered'}},
        'object':{'id':quiz_name + '_question1', 'definition':{'name':{'en-US':display_name + ' question1'}}}, 
        'context':{'contextActivities':{'parent':[{'id': quiz_name}]}},
        'result':{'success': True, 'response': response1,'extensions': {'answer:correct_answer': answer1}}
        }
    resp2 = {
        'actor': {'mbox': actor, 'name': actor_name},
        'verb': {'id': 'http://adlnet.gov/expapi/verbs/answered', 'display':{'en-US': 'answered'}},
        'object':{'id':quiz_name + '_question2', 'definition':{'name':{'en-US':display_name + ' question2'}}},
        'context':{'contextActivities':{'parent':[{'id': quiz_name}]}},
        'result':{'success': True, 'response': response2,'extensions': {'answer:correct_answer': answer2}}
        }
    resp3 = {
        'actor': {'mbox': actor, 'name': actor_name},
        'verb': {'id': 'http://adlnet.gov/expapi/verbs/answered', 'display':{'en-US': 'answered'}},
        'object':{'id':quiz_name + '_question3', 'definition':{'name':{'en-US':display_name + ' question3'}}},
        'context':{'contextActivities':{'parent':[{'id': quiz_name}]}},
        'result':{'success': True, 'response': response3,'extensions': {'answer:correct_answer': answer3}}
        }
    resp4 = {
        'actor': {'mbox': actor, 'name': actor_name},
        'verb': {'id': 'http://adlnet.gov/expapi/verbs/answered', 'display':{'en-US': 'answered'}},
        'object':{'id':quiz_name + '_question4', 'definition':{'name':{'en-US':display_name + ' question4'}}},
        'context':{'contextActivities':{'parent':[{'id': quiz_name}]}},
        'result':{'success': True, 'response': response4,'extensions': {'answer:correct_answer': answer4}}
        }
    resp5 = {
        'actor': {'mbox': actor, 'name': actor_name},
        'verb': {'id': 'http://adlnet.gov/expapi/verbs/answered', 'display':{'en-US': 'answered'}},
        'object':{'id':quiz_name + '_question5', 'definition':{'name':{'en-US':display_name + ' question5'}}},
        'context':{'contextActivities':{'parent':[{'id': quiz_name}]}},
        'result':{'success': True, 'response': response5,'extensions': {'answer:correct_answer': answer5}}
        }
    
    wrong = 0
    if type1 != 'short answer':
            if answer1 != response1:
                    resp1['result']['success'] = False
                    wrong += 1
    else:
            if not set(answer1.split(',')).issubset([str(i).lower().strip() for i in response1.split(",")]):
                    resp1['result']['success'] = False
                    wrong += 1                        
    data.append(resp1)
    
    if type2 != 'short answer':
            if answer2 != response2:
                    resp2['result']['success'] = False
                    wrong += 1
    else:
            if not set(answer2.split(',')).issubset([str(i).lower().strip() for i in response2.split(",")]):
                    resp2['result']['success'] = False
                    wrong += 1                        
    data.append(resp2)
    
    if type3 != 'short answer':
            if answer3 != response3:
                    resp3['result']['success'] = False
                    wrong += 1
    else:
            if not set(answer3.split(',')).issubset([str(i).lower().strip() for i in response3.split(",")]):
                    resp3['result']['success'] = False
                    wrong += 1                        
    data.append(resp3)

    if type4 != 'short answer':
            if answer4 != response4:
                    resp4['result']['success'] = False
                    wrong += 1
    else:
            if not set(answer4.split(',')).issubset([str(i).lower().strip() for i in response4.split(",")]):
                    resp4['result']['success'] = False
                    wrong += 1                        
    data.append(resp4)

    if type5 != 'short answer':
            if answer5 != response5:
                    resp5['result']['success'] = False
                    wrong += 1
    else:
            if not set(answer5.split(',')).issubset([str(i).lower().strip() for i in response5.split(",")]):
                    resp5['result']['success'] = False
                    wrong += 1                        
    data.append(resp5)

    result_data = {
                'actor': {'mbox': actor, 'name': actor_name},
                'verb': {'id': 'http://adlnet.gov/expapi/verbs/passed', 'display':{'en-US': 'passed'}},
                'object':{'id':quiz_name, 'definition':{'name':{'en-US':display_name}}},
                'result':{'score':{'min': 0, 'max': 5, 'raw': 5 - wrong}}
                }
    
    if wrong > 2:
            result_data['verb']['id'] = 'http://adlnet.gov/expapi/verbs/failed'
            result_data['verb']['display']['en-US'] = 'failed'
    data.append(result_data)

    post_resp = requests.post(settings.LRS_STATEMENT_ENDPOINT, data=json.dumps(data), headers=settings.HEADERS, verify=False)
    status = post_resp.status_code
    content = post_resp.content

    if status == 200:
            content = json.loads(post_resp.content)                
            st1 = requests.get(settings.LRS_STATEMENT_ENDPOINT + '?statementId=%s' % content[0], headers=settings.HEADERS, verify=False).content
            st2 = requests.get(settings.LRS_STATEMENT_ENDPOINT + '?statementId=%s' % content[1], headers=settings.HEADERS, verify=False).content
            st3 = requests.get(settings.LRS_STATEMENT_ENDPOINT + '?statementId=%s' % content[2], headers=settings.HEADERS, verify=False).content
            st4 = requests.get(settings.LRS_STATEMENT_ENDPOINT + '?statementId=%s' % content[3], headers=settings.HEADERS, verify=False).content
            st5 = requests.get(settings.LRS_STATEMENT_ENDPOINT + '?statementId=%s' % content[4], headers=settings.HEADERS, verify=False).content
            st6 = requests.get(settings.LRS_STATEMENT_ENDPOINT + '?statementId=%s' % content[5], headers=settings.HEADERS, verify=False).content
            st7 = requests.get(settings.LRS_STATEMENT_ENDPOINT + '?statementId=%s' % content[6], headers=settings.HEADERS, verify=False).content
    else:
            st1 = st2 = st3 = st4 = st5 = st6 = st7 = ""

    return template('quiz_results', partname=partname, status=status, score=(5 - wrong), content=content, st1=st1, st2=st2, st3=st3, st4=st4, st5=st5, st6=st6, st7=st7)

@app.route('/makeqr')
def form_qr():
    if not request.cookies.get('account') or not request.cookies.get('name'):
            redirect('/register')
    return template('makeqr.tpl', pw=settings.CREATE_PASSWORD)

@app.route('/makeqr', method='POST')
def create_qr():
    if not request.cookies.get('account') or not request.cookies.get('name'):
            redirect('/register')

    name = request.forms.get('name')

    if name in [d.keys()[0] for d in util.get_existing_pages()]:
        return redirect('/tryagain')

    url_name = urllib.quote_plus(name)
    instructions = request.forms.get('instructions')
    info = request.forms.get('info')

    qrname = url_name + '.png'
    qrdata =  settings.INFO_DOMAIN + url_name
    img = qrcode.make(qrdata)
    
    with open('static/%s' % qrname, 'w+') as qr:
            img.save(qr, 'PNG')

    info_template_name = url_name + '_info.tpl'
    with open('views/%s' % info_template_name, 'w+') as tpl:
            tpl.write(settings.INFO_TEMPLATE.format(name, name + ' Info', info, url_name, url_name, qrname))

    instruction_template_name = url_name + '_instructions.tpl'
    with open('views/%s' % instruction_template_name, 'w+') as tpl:
            tpl.write(settings.INSTRUCTION_TEMPLATE.format(name, name + ' Instructions', instructions, url_name))

    question_template_name = url_name + '_questions.tpl'
    with open ('views/%s' % question_template_name, 'w+') as tpl:
            tpl.write(settings.QUIZ_TEMPLATE)
    return redirect('/info/' + url_name)  

@app.route('/tryagain')
def try_again():
    if not request.cookies.get('account') or not request.cookies.get('name'):
            redirect('/register')    
    return template('try_again')

run(app, server='gunicorn', host='localhost', port=8099, debug=True, reloader=True)