try:
  import json
except ImportError:
  try:
    from django.utils import simplejson as json
  except ImportError:
    import simplejson as json