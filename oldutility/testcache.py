from sentencecache import SentenceCache
import time
# Instantiate a SentenceCache object with a maximum word count
cache = SentenceCache()

def calculate_response_time(start_time):
     """Calculates the time taken between the request and the response in seconds."""
     end_time = time.time()
     return end_time - start_time
 

def checkdatabase():
    """Loads from file, returns the data directly, and calculates the word count without affecting short-term memory.""" 
    cache_instance = SentenceCache()  
    loaded_cache = cache_instance._load_from_file()
    return 'Database:', loaded_cache



start_time = time.time()  # Capture request start time
print(checkdatabase())
response_time = calculate_response_time(start_time)
print(f"Response time: {response_time:.2f} seconds")


print (f"Cache: {cache.get_cache()}")