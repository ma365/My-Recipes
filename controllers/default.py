# -*- coding: utf-8 -*-

def contactform():
    form=SQLFORM.factory(
    Field('your_name', requires=IS_NOT_EMPTY()),
    Field('your_email', requires=IS_EMAIL()),
    Field('your_content', 'text', requires=IS_NOT_EMPTY()),
    captcha_field()
)
    if form.process().accepted:
        if mail.send(to='macanhhuydn@gmail.com',
        subject='From %s' % form.vars.your_name,
        message=form.vars.your_content):
            redirect(URL('contactform'))
    elif form.errors:
        form.errors.your_email='Unable to send email'
    response.title = 'Contact Us'
    return dict(form=form)

@auth.requires_signature()
def ask():
#     {{=LOAD('contact','ask.load',ajax=True,user_signature=True)}}
    pass

def index():
    records=db(db.recipe).select(orderby=db.recipe.id, limitby=(0,20))
    response.title = 'Home Page'
    return dict(records=records)

def all_recipes():
    if len(request.args):
        page=int(request.args[0])
    else:
        page = 0
    items_per_page = 15
    limitby = (page*items_per_page,(page+1)*items_per_page+1)
    rows = db().select(db.recipe.ALL,limitby=limitby)
    response.title = 'All Recipes'
    return dict(rows=rows, page=page,items_per_page=items_per_page)

def my_recipes():
    records=db(db.recipe.created_by==auth.user_id).select(orderby=db.recipe.title)
#     form=SQLFORM(db.recipe,fields=['category'])
    response.title = 'My Recipes'
    return dict(records=records)

@auth.requires_membership('manager')
def manage():
    grid = SQLFORM.smartgrid(db.recipe)
    response.title = 'Manage Recipes'
    return dict(grid=grid)

@auth.requires_login()
def new_category():
    fields = [field for field in db.category]
    form = SQLFORM.factory(
    *fields,
    formstyle='bootstrap',
    _class='category form-horizontal',
    table_name='category'
    )
    response.title = 'New Category'
    if form.accepts(request.vars,session):
        db.category.insert(**db.category._filter_fields(form.vars))
        response.flash='done!'
        redirect(URL('index'))
    elif form.errors.has_key('captcha'):
        response.flash='invalid capctha'
    else:
        pass
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
    this_recipe = db.recipe(request.args(0,cast=int)) or redirect(URL('index'))
    db.comment.recipe_id.default = this_recipe.id
    form = SQLFORM(db.comment).process() if auth.user else None
    comments = db(db.comment.recipe_id==this_recipe.id).select()
    response.title = this_recipe.title
    return dict(recipe=this_recipe, comments=comments, form=form)

@auth.requires_login()
def edit():
    this_recipe = db.recipe(request.args(0,cast=int)) or redirect(URL('index'))
    if this_recipe.created_by != auth.user_id:
        redirect(URL('index'))
    response.title = this_recipe.title
    form = SQLFORM(db.recipe, this_recipe).process(next = URL('show',args=request.args))
    return dict(form=form)

@auth.requires_login()
def delete():
    this_recipe = db.recipe(request.args(0,cast=int)) or redirect(URL('index'))
    if this_recipe.created_by == auth.user_id:
        db(db.recipe.id == this_recipe.id).delete()
    redirect(URL('index'))

@auth.requires_login()
def new_recipe():
#     form=SQLFORM(db.recipe,fields=['title','description',\
#                                'category','instructions'])
    form=SQLFORM(db.recipe)
    if form.accepts(request,session):
        redirect(URL('index'))
    response.title = 'New Recipe'
    return dict(form=form)

def user():
	return dict(form=auth())

def download():
	"""allows downloading of documents"""
	return response.download(request, db)

def search():
    if len(request.args):
        page=int(request.args[0])
    else:
        page = 0
    items_per_page = 15
    limitby = (page*items_per_page,(page+1)*items_per_page+1)
    query = db.recipe.title.contains(request.vars.keyword)
    rows = db(query).select(orderby=db.recipe.id,limitby=limitby)
    response.title = 'Search Results'
    return dict(rows=rows, page=page,items_per_page=items_per_page)

def search_ajax():
    """an ajax search page"""
    response.title = 'Search Recipes'
    return dict(form=FORM(INPUT(_id='keyword',_name='keyword',
                _onkeyup="ajax('callback', ['keyword'], 'target');")),
                target_div=DIV(_id='target'))

def callback():
    """an ajax callback that returns a <ul> of links to wiki pages"""
    query = db.recipe.title.contains(request.vars.keyword)
    recipes = db(query).select(orderby=db.recipe.id)
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
