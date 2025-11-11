import os
import requests
from fastmcp import FastMCP
mcp = FastMCP("mcp-live-events")


def format_events(response_dict: dict) -> str:
    if not response_dict:
        return "No events found!"

    return "\n\n".join(
        [
            f"""
Name: {event.get("name")}
Link: {event.get("url")}
Event Datetime: {event.get("dates")["start"]["dateTime"]}
Genres: {", ".join(set(c["genre"]["name"] for c in event.get("classifications")))}
Info: {event.get("info")}
Venue: {event.get("_embedded")["venues"][0]["name"]}
"""
            for event in response_dict["_embedded"]["events"]
        ]
    )
    
class EventsApiClient:
    def __init__(self):
        self.base_url = "https://app.ticketmaster.com/discovery/v2"
        self.api_key = os.environ.get("TICKETMASTER_API_KEY")
        if not self.api_key:
            raise ValueError("Ticketmaster API key missing!")

    def fetch_events(
        self,
        start_dttm_str: str,
        end_dttm_str: str,
        classification_name: str = "Music",
        keyword: str | None = None,
    ) -> dict | None:
        try:
            params = {
                "apikey": self.api_key,
                "startDateTime": start_dttm_str,
                "endDateTime": end_dttm_str,
                "classificationName": classification_name,
                "size": 100,
            }
            if keyword:
                params["keyword"] = keyword
            response = requests.get(
                f"{self.base_url}/events.json",
                params=params,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

@mcp.tool()
def get_upcoming_events(start_dttm_str: str, end_dttm_str: str, keyword: str | None = None) -> str:
    """
    Get upcoming music events.
    
    Args:
        start_dttm_str: Start date/time in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ). Example: 2025-02-08T00:00:00Z
        end_dttm_str: Start date/time in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ). Example: 2025-02-10T00:00:00Z
        keyword: Any optional keywords to help filter search results.
    """

    data = EventsApiClient().fetch_events(start_dttm_str=start_dttm_str, end_dttm_str=end_dttm_str, keyword=keyword)

    return format_events(data)




def main():
    mcp.run(transport='stdio')
    
    
    
if __name__ == "__main__":
    main()