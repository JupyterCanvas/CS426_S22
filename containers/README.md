# Singularity container config
---
## create basic definition file

```bash
mkdir containers && cd containers
vim debian.def
```
```
Bootstrap: library
From: debian:bullseye

%post
    echo "Hello from inside the container"

%runscript
    echo "This is what happens when you run the container..."

```
---
development cycle:
1. create a writable container (sandbox)
2. shell into container with --writable option and tinker with it interactively
3. record changes in definition file
4. rebuild the container from the definition file
5. rinse and repeat until happy
6. rebuild the container from the final definition file as a read-only singularity image format (SIF) image for use in production

