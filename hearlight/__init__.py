from .css import css

import IPython

IPython.get_ipython()

from ipywidgets import HTML

display(HTML(value=css))
