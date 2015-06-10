#!/bin/bash
cp bpgviewer-thumbnailer /opt/bpgviewer/bin/
chown 0.0 /opt/bpgviewer/bin/bpgviewer-thumbnailer
chmod 755 /opt/bpgviewer/bin/bpgviewer-thumbnailer
cp bpgviewer.thumbnailer /usr/share/thumbnailers/
chown 0.0 /usr/share/thumbnailers/bpgviewer.thumbnailer
chmod 644 /usr/share/thumbnailers/bpgviewer.thumbnailer
cp bpgviewer-thumbnailer.schemas /usr/share/gconf/schemas/
chown 0.0 /usr/share/gconf/schemas/bpgviewer-thumbnailer.schemas
chmod 644 /usr/share/gconf/schemas/bpgviewer-thumbnailer.schemas
