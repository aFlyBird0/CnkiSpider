#!/bin/sh
# 生成必要的target，result等文件夹
if [ ! -d "target"  ];then
  mkdir "target"
fi

if [ ! -d "result"  ];then
  mkdir "result"
fi

if [ ! -d "html"  ];then
  mkdir "html"
fi

if [ ! -d "log"  ];then
  mkdir "log"
fi

if [ ! -d "error"  ];then
  mkdir "error"
fi

if [ ! -d "author"  ];then
  mkdir "author"
fi

if [ ! -d "author_output"  ];then
  mkdir "author_output"
fi