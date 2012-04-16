# Snap! output formatter
#
# (C) Copyright 2012 Mo Morsi (mo@morsi.org)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License, Version 3,
# as published by the Free Software Foundation
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import config, callback
from snap.metadata.snapfile import SnapFile
from snap.metadata.tdl      import TDLFile
from snap.exceptions        import InvalidOperationError

class OutputFormatter:
  @classmethod
  def create(cls, output_format, **args):
    outfile = args['outfile']
    snapdir = args['snapdirectory']
    encryption_password = args['encryption_password']

    if output_format == "snapfile":
      SnapFile(snapfile=outfile,
               snapdirectory=snapdir,
               encryption_password=encryption_password).compress()
    elif output_format == "tdl":
      TDLFile(tdlfile=outfile,
              snapdirectory=snapdir).write()

  @classmethod
  def retrieve(cls, output_format, **args):
    infile = args['infile']
    snapdir = args['snapdirectory']
    encryption_password = args['encryption_password']

    if output_format == "snapfile":
      SnapFile(snapfile=infile,
               snapdirectory=snapdir,
               encryption_password=encryption_password).extract()
    elif output_format == "tdl":
      raise InvalidOperationError("cannot use snap to restore tdls")
