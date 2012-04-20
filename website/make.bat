@echo off

IF "%1"=="run"   GOTO run
IF "%1"=="setup" GOTO setup
IF "%1"=="clean" GOTO clean
GOTO help

:help
echo Usage: make 'target', where target is
echo  setup         -- setup python egg
echo  test          -- run all nosetests
echo  blank-db      -- create a blank database
echo  run           -- run the site in development mode
echo  clean         -- reset the folder to clean git checkout (removes virtual python env)
GOTO end

:run
pserve development.ini --reload
GOTO end

:setup
python setup.py develop
REM populate_KaraKara development.ini
GOTO end

:clean
rmdir *.egg-info /S /Q
GOTO end

:end
