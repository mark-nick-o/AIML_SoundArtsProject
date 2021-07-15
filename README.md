# AIML_SoundArtsProject
SAAI Factory - Hackathon on Art and AI

WIP
====
The idea is that the videos and music are loaded to the re-direct server and that a json file is created when this is loaded, this json file contains which keywords relate to each item loaded into the server, a chatbot client and a speach recognition client then recognises the request by reading the json file and the keywords associated with each item then randomly selecting each one to be played from the cloud storage. Each video and sound has been made with different packages and instruments and methods to give various effects, the themes of these visuals are also given as a keyword method of selection, there is also a pathway into an old interactive java/javascript sound visual arts games world if you are able to run unsigned java applets and javascript.
you can communicate via the @blueSparrow_bot http://t.me/blueSparrow_bot

if you start the google colab you can experiment by sending the bot commands via the blueSparrow messanger once you have came to the end of the spreadsheet, I will hope to host this application and some more before the end of the project but it is possible during test to example the machine learning and test out the applications.

to run the rest server you need to install the libraries or use the binary (which has been made for ubuntu linux) then make the executable

compile
=======
command #> g++-7 -std=c++17 webserver_rest2.cpp -o webserver_rest2 -lhttpserver

run
======
command #>  ./webserver_rest2

load a single file for test
===========================
command #> ./rest_server_test.sh https://soundcloud.com/ringroserecords/in2u

(very shortly a loader will be provided that loads all the files that make up the arts project and this will correspond to the json file or BOT_CONFIG provided) 
