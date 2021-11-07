version_info='2.9.4 beta4'
update_info='20211107'

import os, sys, getopt, shutil

title_text='[GitHub Desktop Translator zh_CN] (ver '+version_info+')'
title_text='='*len(title_text)+'\n'+title_text+'\n'+'='*len(title_text)

version_text=title_text+'''
GitHub Desktop translation '''+version_info+'''
  --by Zetaspace '''+update_info+'''

link: github.com/ZetaSp/GHDTranslator.py

Thank you for using!
'''

helpo_text='''
Usage: '''+os.path.split(sys.argv[0])[1]+''' -d <app folder>

-d --dir <dir>    Target dir, GHD app folder like 'app-2.8.4'
-r --restore      Restore from auto-backup file, using with --dir
-c --check_update Check for updates from github (mirror fastgit)
-h --help         Show this message
-v --version      Show version info
'''
help_text=title_text+helpo_text

error_text=lambda what:title_text+'\n'+what+'\n'+helpo_text

def check_update():
    print(title_text)
    print('Checking for updates...\n')
    import requests
    # Not using GitHub API, because I'm always "rate limited"...
    # Using raw version.json instead.
    #api='https://raw.githubusercontent.com/ZetaSp/GHDTranslator.py/main/version.json'    
    # Githubusercontent.com is unreachable in China; using mirror fastgit.org.
    api='https://raw.fastgit.org/ZetaSp/GHDTranslator.py/main/version.json'

    print('Current: ver '+version_info+' update '+update_info)
    req=requests.get(api).json()
    version=req['version']
    update=req['update']
    
    print('Newest:  ver '+version+' update '+update+'\n')
    if update_info==update:
        print('You are using the newest version!')
        sys.exit(0)
    else:
        print('New version('+update+') available!')
        print('===> https://github.com/ZetaSp/GHDTranslator.py')
        sys.exit(1)

# Get cmdline args
if sys.argv[1:]==[]:print(error_text('No options.'));sys.exit(1)
try:
    opts,args=getopt.getopt(sys.argv[1:],'hvd:rc',['help','version','dir=','restore','check_update'])
except getopt.GetoptError:
    print(error_text('Unknown options.')) # Unknown args
    sys.exit(1)

restore=False
appdir=''
exist=os.path.exists
copy=shutil.copy2
for opt,arg in opts:
    if opt in ('-h','--help'):
        print(help_text)
        sys.exit(0)
    elif opt in ('-v','--version'):
        print(version_text)
        sys.exit(0)
    elif opt in ('-c','--check_update'):
        check_update()
        sys.exit(0)
    elif opt in ('-r','--restore'):
        restore=True
    elif opt in ('-d','--dir'):
        appdir=arg
if appdir=='':
    print(error_text('Dir needed.'))  # Blank target dir
    sys.exit(0)
if not type(appdir)is str:
    print(error_text('Error dir: '+str(appdir)))    # Not str
    sys.exit(0)
if(appdir[0]=="'"and appdir[-1]=="'")or(appdir[0]=='"'and appdir[-1]=='"'):
    appdir=appdir[1:-1] # Cut '...'
if not exist(os.path.abspath(appdir)+'\\resources\\app'):
    print(error_text('Not exist dir: '+appdir))  # Not exist target dir
    sys.exit(0)

# Basically Verified
appdir=os.path.abspath(appdir+'\\resources\\app')
resdir=os.path.abspath(os.getcwd())
jsdir0=appdir+'\\main.js'
jsdir1=appdir+'\\renderer.js'
jsdir0b=jsdir0+'.bak'
jsdir1b=jsdir1+'.bak'
extra=['\\static\\cherry-pick-intro.png']
if restore: # Restore
    if not(exist(jsdir0b)and exist(jsdir1b)):
        print(error_text("Can't find js files to restore."))    # Not the right target dir
    else:
        # Verified, Restore
        print(title_text+'\nRestore files.\n')
        print('Restoring main.js, renderer.js...')
        copy(jsdir0b,jsdir0)
        copy(jsdir1b,jsdir1)
        print('Restoring extra files...')
        for f in extra:
            print('  '+f)
            copy(appdir+f+'.bak',appdir+f)
        print('Restore finished.')
else:   # Patch
    if not(exist(jsdir0)and exist(jsdir1)):
        print(error_text("Can't find js files to patch."))  # Not the right target dir
    else:
        if sum(map(lambda f:int(not exist(resdir+f)),extra))!=0:
            resdir=os.path.abspath(os.path.split(sys.argv[0])[0])   # Can't find in current dir,
        if sum(map(lambda f:int(not exist(resdir+f)),extra))!=0:    # Try py file dir
            print(error_text("Can't find extra resources."))    # Can't find resources
        else:
            # Verified, Patch
            print(title_text+'\nPatch files.\n')
            print('Target dir: '+appdir+'\nResource dir: '+resdir)
            print('\nBackuping...')   # Backup
            if not exist(jsdir0b):
                print('  \\main.js ==> bak')
                copy(jsdir0,jsdir0b)
            if not exist(jsdir1b):
                print('  \\renderer.js ==> bak')
                copy(jsdir1,jsdir1b)
            for f in extra:
                if not exist(appdir+f+'.bak'):
                    print('  '+f+' ==> bak')
                    copy(appdir+f,appdir+f+'.bak')
            print('\nRestoring...')   # Restore all
            print('  \\main.js <== bak')
            copy(jsdir0b,jsdir0)
            print('  \\renderer.js <== bak')
            copy(jsdir1b,jsdir1)
            for f in extra:
                print('  '+f+' <== bak')
                copy(appdir+f+'.bak',appdir+f)
            print('\nPatch start.\nCopying extra files...') # Copy extra files
            for f in extra:
                print('  '+f+' <== Translated')
                copy(resdir+f,appdir+f)
            print('Translating js...')    # Patch js
            js=['','']
            with open(jsdir0,'r',encoding='utf-8')as j:js[0]=j.read()
            with open(jsdir1,'r',encoding='utf-8')as j:js[1]=j.read()
            import re
            tar=(0,1)
            def sub(mode):
                global tar,js
                if mode=='m':   # main.js
                    tar=(0,1)
                elif mode=='r': # renderer.js
                    tar=(1,2)
                elif mode=='a': # all
                    tar=(0,2)
                else:
                    m,n=mode.split('>')
                    if'&'in m:  # &File --> 文件(&F)
                        n+='(&'+m[m.index('&')+1].upper()a+')'
                    if'...'in m:
                        n+='...'
                    if not('\\'in m or'*'in m or'?'in m):
                        for i in js[tar[0]:tar[1]]:
                            i.replace(m,n)
                    else:
                        for i in js[tar[0]:tar[1]]:
                            i=re.sub(m,n,i)
            sub('&File>文件')
            sub('')

            print('meow')

# EOF
sys.exit(0)
