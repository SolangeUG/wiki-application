import os
import jinja2
import webapp2

# os.path.dirname(__file__) returns the string name of the current directory ==> 'sug-blog'
# os.path.join(os.path.dirname(__file__), "../pages") appends 'pages' to the current directory ==> 'sug-blogs/pages'
template_dir = os.path.join(os.path.dirname(__file__), "../pages")
jinja_env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(template_dir),
                autoescape=True)


def format_datetime(value, datetime_format='medium'):
    """
    Return a formatted DateTime value.
    :param value: input value to format
    :param datetime_format: the desired format
    :return: the formatted DateTime value
    """
    if value:
        if datetime_format != 'medium':
            return str(value)
        else:
            return value.strftime('%b %d, %Y - %H:%M')


# add the previously created format to jinja environment filters
jinja_env.filters['datetime'] = format_datetime


class TemplateHandler(webapp2.RequestHandler):
    """
    TemplateHandler inherits from the webapp2.RequestHandler class.
    Its main purpose is to aggregate methods that render a given template,
    with given arguments, to the screen.
    """
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    @staticmethod
    def render_str(template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))