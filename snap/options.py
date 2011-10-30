SNAP_VERSION='0.5'

# default location which to write snapshots
#  (timestamp and 'tgz' extension will be appended)
DEFAULT_SNAPFILE='/tmp/snap'

# locations which to load snap! configuration from
CONFIG_FILES=['/etc/snap.conf', '~/.snap']

# a mapping of targets to default backends
# on a per-os basis
DEFAULT_BACKENDS = {
  'mock'    : { 'repos'    : 'mock',
                'packages' : 'mock',
                'files'    : 'mock',
                'services' : 'mock' },

  'fedora'  : { 'repos'    : 'syum',
                'packages' : 'syum',
                'files'    : 'syum',
                'services' : 'dispatcher' },

  'ubuntu'  : {},
  'gentoo'  : {},
  'apple'   : {},
  'windows' : {}

}
