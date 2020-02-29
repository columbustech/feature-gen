from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import status
import os, requests, time


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



class Save(APIView):
    parser_class = (JSONParser,)

    @csrf_exempt
    def post(self, request):
        output_path = request.data['output_path']
        auth_header = request.META['HTTP_AUTHORIZATION']

        glm_out_path = '/storage/glm/output'
        for file_name in os.listdir(glm_out_path):
            file_path = glm_out_path + '/' + file_name
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
