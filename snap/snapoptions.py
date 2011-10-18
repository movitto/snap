SNAP_VERSION='Snap Version 0.1'

FS_FAILSAFE=False # enable/disable all file creations
PS_FAILSAFE=False # enable/disable package installation

# Default snapfile
DEFAULT_SNAPFILE='/tmp/snapper'

CONFIG_FILE='/etc/snap.conf'
PACKAGE_SYSTEMS_DIR='/usr/share/snap/packagesystems/'

# Enable for alot of debugging output
dbg=False
def debug(message):
   if dbg:
       print 'DEBUG: ' + message
