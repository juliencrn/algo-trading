#
# Jupyter notebook configuration file
#
c = get_config()

# SSL
c.NotebookApp.certfile = u'/root/.jupyter/mycert.pem'
c.NotebookApp.keyfile = u'/root/.jupyter/mykey.key'

# IP Address and port
# set IP to "*" to bind to all IP addresses of the cloud instance
c.NotebookApp.ip = '0.0.0.0'
c.NotebookApp.port = '8888'

# options
c.NotebookApp.open_browser = False
c.NotebookApp.allow_root = True
