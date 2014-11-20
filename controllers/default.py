# -*- coding: utf-8 -*-
def contactform():
    form=SQLFORM.factory(
        Field('your_email',requires=IS_EMAIL()),
        Field('question',requires=IS_NOT_EMPTY()))
    if form.process().accepted:
        if mail.send(to='macanhhuydn@gmail.com',
        subject='From %s' % form.vars.your_email,
        message=form.vars.question):
            redirect(URL('contactform'))
    elif form.errors:
        form.errors.your_email='Unable to send email'
    return dict(form=form)

@auth.requires_signature()
def ask():
#     {{=LOAD('contact','ask.load',ajax=True,user_signature=True)}}
    pass

def index():
    records=db(db.recipe.category==request.vars.category)\
            .select(orderby=db.recipe.title)
    form=SQLFORM(db.recipe,fields=['category'])
    return dict(form=form,records=records)

@auth.requires_login()
def new_category():
    fields = [field for field in db.category]
#     fields += [
#     Field('customer_type','string', label=T('Customer Type'),
#          requires=IS_IN_SET(customer_types, zero=None, sort=False)),
#     Field('another_field','string', label=T('Another Field')),
#     ]
    fields += [captcha_field()]
    form = SQLFORM.factory(
    *fields,
    formstyle='bootstrap',
    _class='category form-horizontal',
    table_name='category'
    )
    if form.accepts(request.vars,session):
        db.category.insert(**db.category._filter_fields(form.vars))
        response.flash='done!'
#         if mail:
#             session.name = form.vars.name
#             session.email = form.vars.email
#             session.subject = form.vars.subject
#             session.message = form.vars.message
#             if mail.send(to=['otheremail@yahoo.com'],
#                 subject='project minerva',
#                 message= "Hello this is an email send from contact us form.\nName:"+ session.name+" \nEmail : " + session.email +"\nSubject : "+session.subject +"\nMessage : "+session.message+ ".\n "
#             ):
#                 response.flash = 'email sent sucessfully.'
#             else:
#                 response.flash = 'fail to send email sorry!'
#         mail.send('macanhhuydn@gmail.com',
#         request.vars.subject,
#         request.vars.message,
#         attachments = files
#                  )
        redirect(URL('index'))
    elif form.errors.has_key('captcha'):
        response.flash='invalid capctha'
    else:
        pass
#         response.flash='some other error in your form'
#         redirect(URL('index'))
    return dict(form=form)


def contact():
    files = []
    for var in request.vars:
         if var.startswith('attachment') and request.vars[var] != '':
             # Insert
             element = request.vars[var]
             number = db.documents.insert(attachment=db.documents.attachment.store(
                 element.file,element.filename))

             # Retrieve new file name
             record = db.documents(db.documents.id==number)
             files += [Mail.Attachment(filepath + '/' + record.attachment,
                                       element.filename)]
    response.flash = 'Mail sent !'
    mail.send('macanhhuydn@gmail.com',
        request.vars.subject,
        request.vars.message,
        attachments = files
                 )
    return dict()

def show():
    id=request.vars.id
    recipes = db(db.recipe.id==id).select() or redirect(URL('index'))
#     recipe_id=request.vars.id or redirect(URL('index'))
#     recipes=db(db.recipe.id==1).select()
    if not len(recipes):
        redirect(URL('index'))
    form = SQLFORM(db.comment).process() if auth.user else None
    comments = db(db.comment.recipe_id==id).select()
    return dict(recipe=recipes[0], comments=comments, form=form)

def new_recipe():
#     form=SQLFORM(db.recipe,fields=['title','description',\
#                                'category','instructions'])
    form=SQLFORM(db.recipe)
    if form.accepts(request,session):
        redirect(URL('index'))
    return dict(form=form)


def user():
	return dict(form=auth())

def download():
	"""allows downloading of documents"""
	return response.download(request, db)

def search():
	"""an ajax wiki search page"""
	return dict(form=FORM(INPUT(_id='keyword',_name='keyword',
                _onkeyup="ajax('callback', ['keyword'], 'target');")),
                target_div=DIV(_id='target'))

def callback():
	"""an ajax callback that returns a <ul> of links to wiki pages"""
	query = db.recipe.title.contains(request.vars.keyword)
	recipes = db(query).select(orderby=db.recipe.title)
	links = [A(p.title, _href=URL('show',args=r.id)) for r in recipes]
	return UL(*links)

def feed():
    """generates rss feed form the recipes"""
    response.generic_patterns = ['.rss']
    recipes = db().select(db.recipe.ALL, orderby=db.recipe.title)
    return dict(
        title = 'mywiki rss feed',
        link = 'http://127.0.0.1:8000/',
        description = 'all recipes',
        created_on = request.now,
        items = [
            dict(title = row.title,
            link = URL('show', args=row.id),
            description = MARKMIN(row.body).xml(),
            created_on = row.created_on
            ) for row in recipes])

service = Service()

@service.xmlrpc
def find_by(keyword):
    """finds pages that contain keyword for XML-RPC"""
    return db(db.recipe.title.contains(keyword)).select().as_list()

def call():
    """exposes all registered services, including XML-RPC"""
    return service()
