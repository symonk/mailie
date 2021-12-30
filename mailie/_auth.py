

class Auth:
  """
  Base class for authentication schemes.
  """
  
  def auth():
    ...
    
  def synchronous_auth():
    ...
    
  async def asynchronous_auth():
    ...
