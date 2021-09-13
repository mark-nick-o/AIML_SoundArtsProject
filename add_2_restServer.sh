:
#
# Script to add all the urls confgiured to the rest webserver
#
# for debug uncomment :: set -x
#
FHOME=/home/mark
ADD2SERVER=./rest_server.sh
[ $# == 1 ] && [ "$1" == "DEL" ] && [ -f $FHOME/urls_added ] && rm $FHOME/urls_added 
touch $FHOME/urls_added
[ $# == 1 ] && [ "$1" == "DEL" ] && [ -f $FHOME/urls_errors ] && rm $FHOME/urls_errors
touch $FHOME/urls_errors
field=0
JSON_FILE=$FHOME/AIML_BOT.json
REDIR_BOT_JFILE=$FHOME/REDIR_BOT.json
touch $REDIR_BOT_JFILE
for line in `cat $FHOME/url_defs`
do
  if [ "$field" == 1 ]
  then
    url=$line
    reply=`$ADD2SERVER $url`
    numb=`echo $reply | awk '{ print $1}'`
    if [ "$numb" == -1 ]
    then
      echo "$url malformed ERROR" >> $FHOME/urls_errors
    else
      echo "$tags , $url , $numb" >> $FHOME/urls_added
      # create a new bot file for use with redirection script
      sed 's/$url/$numb/g' $JSON_FILE >> $REDIR_BOT_JFILE
    fi
   elif [ "$field" == 0 ]
   then
     tags=$line
   fi
   field=`expr $field + 1`
   field=`expr $field % 2`
done
