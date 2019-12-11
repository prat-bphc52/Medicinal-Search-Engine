from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import pymongo,asyncio

global myclient,mydb,mycol


# This function makes a GET Request to the specified URL and returns the response
def simple_get(url):
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    print(e)

def refine_key(key):
    newkey = ""
    for i in range(len(key)):
        if not key[i]=='.':
            newkey=newkey+key[i]
    return newkey.lower()

def get_tag_text(tag):
    inner_dict = {}
    flag = False
    key = ''
    content=''
    for child in tag.find_all():
        # print(child.name)
        if child.name=='h2':
            if not key=='' and not content=='':
                inner_dict[refine_key(key)]=content
            flag=True
            content=''
            key = child.text
        elif flag:
            if child.name=='p':
                content=content+"\n"+child.text
            elif child.name=='ul':
                for lis in child.find_all('li'):
                    para = lis.find('p')
                    if para is not None:
                        content = content+'\n'+para.text


    if not key=='':
        inner_dict[refine_key(key)]=content
    return inner_dict

def get_details(med_url, med_name):
    details={}
    print('started '+med_name)
    response=simple_get(med_url)
    if response is not None:
        html=BeautifulSoup(response, 'html.parser')
        tabs_holder = html.find('ul',{'class':'nav-tabs nav-tabs-collapse vmig'})
        tab_dict = {}
        if tabs_holder is not None:
            current_tab_txt = ''
            for x in tabs_holder.find_all('li'):
                if x.b is not None:
                    current_tab_txt = x.text
                elif x.a is not None:
                    if not x.has_attr('class'):
                        tab_dict[x.a.text] = "https://www.drugs.com"+x.a['href']
            if not current_tab_txt == '':
                curr_tag = html.find('div',{'class':'contentBox'})
                print("searching here")
                if curr_tag is not None:
                    details[refine_key(current_tab_txt)] = get_tag_text(curr_tag)
        for key in tab_dict:
            res_tab=simple_get(tab_dict[key])
            if res_tab is not None:
                rtag = BeautifulSoup(res_tab, 'html.parser').find('div',{'class':'contentBox'})
                if rtag is not None:
                    details[refine_key(key)] = get_tag_text(rtag)
    details['_id']=med_name
    mycol.insert_one(details)
    print('ended '+med_name)

if __name__ == '__main__':
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["irproject"]
    mycol = mydb["medicines"]
    fr = open("all_medicines.txt", "r")
    total_docs = 20000
    for i in range(total_docs):
        val = fr.readline().split("=")
        print(str(i+1))
        get_details(val[1],val[0])
