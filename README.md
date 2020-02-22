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
