#------------------------------------------------------

LANG = en_US zh_CN

DOMAIN = checkmate-features

PY_SRCS = $(shell ls [A-Za-z]*.py)

GETTEXT = xgettext --from-code=utf-8

POT_FILE = $(DOMAIN).pot

PO_FILES = $(foreach lang, $(LANG), po/$(lang).po)
MO_FILES = $(foreach lang, $(LANG), translations/$(lang)/LC_MESSAGES/$(DOMAIN).mo)

RIGHT_HOLDER  = "willendare"
E_MAIL = "vincent.croisier@willendare.com"
VERSION = "0.0.4"
PACKAGE = "checkmate features"

GETTEXT_OPT = --language=Python --package-name=$(PACKAGE) \
              --package-version=$(VERSION) \
              --msgid-bugs-address=$(E_MAIL) \
              --copyright-holder=$(RIGHT_HOLDER)

#------------------------------------------------------

all: $(MO_FILES)
	@echo Compilation done.

$(POT_FILE):
	@$(GETTEXT) -o $(POT_FILE) $(GETTEXT_OPT) steps.py

po/%.tmp.po: po/%.po $(POT_FILE)
	@msgmerge -o $@ $< $(POT_FILE)

translations/%/LC_MESSAGES/$(DOMAIN).mo: po/%.tmp.po
	mkdir -p $(subst $(DOMAIN).mo, ,$@)
	msgfmt -o $@ $(filter po%, $^)

#------------------------------------------------------

clean:
	@rm -Rf translations/
	@rm -f $(POT_FILE)

