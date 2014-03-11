all:
	mkdir -pv locale/en_US/LC_MESSAGES
	mkdir -pv locale/zh_CN/LC_MESSAGES
	msgfmt -o locale/en_US/LC_MESSAGES/checkmate.mo steps_en.po
	msgfmt -o locale/zh_CN/LC_MESSAGES/checkmate.mo steps_cn.po
clean:
	-rm -r locale/
