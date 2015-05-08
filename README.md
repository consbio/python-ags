# ArcGIS Server Python Client #

## Overview ##

This library provides a client interface to the REST API on ArcGIS Server 10.2.x
 
Note: This library is a work in progress, and currently only includes interfaces for geoprocessing tasks and server 
administration operations.  Other interfaces will likely be added over time.  

[Documentation](http://arcgis-server-python-client.readthedocs.org/en/latest/)


## Installation ##

*Using pip:*

To install the latest stable version:

```
pip install python-ags
```

To install the latest changes:

```
pip install https://bitbucket.org/databasin/python-ags/get/default.zip#egg=python-ags
```

*Manual installation:*

Download the [latest changes](https://bitbucket.org/databasin/python-ags/get/default.zip), extract, 
and execute 

```
python setup.py install
```


## Usage ##

```
from ags.admin.server import ServerAdmin

server_admin = ServerAdmin(hostname, admin_user, admin_pwd)
print server_admin.list_services()
```


## Requirements ##
requests


## Related Projects ##
There is a new python package from ESRI that provides some overlap with the functionality of this library: 
[ArcREST](https://github.com/Esri/ArcREST)

However, as of this writing, there is no administrative interface for creating services in that package, whereas that
functionality is one of the primary reasons we created this library.



## License ##
Copyright (c) 2013, 2014, 2015 Conservation Biology Institute
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the Conservation Biology Institute nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL CONSERVATION BIOLOGY INSTITUTE BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.