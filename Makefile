CONFIGS := mrk421 mrk501

all clean: $(CONFIGS)

$(CONFIGS)::
	CONFIG_DIR=$(realpath $@) $(MAKE) -C lst-agn-analysis
