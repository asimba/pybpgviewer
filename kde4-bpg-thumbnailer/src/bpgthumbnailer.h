/*
Copyright (c) 2015 Alexey Simbarsky <asimbarsky@gmail.com>
This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of
the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public
License along with this program; if not, write to the Free
Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
Boston, MA 02110-1301, USA.
*/

#ifndef _BPG_THUMBNAILER_H_
#define _BPG_THUMBNAILER_H_

#include <QObject>
#include <kio/thumbcreator.h>

class BPGThumbnailer:public QObject,public ThumbCreator{
    Q_OBJECT
    public:
        BPGThumbnailer();
        virtual ~BPGThumbnailer();
        virtual bool create(const QString &path,int w,int h,QImage &img);
        virtual Flags flags() const;
};

#endif
