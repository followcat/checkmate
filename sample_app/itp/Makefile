all:
	xgettext -o ref.pot steps.py --from-code=utf-8
	msgmerge -o tmp_en.po steps_en.po ref.pot
	msgmerge -o tmp_cn.po steps_cn.po ref.pot
	@echo .po file generated. Now you need to edit the translation in tmp*.po files to be right if steps changed in steps.py. If not, move on.
	@echo And then run "make install" to compile the .po files into .mo files.
install:
	mkdir -pv locale/en_US/LC_MESSAGES
	mkdir -pv locale/zh_CN/LC_MESSAGES
	msgfmt -o locale/en_US/LC_MESSAGES/checkmate.mo tmp_en.po
	msgfmt -o locale/zh_CN/LC_MESSAGES/checkmate.mo tmp_cn.po
	@echo Compilation done.
clean:
	-rm -r locale/
	-rm tmp*.po ref.pot
