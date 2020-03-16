from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import status
import os, shutil, requests, subprocess, time
import json, pprint, requests, textwrap

location = None

def save_folder(input_path, storage_path, auth_header):
    headers = {'Authorization': auth_header}

    response = requests.get(url=os.environ['CDRIVE_API_URL'] + "list/?path=" + input_path, headers=headers)
    drive_objects = response.json()['driveObjects']
    for dobj in drive_objects:
        if dobj['type'] == 'Folder':
            os.mkdir(storage_path + '/' + dobj['name'])
            save_folder(input_path + '/' + dobj['name'], storage_path + '/' + dobj['name'], auth_header)
        else:
            url = os.environ['CDRIVE_API_URL'] + "download/?path=" + input_path + '/' + dobj['name']
            download_url = requests.get(url=url, headers=headers).json()['download_url'] 
            response = requests.get(url=download_url)
            open(storage_path + '/' + dobj['name'], 'wb').write(response.content)
     
def livy_initiliaze():
    try:
        host = 'http://riotous-umbrellabird-livy:8998'
        data = {'kind': 'spark'}                                                                                              
        headers = {'Content-Type': 'application/json'}                                                                      
        r = requests.post(host + '/sessions', data=json.dumps(data), headers=headers)
        global location
        location = r.headers['location']
        return r.json()
    except:
        return r.json()
        
def livy_add():
    try:
        host = 'http://riotous-umbrellabird-livy:8998'                                                                                             
        headers = {'Content-Type': 'application/json'}
        if location is not None:
            session_url = host + location
            r = requests.get(session_url, headers=headers)                                                                      
            statements_url = session_url + '/statements'                                                                        
            data = {'code': '1 + 1'}                                                                                            
            r = requests.post(statements_url, data=json.dumps(data), headers=headers)                                           
            statement_url = host + r.headers['location']                                                                        
            r = requests.get(statement_url, headers=headers)                                                                    
            return r.json()
        else:
            raise ValueError('location not set')
    except:
        return r.json()

class Execute(APIView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def post(self, request):
        input_path = request.data['input_path']

        auth_header = request.META['HTTP_AUTHORIZATION']

        feature_gen_path = '/storage/feature-gen'
        if os.path.exists(feature_gen_path):
            shutil.rmtree(feature_gen_path)
        os.mkdir(feature_gen_path)
        save_folder(input_path, feature_gen_path, auth_header)

        feature_gen_out_path = feature_gen_path + '/output'
        os.mkdir(feature_gen_out_path)

        #with open(feature_gen_out_path + '/out.txt', 'w') as f:
        #   subprocess.call('/feature-gen_build/feature-gen', cwd=feature_gen_path, stdout=f)
        resp_livy = livy_add()

        return Response(resp_livy, status=status.HTTP_200_OK)

class Save(APIView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def post(self, request):
        output_path = request.data['output_path']
        auth_header = request.META['HTTP_AUTHORIZATION']

        feature_gen_out_path = '/storage/feature-gen/output'
        for file_name in os.listdir(feature_gen_out_path):
            file_path = feature_gen_out_path + '/' + file_name
            f = open(file_path, 'rb')
            file_arg = {'file': (file_name, f), 'path': (None, output_path)}
            requests.post(os.environ['CDRIVE_API_URL'] + 'upload/', files=file_arg, headers={'Authorization': auth_header})
            f.close() 

        return Response(status=status.HTTP_200_OK)

class Specs(APIView):
    parser_class = (JSONParser,)

    def get(self, request):
        data = {
            'clientId': os.environ['COLUMBUS_CLIENT_ID'],
            'authUrl': os.environ['AUTHENTICATION_URL'],
            'cdriveUrl': os.environ['CDRIVE_URL'],
            'cdriveApiUrl': os.environ['CDRIVE_API_URL'],
            'username': os.environ['COLUMBUS_USERNAME']
        }
        return Response(data, status=status.HTTP_200_OK)

class AuthenticationToken(APIView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def post(self, request, format=None):
        resp_livy = livy_initialize()
        code = request.data['code']
        redirect_uri = request.data['redirect_uri']
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': os.environ['COLUMBUS_CLIENT_ID'],
            'client_secret': os.environ['COLUMBUS_CLIENT_SECRET']
        }
        response = requests.post(url=os.environ['AUTHENTICATION_URL'] + 'o/token/', data=data)

        return Response(response.json(), status=response.status_code)
