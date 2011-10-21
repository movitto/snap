SNAP_VERSION='0.5'

DEFAULT_SNAPFILE='/tmp/snap-shot'

CONFIG_FILES=['/etc/snap.conf', '~/.snap']

# a mapping of targets to default backends
# on a per-os basis
DEFAULT_BACKENDS = {
  'fedora'  => { 'repos'     => 'yum',
                 'packages', => 'yum',
                 'files',    => 'yum' },
  'ubuntu'  => {},
  'gentoo'  => {},
  'apple'   => {},
  'windows' =>

}
