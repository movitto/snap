# package registry, used to convert packages installed on one os to another
#
# (C) Copyright 2011 Mo Morsi (mo@morsi.org)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License, Version 3,
# as published by the Free Software Foundation
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.


class PackageRegistry:
    PACKAGE_REGISTRY = {
      'mysql-server' : { 'yum' : 'mysql-server',
                         'apt' : 'mysql-server' },
    
      'mysql-client' : { 'yum' : 'mysql',
                         'apt' : 'mysql-client' },
    
      'postgresql-server' : { 'yum' : 'postgresql-server',
                              'apt' : 'postgresql' },
    
      'postgresql-client' : { 'yum' : 'postgresql',
                              'apt' : 'postgresql-client' },
    
      'httpd' : { 'yum' : 'postgresql',
                  'apt' : 'postgresql-client' }
    }

    PACKAGE_SYSTEM_REGISTRY = { 'yum' : {}, 'apt' : {} }
    for pkg in PACKAGE_REGISTRY:
        PACKAGE_SYSTEM_REGISTRY['yum'][PACKAGE_REGISTRY[pkg]['yum']] = pkg

    def encode(package_system, package):
        if package in PackageRegistry.PACKAGE_SYSTEM_REGISTRY[package_system]:
            return PackageRegistry.PACKAGE_SYSTEM_REGISTRY[package_system][package]
        return package
    encode=staticmethod(encode)

    def decode(package_system, package):
        if package in PackageRegistry.PACKAGE_REGISTRY:
            return PackageRegistry.PACKAGE_REGISTRY[package][package_system]
        return package
    decode=staticmethod(decode)
