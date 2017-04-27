#!/bin/bash
FILE=test

printf "\e[1m\n\ntransforming xml file\n=====================\n\n\e[0m"
java -jar saxon.jar -o ${FILE}.fo ${FILE}.xml DocBook/xsl/docbook-xsl-ns-1.79.1/fo/docbook.xsl

printf "\e[1m\n\noptimizing fo file\n==================\n\n\e[0m"
python ../fo-block-optimizer/fo-block-optimizer.py -i ${FILE}.fo -o ${FILE}_opt.fo

printf "\e[1m\n\nprocessing fo file\n==================\n\n\e[0m"
java -jar fop.jar -c ../cfg.xml -fo ../${FILE}.fo -pdf ../${FILE}.pdf

printf "\e[1m\n\nprocessing optimized fo file\n=============================\n\n\e[0m"
java -jar fop.jar -c ../cfg.xml -fo ../${FILE}_opt.fo -pdf ../${FILE}_opt.pdf