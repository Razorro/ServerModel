# ServerModel
*Implement some simple server net message dealing model, as the practise of from knowledge to engineering*

## Model List
- coroutine_server: IO multiplex + nonblock, no other fantastic things, but use coroutine to deal with
buffer, that makes a bit easier and make a more deeper grasp of Python coroutine. Not do anything calculation, just as a echo server.

- threaded_server: based on the coroutine_server, but put the calculation work in work threads, the main thread usually is used to as a IO loop, extracting message from net.
  
### coroutine_server
Simply use select, as an IO multiplex model to make the server has the concurrenct ability, 
use coroutine as the socket's read and write buffer.

### threaded_server
Start several work thread to deal with those message from client, instead dealing in the IO loop, it put the work info work queue, wait for work threads to consume, and then, 
receive the result, send to client, all things clear, Done!

