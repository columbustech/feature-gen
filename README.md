# Feature generation for entity matching

## Overview

### Steps in EM

Entity Matching (EM) finds data instances across two tables say (A and B) that refer to the same real-world entity, 
such as the two tuples (David Smith, UW-Madison) and (D. Smith, UWM). Clearly the search space here (A cross B) is not
amenable to a brute force approach, so some kind of sampling would need to be done to obtain a sample S. S is typically
large enough to be an accurate approximation of the sample space (A crosss B), but S is still too large for training 
any classifiers to do the matching. So, a blocker B is used to reduce S to a candidate set C. The candidate set C is
then used to train a classifier G. The blocker B may be a rule based blocker but may itself be a classifier F.

In this app, we assume that either S or C are given to us and we focus solely on generating features for training the
classifier G or F. If A tuples are [aid, a1, a2, a3...], B tuples are [bid, b1, b2, b3 ...], then S and C will be 
[id, aid, bid]. Section 3 of [this paper](http://pages.cs.wisc.edu/~anhai/papers1/deepmatcher-sigmod18.pdf) provides a
good summary of the kind of features that are typically generated from S and C for training a classfier.

### What we need to do
In this app, we'll define REST API calls that can generate some of the features discussed in the above link.

First, you will identify some datasets that we can use for this EM problem. Many of them can be found on AnHai's [home
page](https://sites.google.com/site/anhaidgroup/useful-stuff/data). Next, you'll identify some possible features we
can start out with. Good starting choices could be string similarity joins which can be found on the pystring matching 
[github page](https://github.com/anhaidgroup/py_stringmatching/tree/master/py_stringmatching/similarity_measure). 

Next, we need to create a skeleton CDrive app. The main part of the skeleton app will be the use of Oauth to access 
files on user's CDrive. I'll explain it here and provide a skeleton app in this repo for you to understand and use.
The backend will be in django and the frontend will be in React. The whole thing will be containerized of course. 

You will create a basic UI that allows users to select CDrive files representing tables A, B and S(or C). You will
provide some kind of menu from which a user can select some subset of features. Keep the UI as simple as possible, keep
the backend API endpoints as clean as possible. The REST API endpoints will later be used to create a python wrapper as
well, but you don't need to worry about that right now. 

Spark has already been deployed on the kubernetes. The Kubernetes cluster has one master and three workers but this can
be scaled at any point if we need to run bigger workloads. Spark has been deployed as a set of two worker pods, one 
master pod, one livy pod and one zepplin pod. [Livy](https://livy.incubator.apache.org/examples/) is a REST server for
managing Spark jobs. You will submit Spark jobs from the feature-gen app backend by making REST API calls to the livy
service. If you guys have time, I also recommend reading up on [helm](https://helm.sh/).

### What next
Once this app is done, we move onto training some ML models. We can reuse much of the same framework for the training
apps.

## Detailed instructions

### EC2 machine access

The cloudpandas.pem key will allow you to access an EC2 machine.

`ssh -i <path_to_cloudpandas.pem> ec2-user@ec2-34-207-228-250.compute-1.amazonaws.com`

Note that this a different machine to the one I provided access to earlier. This machine has access to a 3 node 
Kubernetes cluster which you can manage using the [kubectl](https://kubernetes.io/docs/reference/kubectl/overview/) 
command line tool. 

### Feature gen app

I have provided you access to the [feature-gen](https://www.github.com/columbustech/feature-gen) github repo. The code
is also alread present in the EC2 machine at ~/feature-gen. 

To build the app, first go into the UI directory and build the UI:
`(cd ui && npm run build)`

Then, build the docker image:
`sudo docker build -t <docker_username>/<app_name> .`

Push image to dockerhub:
`sudo docker push <docker_username>/<app_name>`

The machine already has docker credentials for the columbustech account, so you could just do:
`sudo docker push columbustech/feature-gen`

### Installing the app

Use this [test deployment](https://cdrive.columbusecosystem.com). Create an account, log in, go to apps, click install.
Give it the path to the app (eg:docker.io/columbustech/feature-gen:latest). Once it's installed, you need to upload
your input files to cdrive, and share it with the app. 

### Oauth flows to access CDrive data

The app needs to carry out an Oauth flow in order to access user's CDrive data. The code for this is already present
in the skeleton app. The app UI makes a request to it's backend to get specs of the deployment such as the URL where
it has been deployed, the authentication url, username etc. Then the app UI redirects the user to the authentication
URL with two query parameters, client\_id and redirect\_url. Whenver an app is installed, a client id and a client 
secret environment variables are set in the container. The client\_id above refers to this. The redirect\_url is the
app url, which is <CDRIVEURL>/app/<USERNAME>/<APPNAME>. The authentication server will redirect the user back to
the app url with a code query parameter. The app can then make a POST request to the authentication server to get an
authentication token. The app UI will pass the code parameter to it's backend, and the backend will make the POST 
request mentioned above. It will pass the code, the app client id and app client secret in the body of the POST and
receive an authentication token in response. The POST request is made over Kubernetes' internal network. 

The app will store the authentication token in the browser cookies. The token enables the app to access a user's CDrive
files (for which it has access permissions). Note that the code for this is already present, you can directly use the
authentication token to access CDrive files and make other API calls to CDrive. You can take a look at other CDrive
apps such as [Fahes MVD](https://www.github.com/columbustech/fahes-mvd) or 
[GLM numerical mode](https://www.github.com/columbustech/glm-numerical-model) to see how this is done.

### Accessing the app

You can open a terminal to the app pod with the following command from the EC2 machine:
`kubectl exec -it $(kubectl get pods|awk '/feature/{print$1}') -- /bin/bash`

Once inside the pod, you have access to the Kubernetes internal network. The Livy service is available at
http://riotous-umbrellabird-livy:8998 and the above mentioned oauth service is available at http://authentication.

You can list all services with:
`kubectl get svc`

You can similarly list pods and deployments as well as other Kubernetes resources.

While making UI changes, I recommend the following procedure:

1. Install the app.
2. Make UI code changes in the repo within the EC2 machine.
3. Copy them to the app container with:
`kubectl cp ui/src $(kubectl get pods|awk '/feature/{print$1}'):/ui/`
4. Open a terminal in the container as detailed above.
5. Build the UI with
`(cd /ui && npm run build)`
6. Copy to static files location:
`cp -r /ui/build/\* /var/www/frontend/`

For backend code changes, you can follow a similar procedure, except you don't need to recompile the code, the server
is listening for code changes, by default.

Once you've pulled the required CDrive files into the app backend, use the python requests library to submit Spark jobs
to the Livy service.
