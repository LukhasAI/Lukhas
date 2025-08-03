"""

#TAG:bridge
#TAG:api
#TAG:neuroplastic
#TAG:colony


Dream Commerce API Example
"""

import asyncio
from dream_commerce import DreamCommerceAPI, DreamRequest

async def main():
    # Initialize API
    api = DreamCommerceAPI()
    await api.initialize()
    
    # Generate a dream
    request = DreamRequest(
        prompt="flying through space",
        style="creative",
        length="medium"
    )
    
    response = await api.generate_dream(request)
    print(f"Generated Dream: {response.content}")
    print(f"Symbols: {response.symbols}")
    print(f"Themes: {response.themes}")

if __name__ == "__main__":
    asyncio.run(main())
