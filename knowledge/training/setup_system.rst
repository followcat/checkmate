System setup
============
Introduction
------------
The workstation must be configured in order to be used in a safe way.

The safety covers:
    fault proof
        Different partitions will be used to map different directories.
    loss safe
        The core of the work environment is understood at the place where the project code, documentation, partial and temporary copies, tar and zip files are stored.
        The core of the work environment will be encrypted so as to be unusable in case of loss or at computer's end of life.
        The core of the work environment is *fully* setup under the user's $HOME.
        The habit is to have the work environment stored at $HOME/Projects/[project_name].
        Consequenty we avoid storing temporary copies of the project code under /tmp or tar and zip files in a non-encrypted removable storage (USB, micro-SD, ...).


Encryption
----------
Prerequisite
............
The following procedure is based on a debian based gnu/linux system (debian, ubuntu).
The system must be installed with at least three different partitions:

    - swap
    - /home
    - /

The /home partition is supposed to be format as an ext4 filesystem.
A root account must be accessible (have a password) so that /home can be unmounted in recovery mode.
Any copy (checkouts, tar files) of TCS is stored under /home.

/home partition will be encrypted by the following procedure.


Procedure
.........
Connect onto a session where you have internet access.
Install following dependencies:

    - ecryptfs-utils
    - cryptsetup

::

    su -
    apt-get install ecryptfs-utils
    apt-get install cryptsetup


Start laptop in recovery mode (no X session) and connect as root

::

    cd /home
    tar cvf ~/home.vcr.tar vcr

    modprobe dm_mod
    mount

-> get the /dev/ corresponding to /home (mine is /dev/sda7, change command according to your output)

::

    umount /dev/sda7
    cryptsetup luksFormat /dev/sda7 -c aes -s 256 -h sha256

-> requires a passphrase (allows space). This passphrase will be asked at each system startup and should be remembered.

::

    cryptsetup luksOpen /dev/sda7 home
    ls /dev/mapper/home
    mke2fs -t ext4 -j /dev/mapper/home -L home
    mount /dev/mapper/home /home
    cd /home
    tar xvf ~/home.vcr.tar

Edit /etc/fstab
Replace:

::

    /dev/sda7    /home    ext4  defaults   0   2

by:

::

    /dev/mapper/home   /home    ext4  rw,errors=remount-ro   0   0

Edit /etc/crypttab
Add line:

::

    home    /dev/sda7    none   luks

Cleanup and restart to check everything is in place:

::

    umount /home
    cryptsetup luksClose /dev/mapper/home

    shutdown -r now


On the prompt "Enter passphrase:", type the passphrase chosen at luksFormat


If you suffer of having to input two password at startup (/home passphrase and your own user password),  you can disable password input by opting for automatic login in login screen.
On gnome desktop, it is available throught the menu

::

    System -> Administration -> Login Screen

Opt in the option:

::

    Log in as _____(user) automatically
