CC = gcc
CFLAGS  = -s -O3 -fPIC -shared -Wl,-soname,libbpgdec.so.0 -lbpg

TARGET = libbpgdec

all: $(TARGET)

$(TARGET): $(TARGET).c ; $(CC) $(TARGET).c $(CFLAGS) -o $(TARGET).so

clean: ; $(RM) $(TARGET)
