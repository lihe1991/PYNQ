# Set up some environment variables as /etc/environment
# isn't sourced in chroot

export PATH=/opt/python3.6/bin:$PATH
export BOARD=Pynq-Z1
export HOME=/root
export PYNQ_PYTHON=python3.6

cd /home/xilinx
mkdir scripts
mkdir jupyter_notebooks
mkdir docs
mkdir jupyter_notebooks/slides
mv /root/reveal.js jupyter_notebooks/slides

ln -s /opt/python3.6/lib/python3.6/site-packages/pynq pynq

make -f pynq_git/scripts/linux/makefile.pynq update_pynq
make -f pynq_git/scripts/linux/makefile.pynq new_pynq_update
old_hostname=$(hostname)
pynq_git/scripts/linux/hostname.sh
hostname $old_hostname
rm -rf pynq_git
rm -rf docs

cd /root

chown xilinx:xilinx /home/xilinx/REVISION
