# Generic-REST-Adapter
Simply a REST adapter using HTTPS to quick-start API projects

+ BASIC INFO

  + This is a generic REST adapter that provides the ability to get general logging and HTTPS requests up and 
    running. To craft a specific project using this, simply inherit the adapter and implement authorization / 
    authentication setup and headers configuration. This adapter uses Requests and a Session object to facilitate
    the HTTPS requests. Includes a requirements.txt file (urllib3 and requests are main dependencies). 
    
+ GENERAL USE 
  + There are get, post, put, and delete HTTPS methods given that utilize a generic "do" method that encapsulates
    basic error checking and logging. Default logging level is DEBUG. Modify the paths.py to edit the LOGGING_PATH
    variable. Inheritance is expected, overwriting RestAdapater class variables or ignoring them as needed. Any 
    functions you implement in your custom adapter can use self.log(level="", msg=""). If SSL_Verify is false then
    urllib3 warnings are suppressed.   
    
+ SPECIFIC INSTRUCTIONS
  + Post-Hostname URL addition. Some necessary post-hostname URL modifications may include versions, or endpoint
    prefixes like "REST/" or "endpoints/", etc. This can be taken care of via the customized class you set up. 
    
  + Ex.:
  
  ```
  class AnAdapter(RestAdapter):
      def __init__(self, post_hostname: str, ...):
           super().__init__(...)
           self.url += post_hostname
           self.session.headers.update({"API_KEY": getenv("API_KEY") OR self._api_key, etc.})
  ```

No parameter modification functions are provided.
No complex logging is set up or configured. 
No built-in handler/formatter addition functions. Add this on your own by modifying the logging_config
function. 