# Debug
# Debug related tools

from core.conf				import LOG_PREFIX

from libqtile.log_utils 	import logger

def log(msg):
	logger.warning(LOG_PREFIX + " " + msg)