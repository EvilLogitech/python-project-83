import page_analyzer.app as myapp
# from page_analyzer.app import app
app = myapp.app
get_h1 = myapp.get_h1
get_description = myapp.get_description
get_title = myapp.get_title

__all__ = ['app', 'get_h1', 'get_description', 'get_title']
