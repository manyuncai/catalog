# Catalog App ![CI status](https://img.shields.io/badge/build-passing-brightgreen.svg)

<b>Catalog App </b> is an application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.


### Repository location
* https://github.com/manyuncai/catalog


### Project Files description
* <a style="color:red">static</a> - folder containing style.css to decorate the html Files
* <a style="color:red">templates</a> - folder containing .html files for each endpoint
* <a style="color:red">database_setup.py</a> - file to create database (catalogdatabasewithusers.db) containing three tables: User, Catalog and CatalogItem
* <a style="color:red">catalogdatabasewithusers.db</a> - create by running database_setup.py
* <a style="color:red">lotsofcatalogItems.py</a> - adding some data to the catalogdatabasewithusers.db
* <a style="color:red">client_secrets.json </a> - Aaoth 2 file from  <a href= "https://console.developers.google.com/apis/dashboard?project=restaurant-menu-app-229519">google API console </a> for authentication with gmail login
* <a style="color:red">project.py</a> - main file, run this file to bring Catalog App in localhost:8000 in the browser


### Installation/Requirement
* Vagrant and VirtualBox
* flask
* sqlalchemy
* python 2.7.12


`pip install flask`

### Setup VM and Download the database
* download vagrant file from <a href= "https://github.com/udacity/fullstack-nanodegree-vm" > VM Setup </a> to set up access to Udacity VM with instruction
* bring the virtual machine online( with <a style="color:red">vagrant up </a>& <a style="color:red">vagrant ssh </a>) in the Windows Powershell or Git Bash terminal (for Windows 10)


### Running the Application
* Clone or download the project in the local machine vagrant directory, for example: <a style="color:red">D:\Full-Stack\fullstack\vagrant\catalog </a>
* for Windows 10, bring up Git Bash terminal,<a style="color:red"> cd D:\Full-Stack\fullstack\vagrant\catalog </a>
* bring the VM up by running <a style="color:red">vagrant up </a> & <a style="color:red">vagrant ssh </a>
* in the VM, run <a style="color:red">cd /vagrant </a> , <a style="color:red"> cd catalog </a> and <a style="color:red">python project.py </a>
* Access and test your application by visiting http://localhost:8000 locally
* use ctrl + c to end the application


### Usage
sqlalchemy module is used to access and create the database in the Python DB-API
```python
from sqlalchemy import create_engine

engine = create_engine('sqlite:///catalogdatabasewithusers.db') # create the database
Base.metadata.bind = engine  
DBSession = sessionmaker(bind=engine) # close the database link
session = DBSession() # point to the database
session.add () # add record
session.commit()
session.close()
```
### Json Endpoints
* @app.route('/catalog/JSON') and @app.route('/catalog.json') provide Json endpoit for all catalog & items
* @app.route('/catalog/<string:sport_name>/<string:goods_name>/JSON') & @app.route('/catalog/<string:sport_name>/<string:goods_name>/json') provides Json endpoint for a single item in the catalog.

### Contributing
All comment and suggestions are welcome to make my project works better

### Known Bugs
None
