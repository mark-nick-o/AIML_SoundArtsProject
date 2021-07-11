// Rest Webserver : 
//
// install dependancy library first
// gunzip libmicrohttpd-0.9.68.tar.gz 
// tar -xvzf libmicrohttpd-0.9.68.tar
// cd libmicrohttpd-0.9.68
// mkdir build
// cd build
// ../configure
// make
// sudo make install
//
// unzip libhttpserver-master.zip
// cd libhttpserver-master
// ./bootstrap
// mkdir build
// cd build
// ./../configure CXX='g++-7'
// make 
// sudo make install
//
// export LD_LIBRARY_PATH=/usr/local/lib
//
// compiles with 
// g++-7 -std=c++17 webserver_rest.cpp -o webserver_rest -lhttpserver
//
// Ref Lecture :: OTUS.ru by Marat Seifullin
//
#include <httpserver.hpp>
#include <iostream>
#include <string>
#include <regex>
#include <mutex>
#include <unordered_map>

// define the colors
#define RED "\033[31m"
#define GREEN "\033[32m"
#define YELLOW "\033[33m"
#define BLUE "\033[34m"
#define WHITE "\033[37m"

//#define SINGLE_URL

using namespace std;

std::unordered_map<int, std::string> redirectUrls;
std::mutex mtx;
int g_counter = 0;

std::string savedUrl;
regex pattern(".*http:.*"); 
regex pattern2(".*https:.*"); 

class Save_resource: public httpserver::http_resource {
public:
    //const http_response render POST(const http_request& req)
    const std::shared_ptr<httpserver::http_response> render_POST(const httpserver::http_request& req)
    {
        std::cout << GREEN << std::endl << "save resource::render " << std::endl;
        std::string body = req.get_content();
        std::string response_text;

        if ((regex_match(body, pattern)) or (regex_match(body, pattern2))) {
            std::cout << YELLOW << "POST = " << BLUE << body << std::endl;
#if defined(SINGLE_URL)
            savedUrl = body;
            response_text = " redirect " + savedUrl + "\n";
#else
            int currentNumber = ++g_counter;
            mtx.lock();
            redirectUrls[currentNumber] = body;
            mtx.unlock();
            response_text = to_string(currentNumber) + " redirect " + body + "\n";
            std::cout << YELLOW << "ID = " << BLUE << currentNumber << std::endl;
#endif
        } else {
            std::cout << RED << "Error with url supplied " << std::endl;
            response_text = "-1 redirect fail wrong url format must start http: \n";
        }

        httpserver::string_response* response = new httpserver::string_response(response_text, 200);
        std::cout << RED << "save_resource::render " << std::endl;
        return std::shared_ptr<httpserver::http_response>(response);
    }
    
};

class Redirect_resource: public httpserver::http_resource {
public:
    //const http_response render GET(const httpserver::http_request& req) {
    const std::shared_ptr<httpserver::http_response> render_GET(const httpserver::http_request& req) {
        std::cout << GREEN << std::endl << "resource render " << std::endl;
#if defined(SINGLE_URL)
       httpserver::string_response* response = new httpserver::string_response("",302);
       response->with_header("Location",savedUrl);
       std::cout << RED << "redirect resource render " << savedUrl << std::endl;
#else
        std::string value = req.get_path_piece(1);
        int inValid = 0;
        std::string respUrl;
        httpserver::string_response* response;

        std::cout << YELLOW << "value : " << BLUE << value << std::endl;
        int id = 0;
        try {
            id = std::stoi(value);
        }
        catch (...) {
            response = new httpserver::string_response("Invalid key : " + value,400); 
            std::cout << RED << "Invalid Key : " << BLUE << value << std::endl;     
            inValid = 1;     
        }

        if (inValid == 0) {
           std::cout << YELLOW << "value : " << GREEN << value << std::endl;
           mtx.lock();
           auto search = redirectUrls.find(id);
           if (search == redirectUrls.end()) {
                inValid = 2;           
           }  
           else
           {
                respUrl = redirectUrls[id];                     /* url found then save to re-direct it */         
           }
           mtx.unlock();         
        }

        if (inValid== 0) {                        /* set the sucess message outside the mutex */
               response = new httpserver::string_response("",302);
               response->with_header("Location",respUrl);
               std::cout << GREEN << "Valid Key redirect : " << BLUE << value << " " << respUrl << std::endl; 
        }
        else if (inValid== 2)                      /* set the not found message outside the mutex */
        {
               response = new httpserver::string_response("",302); 
               response->with_header("Location","/error");
               std::cout << RED << "Invalid Key not found : " << BLUE << value << std::endl; 
        }       
#endif
 
        return std::shared_ptr<httpserver::http_response>(response);
    }
};

class Error_resource: public httpserver::http_resource {
 public:   
    //const http_response render GET(const httpserver::http_request& req ) {
    const std::shared_ptr<httpserver::http_response> render_GET(const httpserver::http_request& req ) {
        std::cout << GREEN << std::endl << "Error Resource:: render" << std::endl;
        httpserver::string_response* response = new httpserver::string_response("Requested resource not found",404);

        std::cout << RED << "error resource render" << std::endl;
        return std::shared_ptr<httpserver::http_response>(response);
    }
};

int main(int argc, char** argv) {

    httpserver::webserver ws = httpserver::create_webserver(8080).
    max_threads(8).
    max_connections(200);

    bool successStatus = false;

    Save_resource sr;
    successStatus = ws.register_resource("/save",&sr);
    if (successStatus==false){
        std::cout << WHITE << "saved url" << std::endl;
        return 1;
    }

    Redirect_resource rdr;
    successStatus = ws.register_resource("/redirect",&rdr, true);
    if (successStatus==false){
        std::cout << WHITE << " redirect " << std::endl;
        return 1;
    }

    Error_resource err;
    successStatus = ws.register_resource("/error",&err);
    if (successStatus==false){
        std::cout << WHITE << " error " << std::endl;
        return 1;
    }

    ws.start(true);
    return(0);
}
//
// =================== To test ======================================
//
// make shell script call it shell_to_do_url.sh
// add this line
// curl -d $1 -X POST http://localhost:8080/save
// then
// chmod +x shell_to_do_url.sh
// ./shell_to_do_url.sh https://aircamuk.pro
// where the argument is you're url you want to redirect to
//
// test from browser 
// 127.0.0.1:8080/redirect
// 127.0.0.1:8080/redirect/<number you assigned>
