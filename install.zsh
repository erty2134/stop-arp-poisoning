# create dynamic libary for ctypes
gcc -dynamiclib -o libioctl_wrapper.dylib ioctl_wrapper.c

# move folder to /usr/local/opt

# move launcher to /usr/local/bin