SNAP_VERSION='0.5'

# default location which to write snapshots
#  (timestamp and 'tgz' extension will be appended)
DEFAULT_SNAPFILE='/tmp/snap-shot.tgz'

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

  'rhel'  :   { 'repos'    : 'syum',
                'packages' : 'syum',
                'files'    : 'syum',
                'services' : 'dispatcher' },

  'centos'  : { 'repos'    : 'syum',
                'packages' : 'syum',
                'files'    : 'syum',
                'services' : 'dispatcher' },

  'ubuntu'  : { 'repos'    : 'sapt',
                'packages' : 'sapt',
                'files'    : 'sapt',
                'services' : 'dispatcher' },

  'debian ' : { 'repos'    : 'sapt',
                'packages' : 'sapt',
                'files'    : 'sapt',
                'services' : 'dispatcher' },


  'gentoo'  : {},
  'apple'   : {},
  'windows' : {}

}
