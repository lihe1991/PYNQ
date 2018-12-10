PYNQ and PetaLinux
==================

The PYNQ environment is primarily designed to run inside of a Ubuntu-based
filesystem with the kernel being provided by PetaLinux. This is the flow which
the sdbuild directory supports. It is possible, however, to install PYNQ inside
of a PetaLinux root filesystem with the following caveats:

 1) No overlays will be installed
 2) Jupyter is not supported - only the PYNQ library
 3) Parts of logictools require libraries not available in PetaLinux 

The rest of this guide describes how to configure a PetaLinux project to
include PYNQ. It is specific to version 2018.2.

Add the required layers
-----------------------

Clone the OpenEmbedded repositories - we need some packages that aren't
included in the PetaLinux. We also need to check out the correct version

```
    git clone git://git.openembedded.org/meta-openembedded
    cd meta-openembedded
    git checkout rocko
```

Now we can run `petalinux-config` in the PetaLinux project and add two new user layers  

 1) This directory
 2) meta-openembdedded/meta-python

Add PYNQ to the filesystem target
---------------------------------

Edit `project-spec/meta-user/recipes-core/images/petalinux-image.bbappend` and
add the following line  

```
    IMAGE_INSTALL_append = " python3-pynq"
```

Next run `petalinux-config -c rootfs` and you will find the option to select
`python3-pynq` under `user packages`. Select it to add it to the filesystem

Build the filesystem
--------------------

run `petalinux-build` to build all of the components
run `petalinux-pacakge --boot --u-boot --fpga` to create `BOOT.BIN`

