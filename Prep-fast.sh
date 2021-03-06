#!/bin/bash

function qsub_replacer {
    #qname=${PWD//\//_}
    #qname=${qname##*utl0268_}
    qname_1=${PWD##*/}
    PWD_2=${PWD%/*}
    qname_2=${PWD_2##*/}
    PWD_3=${PWD_2%/*}
    qname_3=${PWD_3##*/}
    PWD_4=${PWD_3%/*}
    qname_4=${PWD_4##*/}
    qname="T$qname_4$qname_3$qname_2$qname_1"
    if [[ $(echo $qname | wc -c) > 17 ]]; then
        qname="T$qname_3$qname_2$qname_1"
    fi
    sed -i s/@N@/$qname/g qsub.parallel
    sed -i s%@R@%$PWD%g qsub.parallel
}

mkdir $1 2> /dev/null
cd $1
cp ../INPUT/* .
qsub_replacer
