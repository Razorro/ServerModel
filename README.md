# ServerModel
*Implement some simple server net message dealing model, as the practise of from knowledge to engineering*

## Model List
- coroutine_server: IO multiplex + nonblock, no other fantastic things, but use coroutine to deal with
buffer, that makes a bit easier and make a more deeper grasp of Python coroutine.
  
### coroutine_server
Simply use select, as an IO multiplex model to make the server has the concurrenct ability, 
use coroutine as the socket's read and write buffer.