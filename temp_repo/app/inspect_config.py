
import sys
try:
    from google import genai
    from google.genai import types
    print("Available fields in GenerateVideosConfig:")
    # print(dir(types.GenerateVideosConfig))
    # It's likely a TypedDict or Pydantic model, let's try to see annotations or fields
    try:
        print(types.GenerateVideosConfig.__annotations__)
    except:
        print(dir(types.GenerateVideosConfig))
except ImportError:
    print("google.genai not found")
