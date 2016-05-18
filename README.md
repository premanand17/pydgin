# PYDGIN - PYthon Disease Generic INterface

A web-based project focused on the genetics and genomics of immunologically related human diseases.

|                                                                   **D-I-L/master**                                                                   |                                                                    **D-I-L/develop**                                                                   |
|:----------------------------------------------------------------------------------------------------------------------------------------------------:|:------------------------------------------------------------------------------------------------------------------------------------------------------:|
| [![Build Status](https://travis-ci.org/D-I-L/pydgin.svg?branch=master)](https://travis-ci.org/D-I-L/pydgin)                                          | [![Build Status](https://travis-ci.org/D-I-L/pydgin.svg?branch=develop)](https://travis-ci.org/D-I-L/pydgin)                                           |
| [![Coverage Status](https://coveralls.io/repos/github/D-I-L/pydgin/badge.svg?branch=master)](https://coveralls.io/github/D-I-L/pydgin?branch=master) | [![Coverage Status](https://coveralls.io/repos/github/D-I-L/pydgin/badge.svg?branch=develop)](https://coveralls.io/github/D-I-L/pydgin?branch=develop) |

### Running Tests

python runtests.py

### Applications Used By PYDGIN

* [django-criteria](https://github.com/D-I-L/django-criteria); used to manage creation and management of criteria index
* [django-data-pipeline](https://github.com/D-I-L/django-data-pipeline); used to populate ElasticSearch indices
* [django-elastic](https://github.com/D-I-L/django-elastic); python interface for creating ElasticSearch queries
* [django-pydgin-auth](https://github.com/D-I-L/django-pydgin-auth); authentication and authorisation app

### Using Docker

Docker repositories are available to assist setting up:

* [pydgin-docker](https://github.com/D-I-L/pydgin-docker); Pydgin, Nginx, Elasticsearch, Postgres containers
* [rserve-docker](https://github.com/D-I-L/rserve-docker); Rserve container
* [jenkins-docker](https://github.com/D-I-L/jenkins-docker); Jenkins-CI, Elasticsearch, Postgres containers for
data pipeline automation and testing

along with DockerHub repositories and images:

* [tcarver/pydgin-docker](https://hub.docker.com/r/tcarver/pydgin-docker/)
* [tcarver/rserve-docker](https://hub.docker.com/r/tcarver/rserve-docker/)
