install:
	rm -f $(HOME)/bin/amaburn1.sh
	ln -s $(PWD)/amaburn1.sh $(HOME)/bin/
	touch pb_mem pb_cpu
