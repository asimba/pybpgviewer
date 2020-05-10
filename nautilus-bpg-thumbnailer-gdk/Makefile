CC = gcc
CFLAGS  = `pkg-config --cflags --libs gdk-pixbuf-2.0` -s -O2 -lm -lbpg

TARGET = bpgviewer-thumbnailer

all: $(TARGET)

$(TARGET): $(TARGET).c ; $(CC) $(TARGET).c $(CFLAGS) -o $(TARGET)

clean: ; $(RM) $(TARGET)
