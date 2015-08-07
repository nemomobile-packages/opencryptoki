if ENABLE_DAEMON
DAEMONDIRS = include sbin
endif

SUBDIRS = lib $(DAEMONDIRS)

install-data-hook:
	$(MKDIR_P) $(DESTDIR)$(lockdir) $(DESTDIR)$(logdir)
