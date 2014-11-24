# -*- coding: utf-8 -*-

db = DAL('sqlite://storage.sqlite')
from gluon.tools import *
auth = Auth(db)
service = Service()
plugins = PluginManager()
auth = Auth(db)
auth.define_tables()
crud = Crud(db)
db.define_table('category',Field('name'))

db.define_table('recipe',
                Field('title'),
                Field('image', 'upload'),
                Field('description', length=256),
                Field('category', db.category),
                Field('created_on', 'datetime', default=request.now),
                Field('created_by', 'reference auth_user', default=auth.user_id),
                Field('time_for_preparation'),
                Field('time_for_cooking'),
                Field('number_of_portions'),
                Field('ingredients', 'text'),
                Field('directions', 'text')
                )

db.define_table('attachment',
            Field('recipe_id', 'reference recipe'),
            Field('name'),
            Field('file', 'upload'),
            Field('created_on', 'datetime', default=request.now),
            Field('created_by', 'reference auth_user', default=auth.user_id),
            format='%(name)s')

db.define_table('comment',
            Field('recipe_id', 'reference recipe'),
            Field('body', 'text'),
            Field('created_on', 'datetime', default=request.now),
            Field('created_by', 'reference auth_user', default=auth.user_id))

db.category.name.requires=[IS_NOT_EMPTY(), IS_NOT_IN_DB(db,'category.name')]

db.recipe.title.requires=[IS_NOT_EMPTY(), IS_NOT_IN_DB(db,'recipe.title')]
db.recipe.description.requires=IS_NOT_EMPTY()
db.recipe.description.requires=IS_NOT_EMPTY()
db.recipe.category.requires=IS_IN_DB(db,'category.id','category.name')
db.recipe.created_by.readable = db.recipe.created_by.writable = False
db.recipe.created_on.readable = db.recipe.created_on.writable = False
db.recipe.image.requires=IS_NOT_EMPTY()


db.comment.body.requires = IS_NOT_EMPTY()
db.comment.recipe_id.readable = db.comment.recipe_id.writable = False
db.comment.created_by.readable = db.comment.created_by.writable = False
db.comment.created_on.readable = db.comment.created_on.writable = False

db.attachment.recipe_id.readable = db.attachment.recipe_id.writable = False
db.attachment.created_by.readable = db.attachment.created_by.writable = False
db.attachment.created_on.readable = db.attachment.created_on.writable = False


## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []

## (optional) optimize handling of static files
response.optimize_css = 'concat,minify,inline'
response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

## create all tables needed by auth if not custom tables
auth.define_tables(username=True, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'smtp.gmail.com:587' if request.is_local else 'smtp.gmail.com:587'
mail.settings.sender = 'macanhhuytesting@gmail.com'
mail.settings.login = 'macanhhuytesting:macanhhuydn'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.janrain_account import use_janrain
use_janrain(auth, filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
from gluon.tools import Recaptcha
auth.settings.captcha = Recaptcha(request,
    '6Le-L_4SAAAAANxw1rmZehjdq3thYkGuAHb68u31', '6Le-L_4SAAAAAFCcpS1rC8KpqMezy1eib2wcEPU1')

def captcha_field(request=request):
    w = lambda x,y: Recaptcha(request,
                              '6LcSNv4SAAAAAJEQoL3Xp1g84uGiuemlCRG9ynqi',
                              '6LcSNv4SAAAAACp6iBq1bhP8DKroXZyaKCuG-U1k')
 
    return Field('captcha', 'string', label='Captcha', widget=w, default='ok')
