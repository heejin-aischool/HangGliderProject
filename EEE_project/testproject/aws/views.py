from django.shortcuts import render, redirect
from aws.models import token
from konlpy.tag import Okt
import json
from django.contrib.auth.models import User
from django.contrib import auth
from django.utils.safestring import mark_safe

def preprocessing_text(sentence):
    okt=Okt()
    not_word=['Josa','Punctuation','Suffix']
    stop_word=['분','하다','것','여기','이다','나오니','부분','기술']
    wrong_word=['안녕하다', '오신','수고','보다','되어다','해주다','지금','진행','이','Ai','이용','청각장애','위해']
    edit_word=['안녕하세요', '오다','수고하다','만나다','되다','부탁','지금부터','진행하다','이것','Ai기술','이용하다','청각장애인','위하다']

    ori_text = okt.pos(sentence,stem=True)
    pre_text=[]
    idx_=0
    TF_bool=True
    for word in ori_text:
        idx=0
        trash=''
        if word[0]=='프로그램' and TF_bool:
            pre_text.append('무엇')
            TF_bool=False
            idx_+=1
            continue
        elif word[0]=='가다':
            pre_text.append('해보다')
            break
        elif word[0]=='이니':
            pre_text.append('때문에')
            pre_text.append('천천히')
            pre_text.append('하다')
            break
        elif word[0]=='수화':
            pre_text.append(word[0])
            pre_text.append('바꾸다')
            continue
        elif word[0]=='배우다':
            pre_text.append(word[0])
            pre_text.append('~던')
            continue    
        elif word[0]=='소통':
            pre_text.append(word[0])
            pre_text.append('돕다')
            continue
        elif (word[0] not in stop_word) and (word[1] not in not_word):
            if word[0] in wrong_word :
                idx=wrong_word.index(word[0])
                pre_text.append(edit_word[idx])
                idx_+=1
                continue
            if word[0]=='내용':
                trash=pre_text[idx_-1]
                pre_text[idx_-1]=word[0]
                pre_text.append(trash)
                idx_+=1
                continue
            pre_text.append(word[0])
            idx_+=1
    if '표현' in pre_text and '부탁' in pre_text:
        pre_text.remove('부탁')
    if 'Ai기술' in pre_text and '되다' in pre_text:
        pre_text.remove('되다')
    if '복습' in pre_text and '시간' in pre_text:
        pre_text.remove('시간')
    
    return pre_text

ERROR_MSG = {
    'ID_EXIST': '이미 사용 중인 아이디 입니다.',
    'ID_NOT_EXIST': '존재하지 않는 아이디 입니다',
    'ID_PW_MISSING': '아이디와 비밀번호를 다시 확인해주세요.',
    'PW_CHECK': '비밀번호가 일치하지 않습니다.',
}

def signup(request):

    context = {
        'error': {
            'state': False,
            'msg': ''
        }
    }
    if request.method == 'POST':
        
        user_id = request.POST['user_id']
        user_pw = request.POST['user_pw']
        user_pw_check = request.POST['user_pw_check']

        if (user_id and user_pw):

            user = User.objects.filter(username=user_id)

            if len(user) == 0:

                if (user_pw == user_pw_check):

                    created_user = User.objects.create_user(
                        username=user_id,
                        password=user_pw
                    )

                    auth.login(request, created_user)
                    return redirect('home')
                else:
                    context['error']['state'] = True
                    context['error']['msg'] = ERROR_MSG['PW_CHECK']
            else:
                context['error']['state'] = True
                context['error']['msg'] = ERROR_MSG['ID_EXIST']
        else:
            context['error']['state'] = True
            context['error']['msg'] = ERROR_MSG['ID_PW_MISSING']

    return render(request, 'signup.html', context)

def login(request):
    context = {
        'error': {
            'state': False,
            'msg': ''
        },
    }

    if request.method == 'POST':
        user_id = request.POST['user_id']
        user_pw = request.POST['user_pw']

        user = User.objects.filter(username=user_id)

        if (user_id and user_pw):
            if len(user) != 0:
                user = auth.authenticate(
                    username=user_id,
                    password=user_pw
                )

                if user != None:
                    auth.login(request, user)

                    return redirect('home')
                else:
                    context['error']['state'] = True
                    context['error']['msg'] = ERROR_MSG['PW_CHECK']
            else:
                context['error']['state'] = True
                context['error']['msg'] = ERROR_MSG['ID_NOT_EXIST']
        else:
            context['error']['state'] = True
            context['error']['msg'] = ERROR_MSG['ID_PW_MISSING']

    return render(request, 'login.html', context)

def logout(request):
    auth.logout(request)

    return redirect('home')

# Create your views here.
def home(request):
    
    return render(request, 'home.html')




def result(request):
    if request.method =='POST':
        text = request.POST['text1']
        texts = preprocessing_text(text)
        print(texts)
        q_list=[]
        for word in texts:
            query=token.objects.get(text=word)
            q_list.append(query.url)
        print(q_list)
        q = mark_safe(json.dumps(q_list))
        context={
            'q':q
        }
        return render(request, 'result.html', context)

    return render(request, 'result.html')


        
