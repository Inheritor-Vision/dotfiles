#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

# Append to history file, don't overwrite it
shopt -s histappend

# for setting history length see HISTSIZE and HISTFILESIZE in bash(1)
HISTSIZE=1000
HISTFILESIZE=2000

# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS.
#shopt -s checkwinsize

#if [ -z "${debian_chroot:-}" ] && [ -r /etc/debian_chroot ]; then
#	    debian_chroot=$(cat /etc/debian_chroot)
#fi

# ----- PATH ----- #

PATH=$PATH:/home/vision/.local/bin

# ----- ALIAS ----- # 

alias ls='ls --color=auto'
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'
alias diff='diff --color=auto'
alias ip='ip --color=auto'

alias ll='ls -lA'
alias l='ls -CF'

alias git-config='/usr/bin/git --git-dir=/home/vision/.dotfiles --work-tree=/home/vision'

#PS1='[\u@\h \W]\$ '

gray='\e[1;37m'
cyan='\e[1;36m'
light_cyan='\e[1;96m'
reset='\e[0m'

# ----- Prompt ----- #

# Careful, enclose ANSI color with \[ \]
#PS1='[\u@\h \W]\$ \[$(printf "\x1b[38;2;255;100;250m\]A lovely shade of pink\[\x1b[0m")\]'
PS1='\['$light_cyan'\]┌──(\['$cyan'\]\u@\h\['$light_cyan'\])-[\['$reset'\]\W\['$light_cyan'\]]\n\['$light_cyan'\]└─\['$cyan'\]\$ \['$reset'\]'

export EDITOR=vim
export SELDON='/mnt/data/Encyclopedia Galactica'
