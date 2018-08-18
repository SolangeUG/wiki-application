import handler.handler as handler


class WikiHandler(handler.TemplateHandler):
    """
    WikiHandler inherits from the hander.TemplateHandler class.
    It aggregates functionalities for creating, editing and retrieving wiki articles, using the GAE Datastore.
    """
    def get(self):
        # TODO: add logic to retrieve articles
        articles = []
        self.render("wiki.html", articles=articles)
