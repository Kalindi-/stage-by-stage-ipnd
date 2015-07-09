# stage 5, 
# a little memory game, 
# made visually up in stage 4, 
# implemented the gameplay in javascript in stage 5

import os
import webapp2
import jinja2
import random
import time
import json

from google.appengine.ext import ndb

#initializing work environment: the file, and the jinja

template_dir = os.path.join(os.path.dirname(__file__), "templates")
template_loader = jinja2.FileSystemLoader(template_dir)
template_env = jinja2.Environment(loader = template_loader, autoescape = True)

# uploading data for the game
game_data = json.load(open('game.json'))

# page making handler

class Handler(webapp2.RequestHandler):
    """contains the basic methods for rendering the templates into html pages"""

    def write(self, *arguments, **key_word_dictionary):    
        """makes a html page out of the inputs"""
        self.response.out.write(*arguments, **key_word_dictionary)

    def render_str(self, template, **parameters): 
    # why here paramenters, and in the other cases i call it key_word_dicitionary
        """makes a string out of the inputs"""
        t = template_env.get_template(template)
        return t.render(parameters)

    def render(self, template, **key_word_dictionary):
        """takes template to fill it in with the keywords"""
        self.write(self.render_str(template, **key_word_dictionary))


#the different simple pages

class FrontPage(Handler):
    "makes my page up, using a template I provide"
    def get(self):
        self.render("front_page.html")

class TermPage1(Handler):
    "makes my page up, using a template I provide"   
    def get(self):
        self.render("game_to_be.html", game_dict=add_random(game_data[2]), title = " - Terms 1 game" )

class TermPage2(Handler):
    "makes my page up, using a template I provide"   
    def get(self):
        self.render("game_to_be.html", game_dict=add_random(game_data[1]), title = " - Terms 2 game")

class TermPage3(Handler):
    "makes my page up, using a template I provide"   
    def get(self):
        self.render("game_to_be.html", game_dict=add_random(game_data[0]), title = " - game about Javascript")
    # does each page have to have its own class? i mean terms1 and terms2 are the same except for the different input
    # is there a way to do this?

class InputPage(Handler):
    def get(self):
        self.render("inputs.html")

    def post(self):
        self.redirect('/game_to_be')


# the pages that are to be made with user input / datastore
class Box(ndb.Model):
    """object made of user inputs """
    term = ndb.StringProperty()
    definition = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

class Page(Handler):
    def get(self):
        """retrieve objects, and create page digestable content"""
        #retrieve all instances of object in date-order
        query = Box.query().order(Box.date)

        # create a dictionary of terms and definitions to pass them into the page template
        game_dict = {}
        for idea in query:
            term = idea.term
            definition = idea.definition

            game_dict[term] = definition

        self.render('game_to_be.html', game_dict=add_random(game_dict), title=" - round of inputs game")

    def post(self):
        """retrieve input data and create instances of object"""

        term = self.request.get('term')
        definition = self.request.get('definition')

        if term and definition and term.isspace() == False and definition.isspace() == False:
            picture = Box(term=term, definition=definition)
            picture.put()
            little_delay()
            self.redirect('/game_to_be')
        else:
            self.render('inputs.html', error=True, term=term, definition=definition)

def little_delay():
    """databases need a moment to update, if no delay, the redirection 
       does not show the most recent input"""
    time_to_update = .1
    time.sleep(time_to_update)


# create a list of random numbers to be attached to each couple of definition and term to scatter them around the page
def add_random(dictionary):
    """ makes sure pairs are recognizeable and adds randomnes to the dictionaries of terms : definitions and"""
    game_dict = dict(dictionary)

    n_terms = 0
    for key in game_dict.keys():
        n_terms +=1

    order_nums = []            
    for n in range(0, n_terms*2):
         order_nums.append(n)

    card_nums = list(order_nums)
    random.shuffle(order_nums)
    
    for key,value in game_dict.items():
        game_dict[key] = [value, order_nums[0], order_nums[1], card_nums[0], card_nums[1]]
        order_nums = order_nums[2:]
        card_nums = card_nums[2:]

    return game_dict


#creation of pages
app = webapp2.WSGIApplication([('/', FrontPage),
                               ('/terms1', TermPage1),
                               ('/terms2', TermPage2),
                               ('/terms3', TermPage3),
                               ('/inputs', InputPage),
                               ('/game_to_be',Page)],
                              debug = True)

