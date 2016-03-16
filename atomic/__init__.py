# -*- coding: utf-8 -*-
__atomic_version__ = (0, 2, 0)                  # atomic VERSION NUMBER
__version__ = '.'.join((str(v) for v in __atomic_version__))


from exa import _conf
from exa.relational import Isotope, Length, Energy, Time, Amount, Constant


from atomic import tests
from atomic.universe import Universe

#from atomic.universe import Universe            # atomic imports
#from atomic.cube import read_cubes
#from atomic.xyz import read_xyz
#from atomic import algorithms
#from atomic.formula import SimpleFormula
#
#if Config._temp:
#    from exa.install import install_notebook_widgets
#    from exa.relational import create_all
#    from atomic.install import update_config
#    update_config()
#    create_all()
#    install_notebook_widgets(Config.atomic['nbext'], Config.atomic['extensions'])
#
