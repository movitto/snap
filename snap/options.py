SNAP_VERSION = '0.6'

# locations which to load snap! configuration from
CONFIG_FILES = ['/etc/snap.conf', '~/.snap',
                'C:\\Program Files\\snap\\snap.conf', 'C:\\Program Files (x86)\\snap\\snap.conf']

# a mapping of targets to default backends
# on a per-os basis
DEFAULT_BACKENDS = {
    'mock'    : { 'repos'    : 'mock',
                  'packages' : 'mock',
                  'files'    : 'mock',
                  'services' : 'mock' },

    'mock_windows' :
                { 'repos'    : 'mock',
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
    'windows' : {  'repos'    : 'disabled',
                   'packages' : 'win',
                   'files'    : 'win',
                   'services' : 'dispatcher'  }

}
