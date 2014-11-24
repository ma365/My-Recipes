# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.logo = A(B('my recipes'),
                  _class="brand",_href="/")
response.title = request.application.replace('_',' ').title()
response.subtitle = ''

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Your Name <you@example.com>'
response.meta.keywords = 'web2py, python, framework'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = [
    (T('Home'), False, URL('default', 'index'), [])
]

DEVELOPMENT_MENU = True

#########################################################################
## provide shortcuts for development. remove in production
#########################################################################

def _():
    # shortcuts
    app = request.application
    ctr = request.controller
    # useful links to internal and external resources
    if auth.user_id:
        response.menu +=  [
                        (T('My Recipes'), False, URL('default', 'my_recipes'), []),
                         (T('New Category'), False, URL('default', 'new_category'), []),
                         (T('New Recipe'), False, URL('default', 'new_recipe'), [])
                    ]
    response.menu +=  [
                      (T('Contact Us'), False, URL('default', 'contactform'), [])
                ]
if DEVELOPMENT_MENU: _()

if "auth" in locals(): auth.wikimenu()
