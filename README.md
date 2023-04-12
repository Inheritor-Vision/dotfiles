# Setup Install

# Info

**Source**:

- [ArchLinux Install Guide](https://wiki.archlinux.org/title/installation_guide)
- [DistoTube Arch Install](https://www.youtube.com/watch?v=PQgyW10xD8s)

# For VMs: ISO Install

Process to setup a minimal Arch Linux setup:

>
> Download the ISO via P2P at https://archlinux.org/download/ 
>

```bash

# ----- Keyboard Layout ----- #

loadkeys fr-latin1

# ----- Boot Mode ----- #

# If EFI folder exists, then boot was done with UEFI. Else, it legacy Boot mode.
ls /sys/firmware/efi/efivars

# ----- Internet Connection ----- # 

# Should works out of the box. Use iwctl for WiFi authentication.
ping archlinux.org 

# ----- NTP Server ----- #

# Set the clock
timedatectl set-ntp true

# Check
timedatectl status

# ----- Disk Partitioning ----- #

# Identify disks
fdisk -l
lsblk

# TODO: LLVM, Disk Encryption or RAID

# Required partitions are: root, uefi boot (If Boot mode is UEFI)
fdisk /dev/*disk_to_be_partitioned*

# Useful commands: list partitions (p), list free space (F), list Partition type (l), add new partition (n), change partition type (t), write & exit (w), quit (q)
# Create GPT table for UEFI boot
g
# Create DOS table for DOS boot
o

# TODO: SWAP partition (useless except for high end SSD for low memory PC), /home partition (for distro hopping / easy backup)
# **/!\ CAUTION /!\**: Static partitions have to be place last. Root partition (or partition taking most of the space) HAS TO BE the first partition, in case you want to create a new partition, saving the copy

# New & Only Root Partition
n
p
1
default
default

# Write to disk
w

# Check
fdisk -l

# ----- Formatting & Mount ----- #

# Format Root

mkfs.ext4 /dev/sda1

# Mount Root

mount /dev/sda1 /mnt

# ----- Install minimal Arch ----- # 

pacstrap /mnt base linux linux-firmware

# ----- Configure Linux ----- #

genfstab -U /mnt >> /mnt/etc/fstab

# ----- Into the VM ----- #

arch-chroot /mnt
pacman -S neovim networkmanager sudo os-prober mtools grub

# DOS boot
pacman -S dosfstools

# UEFI Boot
pacman -S efibootmgr

# ----- Time Zone ----- #

ls -sf /user/share/zoneinfo/Europe/Paris /etc/localtime
hwclock --systohc

# ---- Localization ----- #

vim /etc/locale.gen # Uncomment fr_FR.UTF-8 UTF-8 & en_US.UTF-8
locale-gen
vim /etc/locale.conf # Create & add LANG=en_US.UTF-8
vim /etc/vconsole.conf # Create & add KEYMAP=fr-latin1

# ----- Network ----- #

vim /etc/hostname # Modify hostname
vim /etc/hosts # Append :
# 127.0.0.1	localhost
# ::1		localhost
# 127.0.1.1	myhostname.localdomain	myhostname 
systemctl enable NetworkManager

# ----- Users ----- #

# Root passws
passwd

# Create Sudo user
useradd -m vision
passwd vision
usermod -aG wheel,audio,video,optical,storage vision
EDITOR=nvim visudo # Uncomment sudo for wheel group

# ----- Mount EFI -----#

# Only for UEFI Boot
fdisk -l
mkdir /boot/EFIq
mkdir /boot/EFI /dev/*sda_EFI*

# ----- GRUB ----- #
# DOS Boot
grub-install --target=i386-pc /dev/*sdX_disk* --recheck # Care, sdX is a disk, not a partition

# UEFI Boot
grub-install --target=x86_64-efi --efi-directory=*mount_of_EFI* --bootloader-id=GRUB --recheck

# Generate configuration
grub-mkconfig -o /boot/grub/grub.cfg

# ----- GG WP ----- #
exit
umount /mnt # -l
shutdown now
# Remove ISO

```

# Optional

##  Grub Theme

Grub theme used is [minefield](https://github.com/Lxtharia/minegrub-theme).

Add the following entry to `/etc/grub.d/40_custom` with this inputs:
- Find UEFI Windows partition with `sudo os-prober`
- fs_uuid: `sudo grub-probe -t fs_uuid -d /dev/*partition*`
- hints_string: `sudo grub-probe -t hints_string -d /dev/*partition*`

```grub
if [ "${grub_platform}" == "efi" ]; then
	menuentry "Windows" {
		insmod part_gpt
		insmod fat
		insmod chain
		search --no-floppy --fs-uuid --set=root *hints_string* *fs_uuid*
		chainloader /EFI/Microsoft/Boot/bootmgfw.efi
	}
fi
```

## VMs

- xinitrc: wallpaper, minefield text cycle, screens
.........
