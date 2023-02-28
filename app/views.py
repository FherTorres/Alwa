from typing import List, Dict
#from flask_mysqldb import MySQL
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
#import mysql.connector
import json
import os
import base64
from flask import request, render_template, jsonify, Response, flash, redirect, url_for,jsonify, session
from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, FileField, SelectField, PasswordField, SubmitField, validators, HiddenField)
from wtforms.validators import DataRequired, Email, EqualTo, Length, InputRequired, ValidationError, Optional
from werkzeug.utils import secure_filename
from app import app
import time
import glob
from werkzeug.datastructures import MultiDict
import hashlib
import json
import zipfile
import requests



app.config.update(
    DSPACE_IP="192.168.1.71",
    PAINAL_IP="192.168.1.73",
    SECRET_KEY="Alwa"
)


painal_url = "http://"+app.config['PAINAL_IP']+":20500/"
dspace_url = "http://"+app.config['DSPACE_IP']+":8080/server/api/"
dspace_url_v6 = "http://"+app.config['DSPACE_IP']+":8080/rest/"
create_item_endpoint = "core/items?owningCollection="
login_endpoint = "authn/login"
status_endpoint = "authn/status"
user="test@test.edu"
password="admin"

#app.config['SECRET_KEY']="catalogos"
#app.config['MYSQL_HOST'] = 'db'
#app.config['MYSQL_USER'] = 'root'
#app.config['MYSQL_PASSWORD'] = 'root'
#app.config['MYSQL_DB'] = 'catalogos'
#db = MySQL(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/'


class User(UserMixin):

    def __init__(self, id, username, password, first_name, second_name, user_type) -> None:
        self.id = id
        self.username = username
        self.password = password
        self.first_name = first_name
        self.second_name = second_name
        self.user_type = user_type

    @classmethod
    def check_password(self, hashed_password, password):
        return check_password_hash(hashed_password, password)

class ModelUser():
    @classmethod
    def login(self, username, password, cookie):
        try:
            #cursor = db.connection.cursor()
            #sql = """SELECT id_user, username, password, first_name, second_name, user_type FROM users WHERE username = '{}'""".format(username)
            #cursor.execute(sql)
            #row = cursor.fetchone()
            #if row != None:
            #    print("SIUx2")
            #    print("Siux2")
            #    print(row[2],password)
            #    print(type(password))
            #    print(type(row[2]))
            #    if(row[2] == password):
            #        print("LLEGO")
            user = User("1", username, password, "First_name", "Second_name", cookie)
            return user
            #return None
        except Exception as ex:
            raise Exception(ex)
        
        finally:
            print("SE CIERRA CURSOR")
            #cursor.close()
            

    @classmethod
    def get_by_id(self, id):
        try:
            #cursor = db.connection.cursor()
            #sql = "SELECT id_user, username, first_name, second_name, user_type FROM users WHERE id_user = {}".format(id)
            #cursor.execute(sql)
            #row = cursor.fetchone()
            #if row != None:
            return User("1", "username", "password", "First_name", "Second_name", "cookie")
            #else:
                #return None
        except Exception as ex:
            raise Exception(ex)
        
        finally:
            print("SE CIERRA CURSOR")
            #cursor.close()
        


@login_manager.user_loader
def load_user(id_user):
    return ModelUser.get_by_id(id_user)

def conexion_db():
    conn = mysql.connector.connect(
        host="db",
        user="root",
        password="root",
        database="catalogos"
    )
    return conn

##### AGREGAR CATALOGO EN AUTOMATICO PARA EJEMPLO
#def agregar_catalogo_ejemplo():
#    conn = conexion_db()
#    sql = "INSERT INTO catalogos (nombre_catalogo,descripcion_catalogo,archivo_catalogo,archivo_nombre,usuario_catalogo) VALUES (%s,%s,%s,%s,%s)"
#    cursor = conn.cursor()
#    with open("app/CV_MarianaHinojosa.pdf","rb") as pdf_file:
#        archivo_binario = pdf_file.read()
#
#    cursor.execute(sql, ("Catalogo Ejemplo","Descripcion ejemplo",archivo_binario,"archivo_ejemplo.pdf","admin",))
#    conn.commit()

#agregar_catalogo_ejemplo()

class CatalogoForm(FlaskForm):
    nombre = StringField('Nombre catálogo', validators=[InputRequired(),Length(min=10, max=100)])
    descripcion = TextAreaField('Descripcion catálogo',validators=[InputRequired(),Length(max=200)])
    archivo = FileField('Archivo catálogo')


class UsuarioForm(FlaskForm):
    usuario = StringField('Usuario', validators=[Email(message='Ingrese un correo valido'),DataRequired()])
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellido = StringField('Apellido', validators=[DataRequired()])
    tipo = SelectField(u'Tipo Usuario', choices=[('1', 'Admin'), ('2', 'Normal')])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    confirmar = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password',message='Las contraseñas deben coincidir')])
    def validate_usuario(self, field):
        try:
            sql = """SELECT username FROM users WHERE username = '{}'""".format(field.data)
            cursor = db.connection.cursor()
            cursor.execute(sql)
            row = cursor.fetchone()
            if row != None:
                raise ValidationError('Ese usuario ya existe, elige uno diferente')
        finally:
            cursor.close()
            
            
def validate_same_username(form,field):
    if(form.usuario_compare.data != field.data):
        try:
            sql = """SELECT username FROM users WHERE username = '{}'""".format(field.data)
            cursor = db.connection.cursor()
            cursor.execute(sql)
            row = cursor.fetchone()
            if row != None:
                raise ValidationError('Ese usuario ya existe, elige uno diferente')
        finally:
            cursor.close()
            
                      
class UsuarioFormUpdate(FlaskForm):
    usuario = StringField('Usuario', validators=[Email(message='Ingrese un correo valido'),DataRequired(), validate_same_username])
    usuario_compare = HiddenField()
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellido = StringField('Apellido', validators=[DataRequired()])
    tipo = SelectField(u'Tipo Usuario', choices=[('1', 'Admin'), ('2', 'Normal')],default=2)
    password = PasswordField('Contraseña', validators=[Optional(), EqualTo('confirmar',message='Las contraseñas deben coincidir')])
    confirmar = PasswordField('Confirmar Contraseña', validators=[Optional(), EqualTo('password',message='Las contraseñas deben coincidir')])
        
        
        
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template("login.html")
    

def login_dspacev6(user,password):
    print("LOGIN DSPACE!!")
    user = "test@test.edu"
    password = "admin"
    user = user.replace("@", "%40")
    url = dspace_url_v6+"login"

    payload = 'email='+user+'&'+'password='+password
    print(payload)
    
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response)
    code = response.status_code 
    if  code == 200:
        cookie_dict = dict(response.cookies)
        return {'code':200, 'data':{'jsessionid':cookie_dict['JSESSIONID']}}  
    elif code == 401:
        return {'code':401, 'data':{}}

def login_painal(user,password):
    print("LOGIN PAINAL!!")
    url = painal_url+"auth/v1/users/login"

    payload = json.dumps({
        "user": user,
        "password": password
    })
    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response)
    print(response.text)
    if(response.status_code==200):
        response = response.json()
        return {'code':200, 'data':{'painal_token_user':response['data']['tokenuser'], 'painal_api_key':response['data']['apikey'], 'painal_access_token':response['data']['access_token']}}
    return {'code':400}

@app.route('/login', methods=['POST'])
def login():
    print("LOGIN")
    password = request.form['password']
    user = request.form['user']
    print(password,user)
    dspace_login_response = login_dspacev6(user,password)
    #dspace_login_code = 200
    painal_login_response = login_painal(user,password)
    
    if(dspace_login_response['code'] == 200 and painal_login_response['code'] == 200):
        session['cookie'] = dspace_login_response['data']['jsessionid']
        session['painal_token_user'] = painal_login_response['data']['painal_token_user']
        session['painal_api_key'] = painal_login_response['data']['painal_api_key']
        session['painal_access_token'] = painal_login_response['data']['painal_access_token']
        user = ModelUser.login(user, password, session['cookie'])
        login_user(user)
        return redirect(url_for('index'))
    else:
        return redirect(url_for('home'))





@app.route('/dashboard')
@login_required
def dashboard():
    
    print(session)
    print("DASHBOARD COOKIE")
    print(session['cookie'])



    url = dspace_url_v6+"communities"
    payload={}
    headers = {
        'Accept': 'application/json',
        'Cookie': 'JSESSIONID='+session['cookie']
    }
    
    response = requests.request("GET", url, headers=headers, data=payload).json()
    print(response)
    print(type(response))

    return render_template('dashboard.html', data=response)


@app.route('/logout')
def logout():
    url = dspace_url_v6+"logout"
    payload={}
    headers = {
        'Cookie': 'JSESSIONID='+session['cookie']
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response)
    session.clear()
    logout_user()
    return redirect(url_for('home'))


@app.route('/create_collection')
def create_collection():
    return render_template('create_collection.html')

@app.route('/create_item')
def create_item():
    return render_template('create_item.html')

@app.route('/digital_resources', methods=["POST"])
def digital_resources():
    content = request.get_json()
    print(content)
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


@app.route('/view_collections')
def view_collections():
    uuid = request.args.get('uuid')
    name = request.args.get('name')
    url = dspace_url_v6+"communities/"+uuid+"/collections"
    payload={}
    headers = {
        'Accept': 'application/json',
        'Cookie': 'JSESSIONID='+session['cookie']
    }

    response = requests.request("GET", url, headers=headers, data=payload).json()
    print(response)

    return render_template('view_collections.html', data=response, name=name)

@app.route('/view_items')
def view_items():
    uuid = request.args.get('uuid')
    community_name = request.args.get('communityName')
    collection_name = request.args.get('collectionName')
    url = dspace_url_v6+"collections/"+uuid+"/items"
    payload={}
    headers = {
        'Accept': 'application/json',
        'Cookie': 'JSESSIONID='+session['cookie']
    }

    response = requests.request("GET", url, headers=headers, data=payload).json()
    print(response)

    return render_template('view_items.html', data=response, community_name=community_name, collection_name=collection_name)



@app.route('/create_item_rest', methods = ['POST'])
def create_item_rest():
    collection_uuid = request.args.get('uuid')
    content = request.get_json()
    url = dspace_url + create_item_endpoint + collection_uuid
    
    print(type(content))
    print(session)
    payload = json.dumps(content)
    print(payload)
    headers = {
        'X-XSRF-TOKEN': session['X-XSRF-TOKEN'],
        'Authorization': session['token_bearer'],
        'Content-Type': 'application/json',
        'Cookie': 'DSPACE-XSRF-COOKIE='+session['X-XSRF-TOKEN']
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response)
    print(response.text)
    
    if(response.status_code == 403):
            return json.dumps({'success':False, 'Message':'Vuelve a autenticarte'}), 403, {'ContentType':'application/json'}
    elif(response.status_code == 400):
        return json.dumps({'success':False, 'Message':'Al parecer el UUID que estas usando no es de una coleccion!'}), 403, {'ContentType':'application/json'}

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
    


@app.route('/local_login_dspace', methods = ['POST'])
def local_login_dspace():
    session['X-XSRF-TOKEN'], session['token_bearer'] = login_dspace()

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

def login_dspace():
    url = dspace_url + status_endpoint
    print(url)
    payload = json.dumps({})
    
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    
    response = requests.request("GET", url, headers=headers, data=payload)
    print(response)
    print(response.cookies)
    cookie_dict = dict(response.cookies)
    
    XSRF_COOKIE = cookie_dict["DSPACE-XSRF-COOKIE"]

    url = dspace_url + login_endpoint + "?user=" +user+"&password="+password
    print(url)

    payload={}
    headers = {
        'X-XSRF-TOKEN': XSRF_COOKIE,
        'Cookie': 'DSPACE-XSRF-COOKIE='+XSRF_COOKIE
    }
    print(response)
    print(headers)

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.headers)
    

    headers_dict = dict(response.headers)

    XSRF_COOKIE = headers_dict['DSPACE-XSRF-TOKEN']
    token_bearer = headers_dict['Authorization']

    return XSRF_COOKIE, token_bearer


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/grupos')
def grupos():
    groups_response = get_painal_groups(session['painal_token_user'], session['painal_access_token'])
    return render_template('grupos.html', data=groups_response)



@app.route('/catalogos')
def catalogos():
    url = painal_url+"pub_sub/v1/view/catalogs/user/"+session['painal_token_user']+"/subscribed?access_token="+session['painal_access_token']
    print(url)

    payload = json.dumps({
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    try:
        response = response.json()
    except ValueError:
        response = {'data':[]}

    groups_response = get_painal_groups(session['painal_token_user'], session['painal_access_token'])

    

    return render_template('catalogos.html', data = response['data'], groups = groups_response)


@app.route('/registro')
def registro():
    organizations_response = get_painal_organizations()
    return render_template('registro.html', data=organizations_response)

@app.route('/user_register', methods=['POST'])
def user_register():
    content = request.get_json()
    url = painal_url+"auth/v1/users/create"

    payload = json.dumps({
        "username": content['username'],
        "email": content['email'],
        "password": content['password'],
        "tokenorg": content['tokenorg']
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    code = response.status_code
    response = response.json()
    print(response)
    print(code)
    if(code == 201):
        return json.dumps(response['data']), 200, {'ContentType':'application/json'}
    return json.dumps(response['data']), 400, {'ContentType':'application/json'}


def get_painal_organizations():
    url = painal_url+"auth/v1/view/hierarchy/all"
    payload={}
    headers = {}
    try:
        response = requests.request("GET", url, headers=headers, data=payload).json()
        #response = {'data':""}
    except:
        response = {'data':""}
    print(response)
    return response['data']

def get_painal_groups(painal_token_user, painal_access_token):
    url = painal_url+"pub_sub/v1/view/groups/user/"+painal_token_user+"/subscribed?access_token="+painal_access_token

    payload = json.dumps({
    })
    headers = {
        'Content-Type': 'application/json'
    }

    groups_response = requests.request("GET", url, headers=headers, data=payload).json()
    print(groups_response)
    return groups_response['data']




